# chat_ui_builder 前端 LineChart 展示质量改造计划（Recharts）

## Stage 1：设计与任务拆分
### Task 1.1
- 编写设计文档，明确 WHAT/WHY/HOW 与边界。
### Task 1.2
- 制定实现计划，定义阶段交付物与验证方式。

## Stage 2：代码实现与验证
### Task 2.1
- 引入 `recharts` 依赖。
### Task 2.2
- 重写 `LineChart.tsx` 渲染层为 Recharts，保留 `spec.path` 解析链路。
### Task 2.3
- 调整 `App.css` 中 line chart 样式，删除手写 SVG 强耦合样式。
### Task 2.4
- 运行构建检查并记录结果。

## Stage 3：收尾与进度更新
### Task 3.1
- 追加写入 `progress.md`（仅追加，不修改历史记录）。
### Task 3.2
- 提交 Git（中文 commit 信息，简要概述改动）。
