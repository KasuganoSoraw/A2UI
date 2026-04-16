# chat_ui_builder streaming 端到端渐进式收敛重构设计

## 需求详情
对现有 streaming 链路做定向重构，目标是收敛为唯一的端到端渐进式主链：
`app(ws) -> runtime(stream) -> extractor -> service(stream event->frame) -> app逐帧发送`。

## 澄清结果
- 不再保留“整轮返回 frames 数组”的主路径。
- `service.py` 只保留流式主入口 `stream_project_segment(...)`。
- `runtime.py` 改为流式主入口 `stream_submit_snapshot(...)`。
- `app.py` 改为消费 runtime 异步流并逐帧发送 `a2ui_frame`。
- 删除无用日志：单字符 chunk 与 parsed_events_count=0 的刷屏日志。
- 保持 page_state_summary 在第二阶段结束后统一提交。

## WHAT
1. `streaming/service.py`
   - 删除旧 `project_segment(...)` 聚合入口。
   - 删除旧 `_parse_stream_events(...)` 整轮解析逻辑。
   - 保留并强化 `stream_project_segment(...)` 作为唯一主入口。
   - 精简日志：保留有效日志，移除无意义 chunk 噪音。

2. `streaming/runtime.py`
   - 新增并使用 `stream_submit_snapshot(...)` 作为主入口。
   - `_drain_session(...)` 改为异步流，透传 service 的 frame/final item。
   - 在收到 final 后统一提交 state。
   - 删除旧 `submit_snapshot(...)` 整轮返回路径。

3. `app.py`
   - `/api/chat/ws/stream` 改为消费 `stream_submit_snapshot(...)`。
   - 收到 `type=frame` 立即发送 `a2ui_frame`（单帧）。
   - 收到 `type=final` 发送轻量 `streaming_final`。
   - 保持输入协议不变（sendMessage/message/final）。

## WHY
- 消除双轨制，降低维护成本和阅读负担。
- 真正实现逐帧渲染，满足端到端渐进式体验。
- 保留稳妥 state 提交策略，减少状态不一致风险。

## HOW
- service 第二阶段继续 stream=True + 行解析器，按 event 即时编译 frame 并 yield。
- runtime 每轮触发后直接 `async for` 消费 service，并把 frame 继续向上游转发。
- app 逐条消费 runtime item 并发送 WebSocket 消息，不再等待整轮 frames 集合。
