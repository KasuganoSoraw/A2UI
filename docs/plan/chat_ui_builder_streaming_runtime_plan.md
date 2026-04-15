# chat_ui_builder streaming runtime 开发计划

## Stage 1：设计落地与 runtime 实现
### Task 1.1 新增 runtime 会话状态与主入口
- 新建 `streaming/runtime.py`。
- 定义 `StreamingSessionState` 与 `StreamingRuntime.__init__`。
- 实现 `submit_snapshot(...)` 的状态更新与返回结构。

### Task 1.2 实现同 session 串行 drain
- 实现 `_drain_session(...)` 循环。
- 处理 processing 期间的 pending update。
- 实现最新 raw_text 覆盖逻辑（非 FIFO）。

### Task 1.3 实现触发规则与 service 串联
- 实现 `_should_trigger_first_render(...)`。
- 实现 `_should_trigger_incremental_render(...)`。
- 实现 `_has_meaningful_changes(...)` 与跳过条件。
- 按约定 payload 调用 `project_segment` 并回写 state。

## Stage 2：自检与记录
### Task 2.1 运行最小语法检查
- 运行 `python -m py_compile` 校验新增文件。

### Task 2.2 进度与提交
- 仅追加更新 `progress.md`。
- 提交 git commit（中文简要信息）。
- 创建 PR 记录。
