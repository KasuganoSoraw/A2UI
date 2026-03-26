# 开发计划：chat_ui_builder Tailwind 接入与迁移

## Stage 1：基础接入（Tailwind 能力落地）

### Task 1.1 依赖安装
- 安装 `tailwindcss`、`@tailwindcss/vite`。
- 保留并继续使用 `tailwind-merge`。

### Task 1.2 Vite 配置
- 在 `vite.config.ts` 注册 `@tailwindcss/vite` 插件。

### Task 1.3 全局样式入口
- 新建 `src/index.css`，添加 `@import "tailwindcss";`。
- 将必要的全局基础样式迁移到该入口。

### Task 1.4 入口接线
- 修改 `src/main.tsx`，引入 `src/index.css`。
- 停止引入 `App.css`。

## Stage 2：UI 迁移（核心区域）

### Task 2.1 App 结构迁移
- `App.tsx` 中页面外壳、左右分区、主要面板改用 Tailwind classes。
- 按钮、输入、状态标签、日志区域迁移到 Tailwind。

### Task 2.2 统一 class 合并
- 所有条件 class 拼接统一走 `cn()`。
- 将原有语义类映射替换为 Tailwind 变体字符串。

### Task 2.3 保留少量必要 CSS
- 仅保留 A2UI 渲染区选择器与 FlowDiagram 样式（暂不完全 utility 化）。
- 删除 `App.css`，避免双轨样式。

## Stage 3：验证与收尾

### Task 3.1 构建与检查
- 运行 `npm install`（或保持 lock 一致）。
- 运行 `npm run build`，确认 TS+Vite 构建通过。

### Task 3.2 输出与提交
- 更新 `progress.md` 追加记录（仅追加）。
- 按阶段完成后提交（中文 commit message）。
- 生成 PR 说明。
