# chat_ui_builder streaming 单阶段 LLM 收敛重构计划

## Stage 1：prompt 收敛
### Task 1.1 删除两阶段 prompt
- 删除 `binding_prompt.py`。
- 保留并重写 `stream_event_prompt.py` 为单阶段提示。
- 更新 `prompt/__init__.py` 导出。

## Stage 2：service 收敛
### Task 2.1 删除两阶段遗留代码
- 删除 binding decision/result 模型与解析筛选逻辑。
- 删除两阶段输入拼装与日志。

### Task 2.2 单阶段主链实现
- `stream_project_segment(...)` 直接组单阶段输入。
- 流式解析 NDJSON event，逐 event 编译 frame 并 yield。
- 结束后统一更新 binding/page state 并产出 final。

## Stage 3：校验与记录
### Task 3.1 语法检查
- `python -m py_compile chat_ui_builder/streaming/service.py chat_ui_builder/streaming/prompt/stream_event_prompt.py chat_ui_builder/streaming/prompt/__init__.py chat_ui_builder/streaming/runtime.py`

### Task 3.2 进度与提交
- 追加 `progress.md`
- 中文 commit
- 创建 PR 记录
