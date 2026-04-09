# chat_ui_builder region_archetypes 可读性优先重构设计

## 需求详情
仅重构 `region_archetypes.py`（以及必要的 `skeleton_compiler.py` 对齐保持接口一致），目标是降低 builder 结构理解成本，不改变外部行为。

## 澄清结果
- 保留 `ArrangementSemantics / RegionBuildContext / RegionBuildResult / RegionArchetypeRegistry` 对外接口。
- 保留 role 与 slot 名称，保持与 `RegionBinding.parent_for()` 兼容。
- 允许减少抽象，接受少量重复代码，以提升“打开即读懂”的效果。

## WHAT
- 弱化 `_base_region()`：仅做根容器、header/body 的薄封装。
- 删除 `SlotSpec`，各 builder 显式创建 section。
- 各 builder 显式构造 `slot_parents`，不再依赖多层覆盖。
- 增加简洁中文注释说明步骤。

## WHY
- 现状 `slot_specs + slot_parents + _base_region` 三层叠加，阅读路径过深。
- 显式结构步骤更易调试，也更容易核对每个 role 的真实 layout。

## HOW
1. 先改 `region_archetypes.py` 为显式步骤构建。
2. 验证 `skeleton_compiler.py` 无需接口调整（仅类型兼容）。
3. 运行最小语法检查。
