# chat_ui_builder WebSocket 调试接口开发计划

## Stage 1：设计与基线确认
### Task 1.1
- 阅读 `app.py` 与最近进度，确认仅做后端单文件最小变更。

## Stage 2：实现最小接口
### Task 2.1
- 在 `app.py` 增加 WebSocket 相关 import。
### Task 2.2
- 新增 `/ws/debug` 路由，实现连接、接收文本、日志输出、断开与异常日志。

## Stage 3：验证与收尾
### Task 3.1
- 运行最小语法检查，确认文件可运行。
### Task 3.2
- 追加 `progress.md` 记录并提交。
