# Chat UI Builder Repository Extraction Plan

## Goal

Reduce the upstream A2UI repository to the standalone Chat UI Builder Python
backend while preserving reproducible installation and runtime behavior.

## Keep

- `chat_ui_builder/` backend source and tests
- `chat_ui_builder/uv.lock`
- root `README.md`
- root `.gitignore`
- root `LICENSE`
- Git metadata

## Remove

- renderer and frontend code
- samples and agent SDKs
- A2UI specification sources
- repository tooling
- upstream documentation and site configuration
- upstream GitHub and Gemini configuration
- generated runtime logs

## Verification

1. Install locked dependencies with `uv sync --project chat_ui_builder`.
2. Run the backend tests and record any pre-existing failures.
3. Start the FastAPI service without persisting an API key.
4. Verify `GET /health`.
5. Confirm no backend import or file reference points outside
   `chat_ui_builder/`.
