# chat_ui_builder streaming service 第二阶段流式化开发计划

## Stage 1：service 原地演进
### Task 1.1 新增流式入口与行解析器
- 在 `streaming/service.py` 内新增 `StreamEventLineParser`。
- 新增 `stream_project_segment(...)` 流式入口。

### Task 1.2 保留兼容入口
- 保留 `project_segment(...)`，内部复用流式入口聚合结果。
- 不新增新的主 service 文件。

### Task 1.3 补齐调试日志
- 增加第一阶段输入/输出/解析/过滤日志。
- 增加第二阶段输入/chunk/event->frame/最终汇总日志。

### Task 1.4 状态更新策略
- 第二阶段结束后统一应用 `_apply_events_to_page_state(...)`。

## Stage 2：校验与记录
### Task 2.1 语法检查
- `python -m py_compile chat_ui_builder/streaming/service.py`

### Task 2.2 进度与提交
- 追加 `progress.md`
- 中文 commit
- 创建 PR 记录
