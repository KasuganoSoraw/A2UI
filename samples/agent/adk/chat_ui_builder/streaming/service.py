from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator, Callable
from typing import Any, Literal

from litellm import acompletion
from pydantic import BaseModel, Field

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


class StreamEventLineParser:
  """第二阶段 NDJSON 行解析器。

  说明：
  - 第二阶段改为 stream=True 后，模型文本会按 chunk 到达。
  - 这里用 buffer 拼接并按换行切分，确保支持“半行跨 chunk”。
  """

  def __init__(self) -> None:
    self._buffer = ''

  def feed(self, chunk_text: str) -> list[StreamEvent]:
    if not chunk_text:
      return []

    self._buffer += chunk_text
    events: list[StreamEvent] = []
    while '\n' in self._buffer:
      raw_line, self._buffer = self._buffer.split('\n', 1)
      parsed = self._parse_line(raw_line)
      if parsed is not None:
        events.append(parsed)
    return events

  def finish(self) -> list[StreamEvent]:
    if not self._buffer.strip():
      self._buffer = ''
      return []
    raw_line = self._buffer
    self._buffer = ''
    parsed = self._parse_line(raw_line)
    return [parsed] if parsed is not None else []

  def _parse_line(self, raw_line: str) -> StreamEvent | None:
    line = raw_line.strip()
    if not line:
      return None

    try:
      payload = json.loads(line)
    except json.JSONDecodeError as exc:
      logger.warning('event stage skip invalid NDJSON line: %s line=%s', exc, line)
      return None

    try:
      return STREAM_EVENT_ADAPTER.validate_python(payload)
    except Exception as exc:  # noqa: BLE001
      logger.warning('event stage skip invalid stream event: %s payload=%s', exc, payload)
      return None


class StreamingPromptService:
  """两阶段 streaming prompt 串联服务（最小实现）。"""

  def __init__(
      self,
      llm_caller: LLMCaller | None = None,
      stream_compiler: StreamCompiler | None = None,
  ) -> None:
    self._llm_caller = llm_caller or self._default_llm_caller
    self._stream_compiler = stream_compiler or StreamCompiler()

  async def stream_project_segment(
      self,
      payload: StreamingProjectionInput | dict[str, Any],
  ) -> AsyncIterator[dict[str, Any]]:
    """流式两阶段入口：第一阶段一次性，第二阶段边收边编译边产出。

    设计说明：
    - 第一阶段保持一次性调用，便于稳定拿到 binding decisions。
    - 第二阶段改为 stream=True，模仿非流式 service 的 chunk->parser->compiler 模式。
    - page_state_summary 暂按稳妥策略，在第二阶段结束后统一按 events 回写。
    """

    projection_input = payload if isinstance(payload, StreamingProjectionInput) else StreamingProjectionInput.model_validate(payload)

    binding_payload = {
        'segment_id': projection_input.segment_id,
        'visible_snapshot': projection_input.visible_snapshot,
        'changes': projection_input.changes.model_dump(),
        'binding_state_summary': projection_input.binding_state_summary.model_dump(),
        'page_state_summary': projection_input.page_state_summary.model_dump(),
    }
    logger.info('binding stage input payload=%s', json.dumps(binding_payload, ensure_ascii=False))

    binding_messages = build_binding_messages(binding_payload)
    binding_raw = await self._llm_caller(binding_messages)
    logger.info('binding stage raw output=%s', binding_raw)

    binding_result = self._parse_binding_result(binding_raw, projection_input.segment_id)
    logger.info('binding stage parsed result=%s', binding_result.model_dump())

    accepted_decisions = self._filter_and_apply_decisions(
        decisions=binding_result.decisions,
        binding_state=projection_input.binding_state_summary,
    )
    logger.info(
        'binding stage accepted_decisions=%s',
        [decision.model_dump(exclude_none=True) for decision in accepted_decisions],
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
    logger.info('event stage input payload=%s', json.dumps(event_payload, ensure_ascii=False))

    events: list[StreamEvent] = []
    frame_count = 0
    parser = StreamEventLineParser()
    event_messages = build_stream_event_messages(event_payload)

    async for chunk_text in self._stream_event_chunks(event_messages):
      parsed_events = parser.feed(chunk_text)
      for event in parsed_events:
        events.append(event)
        event_frames = self._stream_compiler.apply(event)
        logger.info(
            'event apply result event=%s frame_count=%s',
            event.model_dump(exclude_none=True),
            len(event_frames),
        )
        for frame in event_frames:
          frame_count += 1
          yield {'type': 'frame', 'frame': frame}

    tail_events = parser.finish()
    for event in tail_events:
      events.append(event)
      event_frames = self._stream_compiler.apply(event)
      logger.info(
          'event apply result event=%s frame_count=%s',
          event.model_dump(exclude_none=True),
          len(event_frames),
      )
      for frame in event_frames:
        frame_count += 1
        yield {'type': 'frame', 'frame': frame}

    # page_state_summary 先保持“阶段结束后统一更新”的稳妥策略，减少状态漂移风险。
    self._apply_events_to_page_state(
        events=events,
        page_state=projection_input.page_state_summary,
    )
    logger.info(
        'event stage final summary total_events=%s total_frames=%s page_state_summary=%s',
        len(events),
        frame_count,
        projection_input.page_state_summary.model_dump(),
    )

    yield {
        'type': 'final',
        'segment_id': projection_input.segment_id,
        'accepted_decisions': [decision.model_dump() for decision in accepted_decisions],
        'events': [event.model_dump(exclude_none=True) for event in events],
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

  async def _stream_event_chunks(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
    """第二阶段默认流式调用，只向上游产出文本 chunk。"""

    response = await acompletion(
        model=settings.litellm_model,
        messages=messages,
        api_base=settings.openai_api_base,
        api_key=settings.openai_api_key,
        stream=True,
        temperature=settings.temperature,
        extra_body={
            'chat_template_kwargs': {
                'enable_thinking': False,
            }
        },
    )

    async for chunk in response:
      content = self._extract_chunk_content(chunk)
      if content:
        yield content

  def _extract_chunk_content(self, chunk: Any) -> str:
    choices = getattr(chunk, 'choices', None) or []
    if not choices:
      return ''
    delta = getattr(choices[0], 'delta', None)
    if delta is None:
      return ''

    content = getattr(delta, 'content', '')
    if isinstance(content, str):
      return content
    if isinstance(content, list):
      texts: list[str] = []
      for part in content:
        if isinstance(part, str):
          texts.append(part)
          continue
        if isinstance(part, dict):
          text_value = part.get('text')
          if isinstance(text_value, str):
            texts.append(text_value)
      return ''.join(texts)
    return ''

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
        logger.info('binding decision rejected: invalid block_type decision=%s', decision.model_dump())
        continue
      if not decision.dataset_id or not decision.target_block_id or not decision.evidence_paths:
        logger.info('binding decision rejected: missing required fields decision=%s', decision.model_dump())
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
      else:
        logger.info('binding decision rejected: append target not found decision=%s', decision.model_dump())

    return accepted

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
