# 开发计划：chat_ui_builder Tailwind 第四阶段（稳定渲染包装层）

## Stage 1：去除 DOM 推断路径

### Task 1.1 下线语义扫描 hook
- 删除 `useA2UISemanticStyles` 及 App 中相关接线。

### Task 1.2 代码清理
- 移除依赖 `sem-*` 的入口代码，避免继续扩张脆弱方案。

## Stage 2：建立稳定包装层与样式入口

### Task 2.1 新增 SurfaceViewport
- 新建稳定包装组件，作为 A2UI 内容主题与视觉层级主入口。

### Task 2.2 重构 index.css
- 移除对 `.sem-*` 和深层结构的主要依赖。
- 保留低耦合组件类型样式和全局基础样式。

### Task 2.3 FlowDiagram 稳定化
- 确保 FlowDiagram 使用稳定 wrapper class 与容器样式，不依赖外部推断命中。

## Stage 3：验证与进度

### Task 3.1 构建验证
- 运行 `npm run build`（若环境依赖缺失，记录失败原因）。

### Task 3.2 文档与进度
- 追加 `progress.md`。
- 每个 stage 完成后提交中文 commit。
