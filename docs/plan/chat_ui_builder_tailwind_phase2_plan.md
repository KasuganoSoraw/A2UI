# 开发计划：chat_ui_builder Tailwind 第二阶段（内容渲染层）

## Stage 1：样式系统骨架

### Task 1.1 变体常量抽离
- 新增 `src/lib/viewStyles.ts`（或同类文件）。
- 定义 panel/surface/section/button/input/list/status 等可复用变体。

### Task 1.2 App 对齐变体
- `App.tsx` 使用变体常量 + `cn()`，减少零散 class。

## Stage 2：A2UI 内容区 Tailwind 化

### Task 2.1 语义样式层
- 在 `src/index.css` 中通过 `@layer components` 定义内容区样式系统。
- 覆盖 region/header/body/facts/actions/form/workflow 等常见结构。

### Task 2.2 FlowDiagram Tailwind 化
- 将 `FlowDiagram.tsx` 大部分视觉类迁移到 Tailwind。
- 保留必要的尺寸定位样式。

## Stage 3：验证与收尾

### Task 3.1 构建验证
- 运行 `npm run build`（若受环境依赖限制，记录失败原因）。

### Task 3.2 进度与提交
- 追加 `progress.md`（只追加）。
- 每个 stage 完成后提交中文 commit。
