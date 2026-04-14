# chat_ui_builder ArrangementSemantics 概念收敛设计

## 需求详情
在不改变现有模块行为和页面效果的前提下，收敛 `ArrangementSemantics` 的抽象复杂度。

范围仅限：
- `samples/agent/adk/chat_ui_builder/skeleton_compiler.py`
- `samples/agent/adk/chat_ui_builder/region_archetypes.py`

## 澄清结果
1. 保持外部调用链不变：`_arrangement_for -> RegionBuildContext.arrangement -> builder`。
2. 保持 slot 语义与 frame 协议不变。
3. 允许 section id 从“语义枚举拼接”改为稳定命名（facts/actions/...）。

## WHAT
- `ArrangementSemantics` 收敛为：
  - `body_layout: 'column' | 'row' | 'none'`
  - `facts_layout: 'row' | 'column'`
  - `actions_layout: 'row' | 'column'`
- 移除旧语义枚举与翻译 helper（stacked/compact_group/fact_grid/action_stack 等）。
- `_base_region()` 直接基于新字段判断是否创建 body 及 body layout。
- 各 archetype 使用稳定 section id：`*_facts`、`*_actions`、`*_flow`、`*_inputs`、`*_list_items`。
- `_arrangement_for()` 改为直白映射并删去无效术语修正。

## WHY
- 减少“命名大于实际行为”的认知负担。
- 降低跨文件语义翻译成本，提升可维护性与可调试性。

## HOW
1. 先在 `region_archetypes.py` 替换语义模型与 builder 实现。
2. 再在 `skeleton_compiler.py` 同步 `_arrangement_for()` 映射。
3. 执行最小语法检查确认重构未破坏调用链。
