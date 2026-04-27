# chat_ui_builder streaming ws runtime 接入设计文档

## 需求详情
在 `chat_ui_builder/app.py` 新增最小可用 WebSocket 接口：`/api/chat/ws/stream`。

目标：将现有 `StreamingRuntime` 接入 app 作为前后端联调入口。

约束：
- 不重写 `runtime/json_extractor/service`。
- app 仅做“收消息 -> 调 runtime -> 发 frames”。
- 通过 query 参数读取 `session_id`，缺失时报错。

## 澄清结果
- 前端消息 `message` 是“累计后的全量 JSON 文本”，可能断裂，不能在 app 中 `json.loads(message)`。
- app 只解析 WebSocket 外层消息 JSON。
- 回给前端的主体是 A2UI `frames`，不是 runtime 全量调试对象。

## WHAT
新增内容：
1. 在 app 模块级创建共享实例：`streaming_runtime = StreamingRuntime()`。
2. 新增路由 `@app.websocket('/api/chat/ws/stream')`。
3. 处理流程：
   - accept 连接
   - 从 query 参数拿 `session_id`
   - 循环接收文本并 `json.loads(raw_text)`
   - 校验 `type/message/final`
   - 调用 `streaming_runtime.submit_snapshot(...)`
   - 仅向前端返回 `frames` 与最小状态字段
4. 补充错误返回协议（invalid json / unsupported type / missing fields / final type / missing session_id）。

## WHY
- runtime 已实现 session 串行、latest 覆盖和触发时机，app 不应重复实现调度逻辑。
- service 已实现两阶段 prompt 与 frame 产出，app 不应重复实现模型逻辑。
- 对前端联调而言，核心消费对象是 A2UI frames，因此接口应聚焦 frames 输出。

## HOW
### 成功返回
- 未触发处理：
  - `{"type":"streaming_status","session_id":"...","processed":false,"final":<request.final>}`
- 触发处理（有/无 frames）：
  - `{"type":"a2ui_frames","session_id":"...","processed":true,"final":<request.final>,"frames":[...]}`

### 异常返回
- invalid json
- unsupported message type
- missing required fields
- final must be boolean
- missing session_id

### 非目标
- 不改现有非 streaming 接口。
- 不做 session 清理策略。
