# chat_ui_builder streaming ws session_id 定向修复计划

## Stage 1：定向改造
### Task 1.1 修改 app.py session_id 逻辑
- query 参数有 `session_id` 则沿用。
- query 参数无 `session_id` 则建连时生成。
- 保证同一 WebSocket 连接内 session_id 固定复用。
- （可选）发送 `streaming_connected` ack。

### Task 1.2 保持主链不变
- 不改消息校验规则。
- 不改 `submit_snapshot(...)` 调用链。
- 不改 `streaming_status` / `a2ui_frames` 协议主体。

## Stage 2：校验与记录
### Task 2.1 最小语法检查
- 运行 `python -m py_compile chat_ui_builder/app.py`。

### Task 2.2 进度与提交
- 追加写入 `progress.md`。
- 中文 commit。
- 创建 PR 记录。
