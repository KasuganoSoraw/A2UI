# chat_ui_builder 前端 Tailwind 接入与样式迁移设计

## 需求详情与澄清

### 需求
在 `samples/client/react/chat_ui_builder` 中：
1. 真正接入 Tailwind CSS（Vite 官方方式）。
2. 落实 `tailwind-merge` 的统一 className 合并工具。
3. 将 `App.css` 主要样式迁移到 Tailwind utility，保留少量必要 CSS。
4. 提升页面视觉一致性，但不改后端协议与流式渲染链路。

### 当前现状（代码确认）
- `main.tsx` 当前仅引入 `@a2ui/react/styles` 与 `./App.css`。尚未导入 Tailwind 入口。 
- `package.json` 已有 `tailwind-merge`，但尚无 `tailwindcss` 与 `@tailwindcss/vite`。 
- `vite.config.ts` 仅有 React 插件，未注册 Tailwind Vite 插件。 
- `App.tsx` 主要依赖 `App.css` 的语义类名（`panel`、`btn` 等）。

结论：只有 `tailwind-merge` 并不能提供 Tailwind 样式能力；它只负责冲突 class 合并。要真正用 Tailwind，必须安装 Tailwind 及 Vite 插件，并在 CSS 入口 `@import "tailwindcss"`。

## WHAT（做什么）
1. 安装依赖：`tailwindcss`、`@tailwindcss/vite`。
2. 配置 `vite.config.ts`：注册 Tailwind 插件。
3. 新建 `src/index.css`：包含 `@import "tailwindcss";`，并迁移/保留少量全局与 A2UI 渲染定制样式。
4. 修改 `src/main.tsx`：引入 `./index.css`，移除 `./App.css`。
5. 重构 `src/App.tsx`：
   - 统一通过 `cn()` 组合 Tailwind class。
   - 将布局、容器、按钮、输入、日志、预览面板等核心样式迁移到 Tailwind。
6. 处理 `FlowDiagram` 的样式：保留在 CSS（组件内部类名较多、绝对定位与连线绘制样式不适合一次性全迁），但保留迁移接口。
7. 删除旧 `App.css`，避免双样式系统并存。

## WHY（为什么）
- 样式职责应由前端承接；后端负责结构语义。
- Tailwind utility + `cn(twMerge)` 能减少散乱 CSS 与 class 冲突，提升可维护性。
- 渐进式渲染链路不依赖 CSS 文件名和实现方式，因此可安全迁移视觉层。

## HOW（怎么做）

### 实施策略
- 采用“核心区域先迁移 + 高复杂局部保留”策略：
  - 先迁移 App 布局、控件、面板、状态、日志等高频 UI。
  - A2UI 渲染区定制选择器与 FlowDiagram 暂放 CSS，避免一次性大改造成回归风险。

### 风险控制
- 不改 `A2UIProvider / A2UIRenderer / useA2UIActions` 逻辑。
- 不改 fetch stream 与 NDJSON 解析逻辑。
- 不改任何后端接口字段和 planning delta 协议。

### 验收要点
- Tailwind 在构建链路中已生效（Vite 插件 + CSS 入口）。
- `App.tsx` 主要 class 基于 Tailwind，并通过 `cn()` 合并。
- `App.css` 职责显著下降并移除重复样式系统。
- 页面功能与流式渲染保持可用。
