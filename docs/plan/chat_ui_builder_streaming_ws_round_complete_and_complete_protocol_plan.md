# chat_ui_builder streaming ws 协议收敛开发计划

## Stage 1：ws 协议定向修改
### Task 1.1 调整 `a2ui_frame`
- 删除 `a2ui_frame` 中的 `final` 字段。

### Task 1.2 调整本轮结束事件
- 将 `streaming_final` 改为 `streaming_round_complete`。

### Task 1.3 增加整条流结束事件
- 在本轮完成且请求 `is_final=true` 时发送 `complete`。

### Task 1.4 收敛状态消息
- `streaming_status` 去掉 `final` 字段。

## Stage 2：校验与记录
### Task 2.1 语法检查
- `python -m py_compile samples/agent/adk/chat_ui_builder/app.py`

### Task 2.2 进度与提交
- 追加 `progress.md`
- 中文 commit
- 创建 PR 记录
