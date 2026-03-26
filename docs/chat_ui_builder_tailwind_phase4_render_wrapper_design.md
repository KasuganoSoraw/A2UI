# chat_ui_builder 前端 Tailwind 第四阶段设计（稳定包装层取代 DOM 推断）

## 需求详情与澄清

### 需求
- 彻底移除基于 MutationObserver 与 DOM 扫描的语义猜测样式方案。
- 不改 planning delta 协议，不改后端主链路。
- 构建稳定的前端包装层/变体体系，避免依赖后端当前 DOM 形状。

### 当前问题
- `useA2UISemanticStyles` 会扫描 `.a2ui-card/.a2ui-row/.a2ui-column` 并动态打语义 class。
- `index.css` 大量规则依赖 `.sem-*` 与结构组合，稳定性仍受 renderer 结构变化影响。
- 问题根因是“样式附着点不稳定”，不是协议问题、不是 Tailwind 接入问题。

## WHAT
1. 下线 `useA2UISemanticStyles`，停止运行时 DOM 推断。
2. 建立稳定渲染包装组件（SurfaceViewport）作为样式主入口。
3. `index.css` 重构为“低耦合组件类型样式 + 包装层主题规则”，减少结构层级依赖。
4. 强化 Tailwind 变体系统，保持 `cn()`/`tailwind-merge` 统一样式组合。

## WHY
- 包装层是前端可控稳定锚点，不依赖后端 slot/id 变化。
- 组件类型样式（text/button/input/list/flow）比结构推断更稳。
- 可继续支持流式渲染，无需协议变更。

## HOW

### 实施策略
- 新增 `SurfaceViewport` 组件，集中承载主题、层级、边框、滚动、背景与区域节奏。
- App 使用该组件包裹 `A2UIRenderer`。
- `index.css` 只保留必要基础规则与低耦合组件类型规则，不再猜测 header/facts/actions。

### 风险控制
- 不改 fetch stream / processMessages。
- 不改后端返回 frame 结构。
- FlowDiagram 保持稳定 wrapper class，视觉独立可控。

### 验收要点
- 不再存在运行时 DOM 推断 hook。
- `.a2ui-card/.a2ui-row/.a2ui-column` 不再作为语义判断入口。
- FlowDiagram 稳定可见。
