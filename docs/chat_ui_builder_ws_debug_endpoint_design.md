# chat_ui_builder WebSocket 调试接口最小改动设计

## 需求详情
- 仅在后端 `samples/agent/adk/chat_ui_builder/app.py` 增加 `/ws/debug` WebSocket 接口。
- 用于前端联调通路验证：接收前端消息并写日志。
- 不接入 A2UI 业务流，不改现有 HTTP 路由、请求模型和 service 流程。

## 澄清结果
- 接口行为保持最简：连接、收消息、记录日志、断开日志、异常日志。
- 仅支持 `receive_text()` 文本接收场景，兼容前端发送普通文本或 JSON 字符串。
- 为便于前端确认链路，连接后发送一条极简确认消息 `connected`。
- 不新增文件，不修改前端代码，不做无关重构。

## WHAT
- 在 `app.py` 增加 `WebSocket` 与 `WebSocketDisconnect` import。
- 新增 `@app.websocket('/ws/debug')` 处理函数。

## WHY
- 前端联调阶段需要一个稳定、低复杂度的 WS 通路探针。
- 最小改动可降低对现有聊天流式逻辑的风险。

## HOW
1. 增加 WebSocket 相关 import。
2. 新增 `/ws/debug`：`accept` 后记录连接日志并发送 `connected`。
3. `while True` 循环 `receive_text()`，每条消息写 `logger.info`。
4. 捕获 `WebSocketDisconnect` 写断开日志。
5. 捕获通用异常写异常日志，不添加复杂恢复逻辑。
