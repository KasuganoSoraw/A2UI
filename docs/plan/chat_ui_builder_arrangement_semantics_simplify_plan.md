# chat_ui_builder ArrangementSemantics 收敛计划

## Stage 1：设计确认
### Task 1.1
- 固化重构边界：仅改 skeleton_compiler 与 region_archetypes。

## Stage 2：region_archetypes 收敛
### Task 2.1
- 重写 `ArrangementSemantics` 为布局直白字段。
### Task 2.2
- 重构 `_base_region()` 与 archetype builder section id 命名。
### Task 2.3
- 删除旧语义 helper/类型。

## Stage 3：skeleton_compiler 对齐
### Task 3.1
- 重写 `_arrangement_for()` 为新字段映射。
### Task 3.2
- 清理旧术语逻辑分支。

## Stage 4：验证与收尾
### Task 4.1
- 运行最小语法检查。
### Task 4.2
- 追加 progress 并提交。
