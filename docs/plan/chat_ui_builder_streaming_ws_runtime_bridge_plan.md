# chat_ui_builder streaming ws runtime 接入开发计划

## Stage 1：接口设计落地
### Task 1.1 新增设计文档与计划
- 新增 runtime 接入设计文档。
- 明确输入协议、错误协议、输出 frames 协议。

### Task 1.2 app.py 薄接口实现
- 模块级创建共享 `StreamingRuntime`。
- 新增 `/api/chat/ws/stream` WebSocket 路由。
- 实现消息解析、字段校验、runtime 调用、frames 回传。
- 增加必要中文注释，强调 app 只做入口层。

## Stage 2：校验与记录
### Task 2.1 最小语法检查
- 运行 `python -m py_compile chat_ui_builder/app.py`。

### Task 2.2 进度与提交
- 追加更新 `progress.md`。
- 完成中文 commit。
- 创建 PR 记录。
