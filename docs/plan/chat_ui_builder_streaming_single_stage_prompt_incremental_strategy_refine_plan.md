# chat_ui_builder 单阶段 streaming prompt 增量策略收敛计划

## Stage 1：提示词规则收敛
### Task 1.1 强化统一增量原则
- 先显示后补全。
- 单事件小负载。
- text/facts/list/table/final summary 全组件统一约束。

### Task 1.2 加强“围绕 changes”约束
- 优先表达新增内容，避免重述整个 visible_snapshot。

### Task 1.3 收敛长度
- 合并重复规则。
- 删除冗余表述，保持短而硬。

## Stage 2：校验与记录
### Task 2.1 语法检查
- `python -m py_compile samples/agent/adk/chat_ui_builder/streaming/prompt/stream_event_prompt.py`

### Task 2.2 进度与提交
- 追加 `progress.md`
- 中文 commit
- 创建 PR 记录
