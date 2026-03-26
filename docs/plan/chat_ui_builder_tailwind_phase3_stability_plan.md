# 开发计划：chat_ui_builder Tailwind 第三阶段（样式稳定性）

## Stage 1：语义附着机制

### Task 1.1 新增语义标注 hook
- 新建 hook，对 `.a2ui-card/.a2ui-row/.a2ui-column` 进行语义归类并打 `.sem-*` class。
- 使用 MutationObserver 适配流式增量渲染。

### Task 1.2 App 接线
- 在 `App.tsx` 为 render-surface 增加 ref 并调用 hook。

## Stage 2：样式规则重构

### Task 2.1 index.css 去耦
- 移除/弱化 id 后缀和深层结构依赖。
- 以 `.sem-*` 语义类 + 稳定 `.a2ui-*` 类型类重写样式。

### Task 2.2 FlowDiagram 稳定性确认
- 保持 FlowDiagram 样式不依赖后端 slot 命名。
- 校验可见性样式完整。

## Stage 3：验证与进度

### Task 3.1 构建验证
- 运行 `npm run build`（若环境依赖缺失则记录）。

### Task 3.2 进度记录与提交
- 追加 `progress.md`。
- 每个 stage 完成后提交中文 commit。
