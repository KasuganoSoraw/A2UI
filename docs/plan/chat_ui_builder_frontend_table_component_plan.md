# Chat UI Builder 前端 Table 组件接入计划

关联设计：`docs/chat_ui_builder_frontend_table_component_design.md`

## Stage 1：方案确认
### Task 1.1
- 对齐后端 `Table.spec.path` + `valueString(JSON)` 输入形态。

### Task 1.2
- 约定组件结构与空态、异常处理、单元格值归一化策略。

## Stage 2：编码实现
### Task 2.1
- 新增 `src/components/Table.tsx`，实现健壮 spec 提取与解析。

### Task 2.2
- 修改 `App.tsx` 注册 `Table` 组件。

### Task 2.3
- 修改 `App.css` 增加 table 最小样式。

## Stage 3：验证与收尾
### Task 3.1
- 运行前端构建或最小语法检查（记录依赖限制）。

### Task 3.2
- 追加 `progress.md`。

### Task 3.3
- 分阶段中文提交。
