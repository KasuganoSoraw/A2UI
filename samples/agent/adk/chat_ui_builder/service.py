from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator, Iterable
from typing import Any

from litellm import acompletion

from compiler import FrameCompiler
from models import A2UIFrame, AddRegionActionDelta, AddRegionDelta, AddTextDelta, InitSurfaceDelta
from planning_stream import PlanningDeltaRecord, PlanningDeltaStreamParser
from prompting import build_messages
from skeleton_compiler import SkeletonCompiler
from settings import settings

logger = logging.getLogger(__name__)


def _truncate(value: Any) -> str:
  text = _to_log_text(value)
  return text[: settings.max_log_chars]



def _to_log_text(value: Any) -> str:
  return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _format_message(template: str, args: tuple[Any, ...]) -> str:
  try:
    return template % args
  except Exception:
    serialized_args = ', '.join(_to_log_text(arg) for arg in args)
    return f'{template} | args={serialized_args}'


def _log_with_full_message(
    *,
    logger_obj: logging.Logger,
    level: int,
    template: str,
    preview_args: tuple[Any, ...],
    full_args: tuple[Any, ...],
) -> None:
  logger_obj.log(
      level,
      template,
      *preview_args,
      extra={'full_message': _format_message(template, full_args)},
  )


class ChatUIService:
  async def stream_frames(
      self,
      user_message: str | None = None,
      source_data: Any | None = None,
      user_query: str | None = None,
      request_id: str = 'unknown',
  ) -> AsyncIterator[A2UIFrame]:
    messages = build_messages(user_message=user_message, source_data=source_data, user_query=user_query)
    parser = PlanningDeltaStreamParser()
    skeleton_compiler = SkeletonCompiler()
    rejected_lines: list[str] = []
    allow_actions = self._has_explicit_actions(source_data)
    logger.info(
        '[%s] Starting LLM stream. endpoint=%s model=%s temperature=%s',
        request_id,
        settings.openai_api_base,
        settings.litellm_model,
        settings.temperature,
    )
    logger.info('[%s] User query=%s', request_id, _truncate(user_query or user_message or ''))
    logger.info('[%s] Source data=%s', request_id, _truncate(source_data))
    logger.info('[%s] allow_actions=%s', request_id, allow_actions)
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
      for frame in self._compile_planning_records(parsed_records, skeleton_compiler, request_id, allow_actions):
        yield frame

    parsed_records, trailing_rejected = parser.finish()
    rejected_lines.extend(trailing_rejected)
    for frame in self._compile_planning_records(parsed_records, skeleton_compiler, request_id, allow_actions):
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
      allow_actions: bool,
  ) -> list[A2UIFrame]:
    frames: list[A2UIFrame] = []
    for record in records:
      _log_with_full_message(
          logger_obj=logger,
          level=logging.INFO,
          template='[%s] Parsed planning delta=%s',
          preview_args=(request_id, _truncate(record.raw_line)),
          full_args=(request_id, _to_log_text(record.raw_line)),
      )
      if not allow_actions and self._is_action_event(record.delta):
        logger.warning(
            '[%s] Skipping action event because source_data has no explicit actions. event=%s',
            request_id,
            type(record.delta).__name__,
        )
        continue
      compiled = skeleton_compiler.apply(record.delta)
      for frame in compiled:
        _log_with_full_message(
            logger_obj=logger,
            level=logging.INFO,
            template='[%s] Emitting planning A2UI frame=%s',
            preview_args=(request_id, _truncate(frame.model_dump(exclude_none=True))),
            full_args=(request_id, _to_log_text(frame.model_dump(exclude_none=True))),
        )
      frames.extend(compiled)
    return frames

  def _is_action_event(self, delta: object) -> bool:
    if isinstance(delta, AddRegionActionDelta):
      return True
    if isinstance(delta, AddRegionDelta) and delta.role == 'actions':
      return True
    return False

  def _has_explicit_actions(self, source_data: Any) -> bool:
    if source_data is None:
      return False
    if isinstance(source_data, dict):
      normalized_keys = {str(key).lower() for key in source_data.keys()}
      action_markers = {
          'actions',
          'available_actions',
          'recommended_actions',
          'recommendations',
          'next_steps',
          'next_actions',
      }
      if normalized_keys.intersection(action_markers):
        return True
      return any(self._has_explicit_actions(value) for value in source_data.values())
    if isinstance(source_data, list):
      return any(self._has_explicit_actions(item) for item in source_data)
    return False

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
