# chat_ui_builder streaming session 级 StreamCompiler 隔离修复计划

## Stage 1：service 去全局 compiler
### Task 1.1 调整 service 接口
- `stream_project_segment(...)` 增加 `stream_compiler` 显式参数。
- 删除 `self._stream_compiler` 依赖。

## Stage 2：runtime 托管 session compiler
### Task 2.1 新增 session compiler 容器
- 在 runtime 中新增 `dict[session_id, StreamCompiler]`。
- 实现按 session 获取/创建并复用。

### Task 2.2 调用链改造
- runtime 调 service 时传入 session compiler。
- 增加关键日志确认 compiler 归属。

## Stage 3：校验与记录
### Task 3.1 语法检查
- `python -m py_compile chat_ui_builder/streaming/service.py chat_ui_builder/streaming/runtime.py`

### Task 3.2 进度与提交
- 追加 `progress.md`
- 中文 commit
- 创建 PR 记录
