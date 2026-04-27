# chat_ui_builder streaming ws session_id 定向修复设计

## 需求详情
定向修改 `chat_ui_builder/app.py` 中 `/api/chat/ws/stream` 的 `session_id` 获取逻辑。

现状问题：当前强依赖 query 参数 `session_id`，缺失则立即报错并断开，导致当前前端无法联调。

## 澄清结果
- 后端 runtime 按 `session_id` 管理状态，因此后端必须有 session_id。
- 前端不一定传 session_id，因此不应强制要求 query 参数。
- 本次采用“一条 WebSocket 连接一个固定 session_id”的策略：
  - query 里有则沿用；
  - query 里没有则在建连时生成；
  - 同连接后续所有消息复用该 session_id。
- 不改 runtime/json_extractor/service，不重写 ws 主流程。

## WHAT
1. 删除“缺少 session_id 直接报错关闭”的行为。
2. 改为：
   - `session_id = websocket.query_params.get('session_id') or f"ws_{uuid4().hex}"`
3. 可选增强（本次实现）：建连后发一条轻量 ack：
   - `{"type":"streaming_connected","session_id":"..."}`
4. 保持消息处理主链不变：校验 -> submit_snapshot -> 返回 streaming_status / a2ui_frames。

## WHY
- runtime 的 session 状态需要稳定键，不可缺失。
- 强制前端传 session_id 会阻断联调，且不是技术必需。
- 连接级固定 session_id 能保证同连接的增量上下文连续、状态可追踪。

## HOW
- 在 websocket accept 后立刻确定连接级 `session_id`。
- 将该 `session_id` 贯穿整个 `while receive_text` 循环中的 runtime 调用与回包。
- 仅调整 session_id 处理，不变更其它协议字段与业务逻辑。
