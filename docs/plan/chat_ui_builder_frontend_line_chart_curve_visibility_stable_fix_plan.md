# chat_ui_builder LineChart 折线可见性稳定修复计划

## Stage 1：设计与计划
### Task 1.1
- 完成本次“移除 CSS 颜色接管”的设计文档。
### Task 1.2
- 制定最小改动开发计划。

## Stage 2：代码修复
### Task 2.1
- 修改 `App.css`：去掉 `.recharts-line-curve` 的 `stroke: var(...) !important`。
### Task 2.2
- 修改 `LineChart.tsx`：移除 CSS 变量传色，使用 Recharts props 显式控制线和点样式。
### Task 2.3
- 保持空态逻辑、协议链路、recharts 组件结构不变。

## Stage 3：验证与收尾
### Task 3.1
- 执行构建检查并记录结果。
### Task 3.2
- 追加更新 `progress.md`。
### Task 3.3
- 分阶段中文提交。
