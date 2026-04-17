# chat_ui_builder streaming 单阶段 LLM 收敛重构设计

## 需求详情
将 streaming 链路从“两阶段 LLM（binding + event）”收敛为“单阶段 LLM 直接输出 StreamEvent NDJSON”。

## 澄清结果
- 保留稳定后半段：`StreamEvent -> StreamCompiler -> FrameCompiler -> A2UIFrame`。
- 保留 runtime 的 session 串行调度与 extractor 触发规则。
- 删除两阶段遗留 prompt/解析/决策代码。
- 不修改 StreamEvent schema。

## WHAT
1. prompt 收敛
- 删除 `binding_prompt.py`。
- `stream_event_prompt.py` 升级为单阶段 prompt：输入直接是
  `visible_snapshot/changes/binding_state_summary/page_state_summary`，输出仍为 NDJSON StreamEvent。
- `prompt/__init__.py` 仅导出单阶段 builder。

2. service 收敛
- 删除两阶段遗留结构：BindingDecision/BindingResult 解析与筛选逻辑。
- `stream_project_segment(...)` 改为单阶段一次调用：
  - 组单阶段输入
  - 流式解析 NDJSON event
  - event 即时编译 frame 并 yield
  - 结束后统一更新 binding/page state 并 yield final

3. runtime 适配
- 继续使用原 payload 结构（含 binding/page state）调用 service 单阶段入口。
- 不再依赖显式 binding decisions。

## WHY
- 双阶段代码会增加理解与维护成本。
- 单阶段能直接表达“从工程输入到事件输出”的主链，代码更清晰。
- 保持事件 schema 与编译链不变，降低重构风险。

## HOW
- 工程侧继续维护 `changes`（extractor）。
- service 结束时统一提交：
  - binding_state_summary（由本轮 create_*_block 事件更新）
  - page_state_summary（由本轮 events 统一更新）
