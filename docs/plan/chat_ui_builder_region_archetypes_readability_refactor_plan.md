# chat_ui_builder region_archetypes 可读性重构计划

## Stage 1：设计确认
### Task 1.1
- 固化边界：主改 `region_archetypes.py`，保持外部接口。

## Stage 2：结构重写
### Task 2.1
- 弱化 `_base_region()`，拆分为薄 helper。
### Task 2.2
- 删除 `SlotSpec` 路径，改为 builder 显式创建 section。
### Task 2.3
- 每个 role 显式构造 `slot_parents`。

## Stage 3：验证与收尾
### Task 3.1
- 运行最小语法检查。
### Task 3.2
- 追加 progress 并提交。
