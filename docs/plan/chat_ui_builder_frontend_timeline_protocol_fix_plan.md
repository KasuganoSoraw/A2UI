# Chat UI Builder 前端 Timeline 协议修复开发计划

关联设计：`docs/chat_ui_builder_frontend_timeline_protocol_fix_design.md`

## Stage 1：设计与实现准备
### Task 1.1
- 对照需求确认修复范围：仅 `Timeline.tsx`、`TimelineItem.tsx`。

### Task 1.2
- 参照内置 `Card` / `List` 的组件协议模式，明确以下约束：
  - 入参必须是 `A2UIComponentProps`
  - 子节点必须来自 `node.properties`
  - 子节点渲染必须经过 `ComponentNode`

## Stage 2：编码修复
### Task 2.1
- 重写 `Timeline.tsx`：
  - 接入 `useA2UIComponent`
  - 读取 `properties.children`
  - 递归渲染 child nodes
  - 支持 `node.weight`

### Task 2.2
- 重写 `TimelineItem.tsx`：
  - 接入 `useA2UIComponent`
  - 优先 `properties.child`，兼容 `children`
  - 渲染 dot/line/content 结构内的 child node
  - 支持 `node.weight`
  - 增加未来扩展字段读取占位

## Stage 3：验证与收尾
### Task 3.1
- 执行前端构建检查（或说明环境限制）。

### Task 3.2
- 在 `progress.md` 追加进度记录（只追加不改历史）。

### Task 3.3
- 按阶段完成提交，提交信息使用中文并简要总结改动。
