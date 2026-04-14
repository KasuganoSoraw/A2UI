# Chat UI Builder 前端 Timeline 组件接入设计

## 需求详情
仅修改前端，为后端已输出的 `Timeline` / `TimelineItem` A2UI 组件提供可渲染组件实现。目标是让时间线容器和时间线条目可以显示，并复用现有子节点内容（Card/Column/Text）。

## 澄清结果
- 本次只做前端改动，不改后端。
- 不新增业务语义，仅补齐组件渲染能力。
- 保持组件轻量：`Timeline` 负责容器布局，`TimelineItem` 负责条目视觉。

## WHAT
1. 新增 `Timeline.tsx` 与 `TimelineItem.tsx` 组件。
2. 在 `App.tsx` 注册 `Timeline` 与 `TimelineItem` 到 `ComponentRegistry`。
3. 在 `App.css` 增加时间线样式。
4. 保持与现有 `FlowDiagram` 注册方式一致。

## WHY
- 后端已能输出 Timeline 相关 frame，前端缺少组件会导致无法展示。
- 轻量组件注册能快速打通显示链路，不引入重型依赖。

## HOW
1. Timeline 组件使用语义化列表容器承载子组件。
2. TimelineItem 组件渲染节点标识、连接线和内容容器。
3. 通过 `children` 承接 A2UI 子树，保证 Card/Text 等现有原子组件继续工作。
4. 更新样式文件，提供基础视觉时间线效果。
