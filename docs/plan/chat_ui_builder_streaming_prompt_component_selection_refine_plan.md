# chat_ui_builder streaming prompt 主组件选择收敛开发计划

## Stage 1：第一阶段判别规则收敛
### Task 1.1 更新 binding prompt
- 收紧 facts 使用范围（概览/摘要）。
- 强化 list/table 对记录集合的优先级。
- 增加 list 与 table 的区分准则。

## Stage 2：第二阶段展开约束收敛
### Task 2.1 更新 stream_event prompt
- facts 只保留少量概览字段。
- list 逐条提炼 title/detail。
- table 仅选关键列，不全字段铺列。
- final summary 仅做概括。

## Stage 3：校验与记录
### Task 3.1 语法检查
- `python -m py_compile samples/agent/adk/chat_ui_builder/streaming/prompt/binding_prompt.py samples/agent/adk/chat_ui_builder/streaming/prompt/stream_event_prompt.py`

### Task 3.2 进度与提交
- 追加 `progress.md`
- 中文 commit
- 创建 PR 记录
