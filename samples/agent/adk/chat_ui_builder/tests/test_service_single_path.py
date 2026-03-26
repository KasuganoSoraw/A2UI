from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

import service as service_module
from service import ChatUIService


class FakeResponse:
  def __init__(self, chunks: list[str]) -> None:
    self._chunks = chunks

  def __aiter__(self):
    self._iter = iter(self._chunks)
    return self

  async def __anext__(self):
    try:
      content = next(self._iter)
    except StopIteration as exc:
      raise StopAsyncIteration from exc
    return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=content))])


async def _collect_frames(service: ChatUIService, message: str) -> list[object]:
  frames: list[object] = []
  async for frame in service.stream_frames(message, request_id='test-request'):
    frames.append(frame)
  return frames


def test_stream_frames_uses_planning_delta_path(monkeypatch) -> None:
  planning_lines = [
      {
          'event': 'init_plan',
          'surface_id': 'main',
          'title': '审批中心',
          'summary': '待办审批概览',
          'page_kind': 'approval_workflow',
          'emphasis': 'action-first',
      },
      {'event': 'add_region', 'id': 'hero_region', 'role': 'hero', 'title': '重点提醒'},
      {
          'event': 'add_region_text',
          'id': 'hero_text',
          'region_id': 'hero_region',
          'text': '共有 3 条待审批事项',
          'usage_hint': 'body',
      },
      {'event': 'finalize_plan'},
  ]
  chunks = ['\n'.join(json.dumps(line, ensure_ascii=False) for line in planning_lines[:2]) + '\n', '\n'.join(json.dumps(line, ensure_ascii=False) for line in planning_lines[2:]) + '\n']

  async def fake_acompletion(**_: object) -> FakeResponse:
    return FakeResponse(chunks)

  monkeypatch.setattr(service_module, 'acompletion', fake_acompletion)

  frames = asyncio.run(_collect_frames(ChatUIService(), '构建审批页面'))

  assert len(frames) > 3
  title_entries = [
      entry
      for frame in frames
      if frame.dataModelUpdate and frame.dataModelUpdate.path == '/title'
      for entry in frame.dataModelUpdate.contents
      if entry.key == 'title'
  ]
  assert any(entry.valueString == '审批中心' for entry in title_entries)
  assert all(
      not (frame.dataModelUpdate and frame.dataModelUpdate.path == '/content/planning_delta_error_text') for frame in frames
  )


def test_stream_frames_emits_error_without_planning_delta(monkeypatch) -> None:
  async def fake_acompletion(**_: object) -> FakeResponse:
    return FakeResponse(['这里不是 planning delta\n'])

  monkeypatch.setattr(service_module, 'acompletion', fake_acompletion)

  frames = asyncio.run(_collect_frames(ChatUIService(), '返回任意文本'))

  title_entries = [
      entry
      for frame in frames
      if frame.dataModelUpdate and frame.dataModelUpdate.path == '/title'
      for entry in frame.dataModelUpdate.contents
      if entry.key == 'title'
  ]
  assert any(entry.valueString == '页面规划失败' for entry in title_entries)

  assert any(
      frame.dataModelUpdate and frame.dataModelUpdate.path == '/content/planning_delta_error_text'
      for frame in frames
  )
