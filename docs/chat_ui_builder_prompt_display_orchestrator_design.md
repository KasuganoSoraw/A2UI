# Chat UI Builder Prompt 展示编排定位重构设计

## 需求详情
- 仅在 `chat_ui_builder/prompting.py` 内重写 `SYSTEM_PROMPT`。
- 将 prompt 主定位从“协议+raw/evidence 保留倾向”调整为“通用展示编排器”。
- 保留现有 planning delta contract、usage_hint、timeline 变体与 FlowDiagram 通用规则能力。

## 澄清结果
- 不改 event schema 与编译器逻辑。
- 不新增场景化模板，不重新引入日志特化 one-shot。
- `source_data` 是展示素材边界，不要求默认原样复刻。
- `user_query` 仅影响展示意图（标题/摘要/优先级），不扩展业务事实边界。

## WHAT
1. 重写 SYSTEM_PROMPT 的职责定义：
   - 明确“展示编排器”而非“分析/求解器”。
2. 收紧 raw/evidence 规则：
   - 仅在“原始结构本身就是用户关注对象”时展示 raw/evidence/details。
   - 默认优先提炼、归并、分组、排序与结构化呈现。
3. 强化“只展示，不编造”：
   - 禁止新增根因、方案、建议动作、排障步骤、结论。
4. 保留并强化交互编排思考维度：
   - 概览/列表(含 timeline)/facts/details/workflow 的分配策略。
   - warning 文本判定、区域拆分与字段前置原则。

## WHY
- A2UI 服务层的核心价值是“降低阅读负担、优化浏览路径”，不是重复上游原文。
- 默认搬运 raw/evidence 会挤占页面主信息，降低可读性与交互效率。
- 通过明确编排原则与边界，可提升输出稳定性并减少 hallucination 风险。

## HOW
1. 在 SYSTEM_PROMPT 中重写“角色定位 + 规划优先级 + 禁止事项”。
2. 更新关键规则中与 raw/evidence 相关条款为“按需展示而非默认展示”。
3. 保留 contract、usage_hint、role×presentation、timeline 与 FlowDiagram 规则/one-shot。
4. 不改动 schema、compiler、models 与 service。
