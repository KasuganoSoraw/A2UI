from __future__ import annotations

import asyncio
from typing import Any

from pydantic import BaseModel, Field

from streaming.json_extractor import JsonExtractionResult, JsonExtractor
from streaming.service import StreamingPromptService


class StreamingSessionState(BaseModel):
  """单个 streaming session 的最小运行态。

  说明：
  - runtime 只保留“最新累计 raw_text”，不保存历史小片段队列。
  - runtime 负责调用时机控制，不负责语义判断与事件生成细节。
  """

  session_id: str
  latest_raw_text: str = ''
  last_visible_snapshot: dict[str, Any] = Field(default_factory=dict)
  binding_state_summary: dict[str, Any] = Field(default_factory=lambda: {'bindings': []})
  page_state_summary: dict[str, Any] = Field(
      default_factory=lambda: {'surface_initialized': False, 'blocks': []}
  )
  is_processing: bool = False
  has_pending_update: bool = False
  is_stream_end: bool = False
  next_segment_index: int = 1
  first_render_done: bool = False


class StreamingRuntime:
  """streaming runtime：session 级串行调度层。

  设计边界：
  1) 维护 session 状态。
  2) 控制同 session 串行处理。
  3) 决定何时 extract。
  4) 决定何时 project_segment。

  不负责 HTTP/WebSocket，不重写 extractor/service，不做语义业务判断。
  """

  def __init__(
      self,
      *,
      json_extractor: JsonExtractor | None = None,
      prompt_service: StreamingPromptService | None = None,
  ) -> None:
    self._json_extractor = json_extractor or JsonExtractor()
    self._prompt_service = prompt_service or StreamingPromptService()
    self._sessions: dict[str, StreamingSessionState] = {}
    self._session_locks: dict[str, asyncio.Lock] = {}

  async def submit_snapshot(
      self,
      *,
      session_id: str,
      raw_text: str,
      is_stream_end: bool,
  ) -> dict[str, Any]:
    """提交一份“累计快照文本”。

    关键策略：
    - 同 session 强串行：若当前正在 processing，本次只更新 latest_raw_text 并返回。
    - 最新覆盖：不做 FIFO 排队，只保留 latest_raw_text。
    """

    state = self._get_or_create_session(session_id)
    lock = self._get_session_lock(session_id)

    async with lock:
      state.latest_raw_text = raw_text
      state.is_stream_end = is_stream_end
      state.has_pending_update = True

      if state.is_processing:
        return {
            'session_id': session_id,
            'processed': False,
            'result': None,
            'state': self._build_state_view(state),
        }

      state.is_processing = True

    last_result: dict[str, Any] | None = None
    try:
      last_result = await self._drain_session(state)
    finally:
      async with lock:
        state.is_processing = False

    return {
        'session_id': session_id,
        'processed': last_result is not None,
        'result': last_result,
        'state': self._build_state_view(state),
    }

  async def _drain_session(self, state: StreamingSessionState) -> dict[str, Any] | None:
    """串行 drain：只要有 pending update 就继续处理。

    为什么需要这样做：
    - 模型调用可能慢，前端会不断提交更长累计文本。
    - drain 每轮都读取“当下最新 raw_text”，确保下一轮看到的是最新快照。
    """

    last_result: dict[str, Any] | None = None
    lock = self._get_session_lock(state.session_id)

    while True:
      async with lock:
        if not state.has_pending_update:
          break

        state.has_pending_update = False
        current_raw_text = state.latest_raw_text
        current_is_stream_end = state.is_stream_end
        previous_snapshot = state.last_visible_snapshot

      extraction = self._json_extractor.extract(
          raw_text=current_raw_text,
          previous_snapshot=previous_snapshot,
          is_stream_end=current_is_stream_end,
      )

      if not self._should_trigger_processing(
          state=state,
          extraction=extraction,
          previous_snapshot=previous_snapshot,
      ):
        continue

      payload = {
          'segment_id': f'seg_{state.next_segment_index:04d}',
          'visible_snapshot': extraction.visible_snapshot,
          'changes': extraction.changes,
          'binding_state_summary': state.binding_state_summary,
          'page_state_summary': state.page_state_summary,
      }

      result = await self._prompt_service.project_segment(payload)

      async with lock:
        state.last_visible_snapshot = extraction.visible_snapshot
        state.binding_state_summary = result.get('binding_state_summary', state.binding_state_summary)
        state.page_state_summary = result.get('page_state_summary', state.page_state_summary)

        has_frames = bool(result.get('frames'))
        has_events = bool(result.get('events'))
        if has_frames or has_events:
          state.first_render_done = True

        state.next_segment_index += 1

      last_result = result

    return last_result

  def _should_trigger_processing(
      self,
      *,
      state: StreamingSessionState,
      extraction: JsonExtractionResult,
      previous_snapshot: dict[str, Any],
  ) -> bool:
    """统一触发入口：先过滤无意义变化，再按首屏/增量规则判断。"""

    if not self._has_meaningful_changes(
        extraction=extraction,
        previous_snapshot=previous_snapshot,
    ):
      return False

    if not state.first_render_done:
      return self._should_trigger_first_render(extraction=extraction)

    return self._should_trigger_incremental_render(extraction=extraction)

  def _should_trigger_first_render(self, *, extraction: JsonExtractionResult) -> bool:
    """首屏触发规则。

    - 任一数组路径新增完整元素数 >= 2 时触发。
    - 或流结束且当前 snapshot 非空时触发收尾。
    """

    if self._has_array_growth(extraction.changes, threshold=2):
      return True

    is_stream_end = bool(extraction.changes.get('is_stream_end'))
    if is_stream_end and bool(extraction.visible_snapshot):
      return True

    return False

  def _should_trigger_incremental_render(self, *, extraction: JsonExtractionResult) -> bool:
    """首屏后增量触发规则。

    - 任一数组路径新增完整元素数 >= 2 时触发。
    - 或流结束且本轮 changes 非空时触发收尾。
    """

    if self._has_array_growth(extraction.changes, threshold=2):
      return True

    is_stream_end = bool(extraction.changes.get('is_stream_end'))
    if is_stream_end and self._changes_has_delta(extraction.changes):
      return True

    return False

  def _has_meaningful_changes(
      self,
      *,
      extraction: JsonExtractionResult,
      previous_snapshot: dict[str, Any],
  ) -> bool:
    """过滤“可见快照未变化 + 无增量 + 未结束”的空轮次。"""

    snapshot_changed = extraction.visible_snapshot != (previous_snapshot or {})
    has_changes_delta = self._changes_has_delta(extraction.changes)
    is_stream_end = bool(extraction.changes.get('is_stream_end'))

    if snapshot_changed:
      return True
    if has_changes_delta:
      return True
    if is_stream_end:
      return True
    return False

  def _changes_has_delta(self, changes: dict[str, Any]) -> bool:
    new_paths = changes.get('new_paths') or []
    new_array_items = changes.get('new_array_items') or {}
    return bool(new_paths or new_array_items)

  def _has_array_growth(self, changes: dict[str, Any], *, threshold: int) -> bool:
    new_array_items = changes.get('new_array_items') or {}
    return any(int(count) >= threshold for count in new_array_items.values())

  def _get_or_create_session(self, session_id: str) -> StreamingSessionState:
    state = self._sessions.get(session_id)
    if state is None:
      state = StreamingSessionState(session_id=session_id)
      self._sessions[session_id] = state
    return state

  def _get_session_lock(self, session_id: str) -> asyncio.Lock:
    lock = self._session_locks.get(session_id)
    if lock is None:
      lock = asyncio.Lock()
      self._session_locks[session_id] = lock
    return lock

  def _build_state_view(self, state: StreamingSessionState) -> dict[str, Any]:
    return {
        'first_render_done': state.first_render_done,
        'is_processing': state.is_processing,
        'has_pending_update': state.has_pending_update,
        'is_stream_end': state.is_stream_end,
        'next_segment_index': state.next_segment_index,
        'last_visible_snapshot': state.last_visible_snapshot,
    }
