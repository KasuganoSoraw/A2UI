# chat_ui_builder table richer cell 普通 dict 化修复计划

## Stage 1：设计与范围确认
### Task 1.1
- 输出本次修复设计文档，明确不再使用 `TableCellSpec`。
### Task 1.2
- 锁定改动范围：`models.py`、`prompting.py`、table 相关测试、前端 `Table.tsx` 测试与辅助函数。

## Stage 2：后端修复
### Task 2.1
- 删除 `TableCellSpec`，将 rows 回退为普通 dict + validator 轻校验。
### Task 2.2
- 更新 table prompt 规则文案（不改事件名）。
### Task 2.3
- 更新后端测试：补充缺 value、越界失败与普通 dict 透传断言。
### Task 2.4
- 运行后端测试（若环境缺依赖，记录限制）。

## Stage 3：前端对齐与验证
### Task 3.1
- 在 `Table.tsx` 显式引入 `getCellWeightClass`，确保仅映射 1..5。
### Task 3.2
- 更新前端测试覆盖权重映射规则。
### Task 3.3
- 运行前端测试（若环境缺依赖，记录限制）。

## 决策记录
- 当前无阻塞决策；若发现“是否允许 cell dict 额外字段”存在争议，按“仅允许 value/visual_weight”执行。
