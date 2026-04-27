# chat_ui_builder 单阶段 streaming prompt changes 去重收敛计划

## Stage 1：规则收敛
### Task 1.1 强化 changes 主任务
- 明确本轮只响应新增内容。
- visible_snapshot 仅作上下文。

### Task 1.2 强化去重展示规则
- 同一新增只保留一个主表达。
- 优先复用已有 block，避免重复 create。
- 概览与明细避免互相重复。

### Task 1.3 控制长度
- 合并重复规则，保持短而硬。

## Stage 2：校验与记录
### Task 2.1 语法检查
- `python -m py_compile chat_ui_builder/streaming/prompt/stream_event_prompt.py`

### Task 2.2 进度与提交
- 追加 `progress.md`
- 中文 commit
- 创建 PR 记录
