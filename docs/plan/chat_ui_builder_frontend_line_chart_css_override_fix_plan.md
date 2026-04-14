# chat_ui_builder LineChart CSS 覆盖修复计划

## Stage 1：设计与定位
### Task 1.1
- 编写设计文档，明确覆盖源、修复边界与方案。
### Task 1.2
- 制定开发计划，按最小改动执行。

## Stage 2：代码修复
### Task 2.1
- 在 `LineChart.tsx` 为每条折线增加稳定颜色变量透传。
### Task 2.2
- 在 `App.css` 的 `.a2ui-line-chart` 作用域补充 Recharts 保护样式（line/grid/axis/dot）。
### Task 2.3
- 保持图表功能、数据逻辑与后端协议不变。

## Stage 3：验证与收尾
### Task 3.1
- 执行构建检查并记录结果。
### Task 3.2
- 追加更新 `progress.md`。
### Task 3.3
- 按阶段提交（中文 commit 信息）。
