# chat_ui_builder table cell visual_weight 升级开发计划

## Stage 1：设计与约束固化
### Task 1.1
- 撰写设计文档，明确 WHAT/WHY/HOW 与边界（不改事件名、不改 frame 结构）。
### Task 1.2
- 确认需要改动的文件与测试范围（后端 schema + 编译透传 + 前端渲染）。

## Stage 2：后端实现与验证
### Task 2.1
- 在 `models.py` 增加 `TableCellSpec` 与 table rows 的 richer cell 支持。
### Task 2.2
- 更新 `prompting.py` 中 table contract 与规则文案。
### Task 2.3
- 保持 `skeleton_compiler.py` 路径不变，补充透传断言测试。
### Task 2.4
- 运行后端测试（至少覆盖 table schema 与 compiler 相关用例）。

## Stage 3：前端实现与验证
### Task 3.1
- 更新 `Table.tsx`：支持 primitive/object cell + `renderCell`。
### Task 3.2
- 更新 `App.css`：增加 `.a2ui-table-cell-weight-1..5` 样式。
### Task 3.3
- 新增前端测试覆盖 primitive/object/class 映射。
### Task 3.4
- 执行前端测试或给出环境限制说明。

## 决策记录
- 当前无阻塞决策项；若实现中出现 union 兼容歧义，将暂停并记录后再继续。
