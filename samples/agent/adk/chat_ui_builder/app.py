from __future__ import annotations

import json
import logging
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, model_validator

from service import ChatUIService
from settings import settings
from streaming.runtime import StreamingRuntime

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
  message: str | None = None
  source_data: dict | list | str | int | float | bool | None = None
  user_query: str | None = None

  @model_validator(mode='after')
  def ensure_non_empty_request(self) -> 'ChatRequest':
    if self.source_data is None and not self.message:
      raise ValueError('`source_data` 或 `message` 至少提供一个。')
    return self


app = FastAPI(title='A2UI Chat UI Builder')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

service = ChatUIService()
streaming_runtime = StreamingRuntime()


@app.on_event('startup')
async def startup_event() -> None:
  logger.info(
      'Chat UI Builder startup. host=%s port=%s endpoint=%s model=%s log_level=%s',
      settings.host,
      settings.port,
      settings.openai_api_base,
      settings.litellm_model,
      settings.log_level,
  )


@app.get('/health')
async def health() -> dict[str, str]:
  return {'status': 'ok'}


@app.websocket('/ws/debug')
async def ws_debug(websocket: WebSocket) -> None:
  await websocket.accept()
  logger.info('WS /ws/debug connected')
  await websocket.send_text('connected')
  try:
    while True:
      message = await websocket.receive_text()
      logger.info('WS /ws/debug message=%s', message[: settings.max_log_chars])
  except WebSocketDisconnect:
    logger.info('WS /ws/debug disconnected')
  except Exception:
    logger.exception('WS /ws/debug error')


@app.websocket('/api/chat/ws/stream')
async def chat_stream_ws(websocket: WebSocket) -> None:
  """streaming ws 薄接口层。

  说明：
  - session 串行调度由 `streaming/runtime.py` 负责。
  - 断裂累计 JSON 提取由 `streaming/json_extractor.py` 负责。
  - 这里仅做：收消息 -> 调 runtime -> 发 frames。
  """

  await websocket.accept()
  # 后端必须有 session_id（runtime 需要按 session 维护状态），
  # 但不强制前端必须传：若 query 未提供，则在“本次连接建立时”生成并固定复用。
  session_id = websocket.query_params.get('session_id') or f'ws_{uuid4().hex}'
  await websocket.send_json({'type': 'streaming_connected', 'session_id': session_id})

  try:
    while True:
      raw_payload = await websocket.receive_text()
      try:
        payload = json.loads(raw_payload)
      except json.JSONDecodeError:
        await websocket.send_json({'type': 'error', 'error': 'invalid json'})
        continue

      if payload.get('type') != 'sendMessage':
        await websocket.send_json({'type': 'error', 'error': 'unsupported message type'})
        continue

      if 'message' not in payload or 'final' not in payload:
        await websocket.send_json({'type': 'error', 'error': 'missing required fields'})
        continue

      message = payload.get('message')
      is_final = payload.get('final')
      if not isinstance(is_final, bool):
        await websocket.send_json({'type': 'error', 'error': 'final must be boolean'})
        continue

      if not isinstance(message, str):
        await websocket.send_json({'type': 'error', 'error': 'missing required fields'})
        continue

      runtime_result = await streaming_runtime.submit_snapshot(
          session_id=session_id,
          raw_text=message,
          is_stream_end=is_final,
      )
      processed = bool(runtime_result.get('processed'))

      if not processed:
        await websocket.send_json(
            {
                'type': 'streaming_status',
                'session_id': session_id,
                'processed': False,
                'final': is_final,
            }
        )
        continue

      projection_result = runtime_result.get('result') or {}
      frames = projection_result.get('frames') or []
      serializable_frames = [
          frame.model_dump(exclude_none=True) if hasattr(frame, 'model_dump') else frame
          for frame in frames
      ]
      await websocket.send_json(
          {
              'type': 'a2ui_frames',
              'session_id': session_id,
              'processed': True,
              'final': is_final,
              'frames': serializable_frames,
          }
      )
  except WebSocketDisconnect:
    logger.info('WS /api/chat/ws/stream disconnected session_id=%s', session_id)
  except Exception:
    logger.exception('WS /api/chat/ws/stream error session_id=%s', session_id)
    await websocket.send_json({'type': 'error', 'error': 'internal server error'})


@app.post('/api/chat/stream')
async def chat_stream(payload: ChatRequest) -> StreamingResponse:
  request_id = uuid4().hex[:8]
  logger.info(
      '[%s] Incoming chat request user_query=%s source_data=%s',
      request_id,
      (payload.user_query or payload.message or '')[: settings.max_log_chars],
      str(payload.source_data)[: settings.max_log_chars],
  )

  async def frame_stream():
    async for frame in service.stream_frames(
        user_message=payload.message,
        source_data=payload.source_data,
        user_query=payload.user_query,
        request_id=request_id,
    ):
      body = frame.model_dump_json(exclude_none=True)
      logger.info('[%s] Streaming frame body=%s', request_id, body[: settings.max_log_chars])
      yield body + '\n'

  return StreamingResponse(frame_stream(), media_type='application/x-ndjson')
