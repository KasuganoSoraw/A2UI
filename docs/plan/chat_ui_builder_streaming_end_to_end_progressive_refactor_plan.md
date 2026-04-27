# chat_ui_builder streaming 端到端渐进式收敛重构计划

## Stage 1：service 主路径收敛
### Task 1.1 删除非渐进式入口与旧解析逻辑
- 删除 `project_segment(...)`。
- 删除 `_parse_stream_events(...)`。

### Task 1.2 保留唯一流式主入口并收敛日志
- 保留 `stream_project_segment(...)`。
- 保留关键日志，移除无意义 chunk 刷屏日志。

## Stage 2：runtime 主路径流式化
### Task 2.1 新增并启用 `stream_submit_snapshot(...)`
- 按 session 串行调度 + latest 覆盖。
- 每轮触发后消费 service 流式输出并向上透传 frame。
- final 阶段统一提交 state。

### Task 2.2 删除旧整轮返回入口
- 删除 `submit_snapshot(...)` 非渐进式返回路径。

## Stage 3：app 逐帧发送
### Task 3.1 ws 路由改为流式消费 runtime
- `async for item in streaming_runtime.stream_submit_snapshot(...)`
- `frame -> a2ui_frame` 单帧发送
- `final -> streaming_final` 轻量结束消息

### Task 3.2 保持输入协议与错误处理
- 保持 sendMessage/message/final 校验逻辑。

## Stage 4：校验与记录
### Task 4.1 语法检查
- `python -m py_compile chat_ui_builder/streaming/service.py chat_ui_builder/streaming/runtime.py chat_ui_builder/app.py`

### Task 4.2 进度与提交
- 追加 `progress.md`
- 中文 commit
- 创建 PR 记录
