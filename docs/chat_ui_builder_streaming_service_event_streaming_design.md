# chat_ui_builder streaming service 第二阶段流式化设计

## 需求详情
在现有 `samples/agent/adk/chat_ui_builder/streaming/service.py` 原地演进：
- 第一阶段保持一次性 binding 判别。
- 第二阶段改为 stream=True，按 NDJSON event 流式解析。
- 实现边收 chunk、边解析 event、边编译 frame、边向上游产出。
- 补齐两阶段完整日志。

## 澄清结果
- 不新增新的主 service 文件，避免职责分散。
- 保留现有 `project_segment(...)` 兼容入口。
- 新增 `stream_project_segment(...)` 作为 ws 渐进渲染入口。
- page_state_summary 继续采用稳妥策略：本轮第二阶段结束后统一更新。
- 不重写 runtime/json_extractor/app 非必要逻辑。

## WHAT
1. 新增 `StreamEventLineParser`：
   - 支持 chunk 拼接、按换行切分、解析 NDJSON、finish 处理尾行。
2. 新增 `stream_project_segment(...) -> AsyncIterator[dict]`：
   - 先跑第一阶段（一次性）；
   - 再跑第二阶段（stream=True）；
   - 每解析出 event 即调用 `StreamCompiler.apply(event)`；
   - 每得到 frame 即 `yield {"type":"frame","frame":...}`；
   - 阶段结束后 `yield {"type":"final", ...}`。
3. `project_segment(...)` 兼容保留：
   - 内部消费 `stream_project_segment(...)` 聚合出原返回结构。
4. 日志补齐：
   - 第一阶段输入、原始输出、解析结果、accepted 与 rejected 原因。
   - 第二阶段输入、chunk、每次解析事件数、event->frame 结果、最终汇总。

## WHY
- 在原文件演进可保持服务职责集中，减少迁移成本与调用方断裂风险。
- 第二阶段改流式可更贴近非流式 service 的渐进工作模式，支持帧级实时产出。
- 保留 `project_segment` 可兼容现有 runtime 调用链，降低改动面。

## HOW
- 第一阶段继续调用现有一次性 `llm_caller`。
- 第二阶段新增默认 `_stream_event_chunks(...)`：使用 `acompletion(..., stream=True)`。
- chunk 文本通过 `StreamEventLineParser` 解析为 `StreamEvent`。
- 对每个 event 立即编译并产出 frame。
- 累积 events 后统一 `_apply_events_to_page_state(...)` 并产出 final 收尾项。
