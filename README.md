# Chat UI Builder Backend

This repository contains only the Python backend for Chat UI Builder.

The service accepts source data and a user query, asks an OpenAI-compatible
model to produce incremental planning events, and compiles those events into
A2UI NDJSON frames.

## Requirements

- Windows
- Python 3.11 or newer
- `uv`
- An OpenAI-compatible model endpoint

## Run with Alibaba Cloud Model Studio

Open PowerShell:

```powershell
cd chat_ui_builder
uv sync --project .

$env:OPENAI_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:OPENAI_API_KEY = "<your-api-key>"
$env:LOCAL_MODEL_NAME = "glm-5.1"
$env:LITELLM_MODEL = "openai/glm-5.1"

uv run --project . .
```

The service listens on `http://localhost:8010` by default.

## Endpoints

- `GET /health`
- `POST /api/chat/stream`
- `WS /api/chat/ws/stream`
- `WS /ws/debug`

The HTTP streaming endpoint returns `application/x-ndjson`.

## Tests

```powershell
cd chat_ui_builder
uv run --project . --with pytest pytest -q
```
