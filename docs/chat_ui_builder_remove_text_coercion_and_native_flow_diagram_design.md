# chat_ui_builder 移除文本纠偏与原生 flow_diagram 支持设计

## 需求详情
本次专项清理目标：
1. 移除后端文本标题机械纠偏（_coerce_text_for_binding / _is_title_overlap / normalize_text 及相关调用链）。
2. 移除原生 `add_region_flow_diagram` 支持及自动补建 workflow region 逻辑。

约束：
- 保留 Mermaid flow 类型路由：`flowchart/sequenceDiagram/stateDiagram-v2 -> slot='flow'`。
- 不再做自动挪区/兜底纠偏。
- 不改 A2UI frame 结构与其他无关行为。

## 澄清结果
- 需同步更新：`models.py`、`skeleton_compiler.py`、`prompting.py`、相关测试。
- 删除原生 flow schema 后，contract 也应移除该事件，避免模型继续输出。
- finalize 只保留通用 orphan region 补建，不包含 flow 专项逻辑。

## WHAT
- `models.py`：删除 `AddRegionFlowDiagramDelta`、`AddFlowDiagramDelta`，并从 union 中移除。
- `skeleton_compiler.py`：
  - 删除文本纠偏相关函数与 router text_coercer 参数。
  - 删除 flow_region_overrides runtime 字段与 `handle_flow` / `_resolve_flow_region`。
  - 删除 handler registry 中 `AddRegionFlowDiagramDelta` 映射。
  - 保留 Mermaid diagramType -> flow/text slot 路由。
- `prompting.py`：移除 `add_region_flow_diagram` 协议说明与相关规则。
- tests：删除/替换原生 flow 用例，保留 Mermaid flow slot 行为验证。

## WHY
- 降低后端“语义控制”与机械修正，回归 LLM 主导组织。
- 消除重复的 flow 表达路径（原生 flow + Mermaid）以简化协议和维护成本。

## HOW
1. 先改 schema 与 compiler 入口，确保无流图类型依赖。
2. 再改 router/content handler 参数与逻辑，移除 text_coercer 链路。
3. 更新 prompt 合同与规则，避免模型输出已删除事件。
4. 更新测试并执行最小检查。
