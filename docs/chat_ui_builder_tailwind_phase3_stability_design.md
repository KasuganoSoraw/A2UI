# chat_ui_builder 前端 Tailwind 第三阶段设计（稳定语义样式附着）

## 需求详情与澄清

### 需求
重构 `samples/client/react/chat_ui_builder` 样式附着方式：
- 不再主要依赖后端 slot id 后缀与深层 DOM 结构。
- 不改协议、不改后端主链路。
- 建立更稳定的前端语义包装层与变体系统。
- FlowDiagram 保持稳定可见。

### 当前问题
- 现有 `index.css` 中仍存在大量依赖后端命名/层级的选择器（如 `[id$='_header']` / `[id$='_body']` / `[id*='_fact_']`）。
- 这类样式在后端 archetype/bucket/slot 结构演进后容易失效。
- 协议层和渲染链路正常，问题在样式附着点不稳定。

## WHAT
1. 引入前端“语义标注层”：在渲染后对 A2UI DOM 进行语义归类（panel/facts/actions/form/workflow/list/header 等）。
2. 将样式从 id 后缀规则迁移到语义 class 规则。
3. 保留必要的基础 `.a2ui-*` 组件类样式，但弱化深层与后端命名耦合。
4. 保持 `cn()` + Tailwind 变体体系。

## WHY
- `.a2ui-*` 组件类型类比后端 slot id 更稳定。
- “语义 class + Tailwind 变体”比“后端 id 后缀匹配”更抗后端结构变化。
- 仍完全符合 A2UI 职责边界：后端给结构，前端做样式系统。

## HOW

### 实施策略
- 新增 hook（MutationObserver）对渲染结果做增量语义标注。
- App 中在 `render-surface` 容器挂 ref 并启用标注 hook。
- `index.css` 改为以 `.sem-*` 语义类为主进行样式附着。

### 风险控制
- 不改 `A2UIRenderer` 输入消息与处理流程。
- 不改 fetch stream / processMessages。
- 不改 planning delta 协议。

### 验收要点
- 大幅减少 id 后缀选择器。
- region/header/facts/actions/form/workflow 样式在结构变动下更稳定。
- FlowDiagram 继续可见。
