from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any, Literal

from litellm import acompletion
from pydantic import BaseModel, Field

from models import A2UIFrame
from settings import settings
from streaming.models import (
    STREAM_EVENT_ADAPTER,
    CreateFactsBlockEvent,
    CreateListBlockEvent,
    CreateTableBlockEvent,
    CreateTextBlockEvent,
    InitStreamSurfaceEvent,
    SetFinalSummaryFactsEvent,
    SetFinalSummaryTextEvent,
    StreamEvent,
)
from streaming.prompt import build_binding_messages, build_stream_event_messages
from streaming.stream_compiler import StreamCompiler

logger = logging.getLogger(__name__)

_ALLOWED_BLOCK_TYPES = {'text', 'facts', 'list', 'table'}


class BindingRecord(BaseModel):
  dataset_id: str
  block_id: str
  block_type: Literal['text', 'facts', 'list', 'table']
  source_path: str


class BindingStateSummary(BaseModel):
  bindings: list[BindingRecord] = Field(default_factory=list)


class PageBlockSummary(BaseModel):
  block_id: str
  block_type: Literal['text', 'facts', 'list', 'table']


class PageStateSummary(BaseModel):
  surface_initialized: bool = False
  blocks: list[PageBlockSummary] = Field(default_factory=list)


class ChangesPayload(BaseModel):
  new_paths: list[str] = Field(default_factory=list)
  new_array_items: dict[str, int] = Field(default_factory=dict)
  is_stream_end: bool = False


class BindingDecision(BaseModel):
  dataset_id: str
  should_create_new_block: bool
  target_block_type: Literal['text', 'facts', 'list', 'table']
  target_block_id: str
  evidence_paths: list[str]


class BindingResult(BaseModel):
  segment_id: str
  decisions: list[BindingDecision] = Field(default_factory=list)


class StreamingProjectionInput(BaseModel):
  segment_id: str
  visible_snapshot: dict[str, Any]
  changes: ChangesPayload = Field(default_factory=ChangesPayload)
  binding_state_summary: BindingStateSummary = Field(default_factory=BindingStateSummary)
  page_state_summary: PageStateSummary = Field(default_factory=PageStateSummary)


LLMCaller = Callable[[list[dict[str, str]]], Any]


class StreamingPromptService:
  """两阶段 streaming prompt 串联服务（最小实现）。"""

  def __init__(
      self,
      llm_caller: LLMCaller | None = None,
      stream_compiler: StreamCompiler | None = None,
  ) -> None:
    self._llm_caller = llm_caller or self._default_llm_caller
    self._stream_compiler = stream_compiler or StreamCompiler()

  async def project_segment(self, payload: StreamingProjectionInput | dict[str, Any]) -> dict[str, Any]:
    """执行一轮两阶段投影，返回 decisions/events/frames 与最新 binding_state_summary。"""

    projection_input = payload if isinstance(payload, StreamingProjectionInput) else StreamingProjectionInput.model_validate(payload)

    binding_payload = {
        'segment_id': projection_input.segment_id,
        'visible_snapshot': projection_input.visible_snapshot,
        'changes': projection_input.changes.model_dump(),
        'binding_state_summary': projection_input.binding_state_summary.model_dump(),
        'page_state_summary': projection_input.page_state_summary.model_dump(),
    }

    binding_messages = build_binding_messages(binding_payload)
    binding_raw = await self._llm_caller(binding_messages)
    binding_result = self._parse_binding_result(binding_raw, projection_input.segment_id)

    accepted_decisions = self._filter_and_apply_decisions(
        decisions=binding_result.decisions,
        binding_state=projection_input.binding_state_summary,
    )

    event_payload = {
        'segment_id': projection_input.segment_id,
        'binding_decisions': {
            'segment_id': projection_input.segment_id,
            'decisions': [decision.model_dump() for decision in accepted_decisions],
        },
        'visible_snapshot': projection_input.visible_snapshot,
        'changes': projection_input.changes.model_dump(),
        'binding_state_summary': projection_input.binding_state_summary.model_dump(),
        'page_state_summary': projection_input.page_state_summary.model_dump(),
    }

    event_messages = build_stream_event_messages(event_payload)
    event_raw = await self._llm_caller(event_messages)
    events = self._parse_stream_events(event_raw)

    frames: list[A2UIFrame] = []
    for event in events:
      frames.extend(self._stream_compiler.apply(event))
    self._apply_events_to_page_state(
        events=events,
        page_state=projection_input.page_state_summary,
    )

    return {
        'segment_id': projection_input.segment_id,
        'accepted_decisions': [decision.model_dump() for decision in accepted_decisions],
        'events': [event.model_dump(exclude_none=True) for event in events],
        'frames': frames,
        'binding_state_summary': projection_input.binding_state_summary.model_dump(),
        'page_state_summary': projection_input.page_state_summary.model_dump(),
    }

  async def _default_llm_caller(self, messages: list[dict[str, str]]) -> str:
    """默认 LLM 调用：复用现有 litellm 配置，返回文本内容。"""

    response = await acompletion(
        model=settings.litellm_model,
        messages=messages,
        api_base=settings.openai_api_base,
        api_key=settings.openai_api_key,
        stream=False,
        temperature=settings.temperature,
        extra_body={
            'chat_template_kwargs': {
                'enable_thinking': False,
            }
        },
    )

    if not getattr(response, 'choices', None):
      return ''

    message = response.choices[0].message if response.choices else None
    content = getattr(message, 'content', '') if message else ''
    return content or ''

  def _parse_binding_result(self, raw_text: str, segment_id: str) -> BindingResult:
    """解析第一阶段 JSON 输出，并做最小兜底。"""

    text = (raw_text or '').strip()
    if not text:
      return BindingResult(segment_id=segment_id, decisions=[])

    try:
      payload = json.loads(text)
    except json.JSONDecodeError as exc:
      logger.warning('binding stage JSON parse failed: %s; raw=%s', exc, text)
      return BindingResult(segment_id=segment_id, decisions=[])

    if not isinstance(payload, dict):
      return BindingResult(segment_id=segment_id, decisions=[])

    payload.setdefault('segment_id', segment_id)
    payload.setdefault('decisions', [])
    try:
      return BindingResult.model_validate(payload)
    except Exception as exc:  # noqa: BLE001
      logger.warning('binding stage validation failed: %s; payload=%s', exc, payload)
      return BindingResult(segment_id=segment_id, decisions=[])

  def _filter_and_apply_decisions(
      self,
      *,
      decisions: list[BindingDecision],
      binding_state: BindingStateSummary,
  ) -> list[BindingDecision]:
    """筛选可接受决策，并按规则更新 binding_state_summary。

    规则：
    - create=true：通过最小校验后新增 binding
    - create=false：不新增 binding，但必须命中既有 dataset_id + block_id
    """

    existing_pairs = {(record.dataset_id, record.block_id) for record in binding_state.bindings}
    accepted: list[BindingDecision] = []

    for decision in decisions:
      if decision.target_block_type not in _ALLOWED_BLOCK_TYPES:
        continue
      if not decision.dataset_id or not decision.target_block_id or not decision.evidence_paths:
        continue

      pair = (decision.dataset_id, decision.target_block_id)

      if decision.should_create_new_block:
        if pair in existing_pairs:
          # 已存在相同绑定，不重复写入。
          accepted.append(decision)
          continue

        binding_state.bindings.append(
            BindingRecord(
                dataset_id=decision.dataset_id,
                block_id=decision.target_block_id,
                block_type=decision.target_block_type,
                source_path=decision.evidence_paths[0],
            )
        )
        existing_pairs.add(pair)
        accepted.append(decision)
        continue

      # append 决策不新增 binding，但必须命中历史绑定。
      if pair in existing_pairs:
        accepted.append(decision)

    return accepted

  def _parse_stream_events(self, raw_text: str) -> list[StreamEvent]:
    """解析第二阶段 NDJSON 输出。"""

    events: list[StreamEvent] = []
    for raw_line in (raw_text or '').splitlines():
      line = raw_line.strip()
      if not line:
        continue
      try:
        payload = json.loads(line)
      except json.JSONDecodeError:
        logger.warning('skip invalid NDJSON line: %s', line)
        continue

      try:
        event = STREAM_EVENT_ADAPTER.validate_python(payload)
      except Exception as exc:  # noqa: BLE001
        logger.warning('skip invalid stream event: %s payload=%s', exc, payload)
        continue
      events.append(event)
    return events

  def _apply_events_to_page_state(
      self,
      *,
      events: list[StreamEvent],
      page_state: PageStateSummary,
  ) -> None:
    """基于本轮已接受事件闭环更新 page_state_summary。

    后端在这里先更新页面状态，保证下一轮请求能直接复用最新上下文，
    避免因为状态滞后导致重复 init_surface 或重复 create block。
    """

    existing_by_block_id = {block.block_id: block for block in page_state.blocks}

    for event in events:
      if isinstance(event, InitStreamSurfaceEvent):
        page_state.surface_initialized = True
        continue

      block_id: str | None = None
      block_type: Literal['text', 'facts', 'list', 'table'] | None = None
      if isinstance(event, CreateTextBlockEvent):
        block_id = event.block_id
        block_type = 'text'
      elif isinstance(event, CreateFactsBlockEvent):
        block_id = event.block_id
        block_type = 'facts'
      elif isinstance(event, CreateListBlockEvent):
        block_id = event.block_id
        block_type = 'list'
      elif isinstance(event, CreateTableBlockEvent):
        block_id = event.block_id
        block_type = 'table'
      elif isinstance(event, SetFinalSummaryTextEvent):
        block_id = event.block_id
        block_type = 'text'
      elif isinstance(event, SetFinalSummaryFactsEvent):
        block_id = event.block_id
        block_type = 'facts'

      if not block_id or not block_type:
        continue
      if block_id in existing_by_block_id:
        continue

      block_summary = PageBlockSummary(block_id=block_id, block_type=block_type)
      page_state.blocks.append(block_summary)
      existing_by_block_id[block_id] = block_summary
