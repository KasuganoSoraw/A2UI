from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator, Iterable
from typing import Any

from litellm import acompletion

from compiler import FrameCompiler
from models import A2UIFrame, AddTextDelta, InitSurfaceDelta
from planning_stream import PlanningDeltaRecord, PlanningDeltaStreamParser
from prompting import build_messages
from skeleton_compiler import SkeletonCompiler
from settings import settings

logger = logging.getLogger(__name__)

STREAM_STATUS_TEXT_ID = 'loading_status_text'


def _truncate(value: Any) -> str:
  text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
  return text[: settings.max_log_chars]


class ChatUIService:
  async def stream_frames(
      self, user_message: str, request_id: str = 'unknown'
  ) -> AsyncIterator[A2UIFrame]:
    messages = build_messages(user_message)
    parser = PlanningDeltaStreamParser()
    skeleton_compiler = SkeletonCompiler()
    rejected_lines: list[str] = []

    for frame in self._loading_frames():
      logger.info('[%s] Emitting loading frame=%s', request_id, _truncate(frame.model_dump(exclude_none=True)))
      yield frame

    logger.info(
        '[%s] Starting LLM stream. endpoint=%s model=%s temperature=%s',
        request_id,
        settings.openai_api_base,
        settings.litellm_model,
        settings.temperature,
    )
    logger.info('[%s] User message=%s', request_id, _truncate(user_message))
    logger.info('[%s] LLM messages=%s', request_id, _truncate(messages))

    response = await acompletion(
        model=settings.litellm_model,
        messages=messages,
        api_base=settings.openai_api_base,
        api_key=settings.openai_api_key,
        stream=True,
        temperature=settings.temperature,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        },
    )

    async for chunk in response:
      delta = chunk.choices[0].delta if chunk.choices else None
      content = getattr(delta, 'content', None)
      if not content:
        continue
      logger.info('[%s] LLM chunk=%s', request_id, _truncate(content))
      parsed_records, rejected = parser.feed(content)
      rejected_lines.extend(rejected)
      for frame in self._compile_planning_records(parsed_records, skeleton_compiler, request_id):
        yield frame

    parsed_records, trailing_rejected = parser.finish()
    rejected_lines.extend(trailing_rejected)
    for frame in self._compile_planning_records(parsed_records, skeleton_compiler, request_id):
      yield frame

    raw_output = parser.raw_output
    logger.info('[%s] Raw LLM output=%s', request_id, _truncate(raw_output))

    if parser.seen_planning_delta:
      for rejected_line in rejected_lines:
        logger.info('[%s] Ignoring non-planning line during delta stream=%s', request_id, _truncate(rejected_line))
      return

    logger.warning(
        '[%s] No valid planning deltas parsed from stream; rejected_lines=%s',
        request_id,
        _truncate(rejected_lines),
    )
    for frame in self._error_frames():
      logger.info('[%s] Emitting error frame=%s', request_id, _truncate(frame.model_dump(exclude_none=True)))
      yield frame

  def _compile_planning_records(
      self,
      records: Iterable[PlanningDeltaRecord],
      skeleton_compiler: SkeletonCompiler,
      request_id: str,
  ) -> list[A2UIFrame]:
    frames: list[A2UIFrame] = []
    for record in records:
      logger.info('[%s] Parsed planning delta=%s', request_id, _truncate(record.raw_line))
      compiled = skeleton_compiler.apply(record.delta)
      for frame in compiled:
        logger.info('[%s] Emitting planning A2UI frame=%s', request_id, _truncate(frame.model_dump(exclude_none=True)))
      frames.extend(compiled)
    return frames

  def _loading_frames(self) -> list[A2UIFrame]:
    compiler = FrameCompiler()
    frames = compiler.apply(
        InitSurfaceDelta(
            event='init_surface',
            surface_id='main',
            title='正在建立规划流',
            summary='后端正在等待模型输出 planning deltas，并将在收到 init_plan 后立即切到业务 UI。',
        )
    )
    frames.extend(
        compiler.apply(
            AddTextDelta(
                event='add_text',
                id=STREAM_STATUS_TEXT_ID,
                parent_id='root',
                text='已启动流式生成，等待首个 init_plan 事件。',
                usage_hint='body',
            )
        )
    )
    return frames

  def _error_frames(self) -> list[A2UIFrame]:
    compiler = FrameCompiler()
    frames = compiler.apply(
        InitSurfaceDelta(
            event='init_surface',
            surface_id='main',
            title='页面规划失败',
            summary='未解析出任何 planning delta，请检查模型输出格式并重试。',
        )
    )
    frames.extend(
        compiler.apply(
            AddTextDelta(
                event='add_text',
                id='planning_delta_error_text',
                parent_id='root',
                text='当前 demo 仅支持 planning delta 主链路（init_plan / add_region* / finalize_plan）。',
                usage_hint='body',
            )
        )
    )
    return frames
