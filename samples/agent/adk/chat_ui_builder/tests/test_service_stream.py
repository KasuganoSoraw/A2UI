from __future__ import annotations

from types import SimpleNamespace

import pytest

from service import ChatUIService


class FakeStreamingResponse:
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
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                delta=SimpleNamespace(content=content),
            )
        ]
    )


@pytest.mark.asyncio
async def test_stream_frames_uses_planning_delta_only(monkeypatch):
  chunks = [
      '{"event":"init_plan","surface_id":"main","title":"测试页面","page_kind":"overview","emphasis":"balanced","layout_hint":"single_column"}\n',
      '{"event":"add_region","id":"hero_section","role":"hero","title":"概览","importance":"high"}\n',
      '{"event":"add_region_text","id":"hero_text","region_id":"hero_section","text":"hello","usage_hint":"body"}\n',
      '{"event":"finalize_plan"}\n',
  ]

  async def fake_acompletion(**_: object):
    return FakeStreamingResponse(chunks)

  monkeypatch.setattr('service.acompletion', fake_acompletion)

  service = ChatUIService()
  frames = [frame async for frame in service.stream_frames('生成测试页面', request_id='t1')]

  assert len(frames) > 0
  assert any(frame.beginRendering is not None for frame in frames)
  assert any(frame.surfaceUpdate is not None for frame in frames)
  assert any(frame.dataModelUpdate is not None for frame in frames)

  serialized = [frame.model_dump(exclude_none=True) for frame in frames]
  serialized_text = str(serialized)
  assert '页面规划失败' not in serialized_text
  assert 'hero_section' in serialized_text
  assert 'hello' in serialized_text


@pytest.mark.asyncio
async def test_stream_frames_emits_error_when_no_planning_delta(monkeypatch):
  chunks = [
      '这不是合法 NDJSON 输出。\n',
      '模型输出了普通文本。\n',
  ]

  async def fake_acompletion(**_: object):
    return FakeStreamingResponse(chunks)

  monkeypatch.setattr('service.acompletion', fake_acompletion)

  service = ChatUIService()
  frames = [frame async for frame in service.stream_frames('随便聊聊', request_id='t2')]

  serialized = [frame.model_dump(exclude_none=True) for frame in frames]
  serialized_text = str(serialized)
  assert '页面规划失败' in serialized_text
  assert 'planning delta' in serialized_text
