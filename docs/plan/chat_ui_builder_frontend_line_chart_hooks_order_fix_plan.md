# chat_ui_builder LineChart Hooks 顺序修复计划

## Stage 1：设计与计划
### Task 1.1
- 编写 Hooks 顺序修复设计文档（范围、边界、方案）。
### Task 1.2
- 编写开发计划，约束最小修改策略。

## Stage 2：编码修复与验证
### Task 2.1
- 前置 `useMemo` 到所有 early return 之前。
### Task 2.2
- 在 memo 回调中处理 `spec` 缺失/结构不完整情况，返回空数组。
### Task 2.3
- 保持空态文案与 Recharts 渲染逻辑不变。
### Task 2.4
- 执行构建检查并记录结果。

## Stage 3：收尾
### Task 3.1
- 追加写入 `progress.md`。
### Task 3.2
- 按阶段提交（中文 commit 信息）。
