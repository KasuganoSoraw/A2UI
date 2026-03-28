from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, model_validator

from service import ChatUIService
from settings import settings

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
    allow_origin_regex=r'http://localhost:\d+',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

service = ChatUIService()


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
