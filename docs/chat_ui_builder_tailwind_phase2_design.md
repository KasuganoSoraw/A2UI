# chat_ui_builder 前端 Tailwind 第二阶段设计（A2UI 内容渲染层）

## 需求详情与澄清

### 需求
在 `samples/client/react/chat_ui_builder` 中，进入 Tailwind 第二阶段：
- 不改后端协议与 planning delta 主链路。
- 不止于 shell 样式迁移。
- 真正优化 A2UI 渲染出来的内容区（region/panel/header/facts/actions/form/workflow）。

### 当前现状
- Tailwind 已接入（`tailwindcss` + `@tailwindcss/vite` + `@import 'tailwindcss'`）。
- `App.tsx` 外层壳子已有 Tailwind 化。
- 但 A2UI 内容区仍主要依赖少量旧式 CSS 选择器；region 视觉变体系统尚未明确。
- `FlowDiagram` 仍主要依赖传统 CSS 类，不利于统一 Tailwind 样式语言。

结论：仅接入 Tailwind 与迁移 App 壳子还不够；需要建立面向 A2UI 内容的前端样式层（变体+语义选择器）。

## WHAT
1. 新建前端样式变体常量（panel/section/button/input/list/surface 等），减少散落 class。
2. 在 `index.css` 中用 Tailwind 的 `@layer components` 针对 A2UI DOM 结构建立“内容区样式系统”：
   - region wrapper
   - header zone
   - facts group
   - actions group
   - form inputs zone
   - workflow zone
3. 优化 `FlowDiagram` 组件，优先改为 Tailwind class（保留极少必要内联样式）。
4. 保持 `cn(tailwind-merge)` 作为统一 class 合并入口。

## WHY
- A2UI 内容区才是最终生成页面的主体，体验提升应集中在这里。
- 后端负责结构语义，前端负责视觉实现；此阶段正是落实职责边界。
- 变体常量 + 语义选择器可让样式更可维护，减少“类名堆砌”。

## HOW

### 实施策略
- 通过“前端包装与样式系统”增强内容层，不新增后端 style 字段。
- 基于已有 component id 命名（如 header/fact/action/input/flow）与 `@a2ui/react` class 结构施加语义样式。

### 风险控制
- 不改 `A2UIProvider/A2UIRenderer/useA2UIActions` 逻辑。
- 不改流式请求与 `processMessages` 逻辑。
- 不改 planning delta 协议。

### 验收要点
- A2UI 内容区视觉层级明显增强。
- facts/actions/form/workflow 呈现更统一。
- `tailwind-merge` 在变体组合中持续被实际使用。
