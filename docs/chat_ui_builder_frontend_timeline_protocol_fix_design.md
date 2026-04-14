# Chat UI Builder 前端 Timeline 协议修复设计

## 需求详情
- 修复 `samples/client/react/chat_ui_builder/src/components/Timeline.tsx` 与 `TimelineItem.tsx`。
- 目标是让组件遵循 `@a2ui/react` 自定义组件协议：接收 `node/surfaceId`，从 `node.properties` 读取子节点，并通过 `ComponentNode` 递归渲染。

## 澄清结果
- 后端 `Timeline -> TimelineItem -> Card -> Column -> Text` 帧结构不改。
- `App.tsx` 中注册逻辑保持不变。
- 当前主要问题是 Timeline 两个组件按普通 React `children` 写法实现，不符合 A2UI 渲染约定，导致渲染为空或不完整。

## WHAT
1. `Timeline` 改为 `A2UIComponentProps` 组件：
   - 使用 `useA2UIComponent(node, surfaceId)`。
   - 从 `node.properties.children` 读取子节点。
   - 用 `ComponentNode` 递归渲染。
   - 保留 `a2ui-timeline` class，并支持 `node.weight -> --weight`。
2. `TimelineItem` 改为 `A2UIComponentProps` 组件：
   - 使用 `useA2UIComponent(node, surfaceId)`。
   - 优先读取 `node.properties.child`，兼容 `children`。
   - 用 `ComponentNode` 渲染 child。
   - 保留 `a2ui-timeline-item` 与内部 dot/line/content 结构，并支持 `node.weight -> --weight`。
   - 预留读取扩展字段（`timestamp/placement/center/color`）以便后续扩展。

## WHY
- `@a2ui/react` 的渲染链路是基于 `ComponentNode` 递归展开组件树，不是将 JSX `children` 直接传给自定义组件。
- 与内置 `Card` / `List` 对齐后，能够保证 Timeline 容器和条目按帧结构正确显示，并复用后续主题与样式机制。

## HOW
1. 参考 `renderers/react/src/components/layout/Card.tsx` 与 `List.tsx` 的数据访问和递归渲染模式。
2. 在 Timeline 两组件中实现统一的 child/children 节点归一化逻辑。
3. 保持 className 与 DOM 结构兼容现有 `App.css`，仅修复协议层实现。
4. 运行前端构建或最小检查验证代码可编译（若环境依赖缺失，记录限制）。
