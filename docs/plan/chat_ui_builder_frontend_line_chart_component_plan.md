# Chat UI Builder 前端 LineChart 组件接入计划

关联设计：`docs/chat_ui_builder_frontend_line_chart_component_design.md`

## Stage 1：方案确认
### Task 1.1
- 对齐后端输出协议：`LineChart.spec.path` + dataModel `valueString(JSON)`。

### Task 1.2
- 明确空态与容错规则（无 spec/无指标/无数据/无有效数值）。

## Stage 2：编码实现
### Task 2.1
- 新增 `src/components/LineChart.tsx`，按 Table 同路径实现 spec 解析与渲染。

### Task 2.2
- 修改 `src/App.tsx` 注册 `LineChart`。

### Task 2.3
- 视需要在 `src/App.css` 添加最小样式。

## Stage 3：验证与收尾
### Task 3.1
- 运行前端构建检查（记录依赖限制）。

### Task 3.2
- 追加 `progress.md`。

### Task 3.3
- 分阶段中文提交。
