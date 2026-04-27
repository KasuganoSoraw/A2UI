# 开发计划：chat_ui_builder 日志双通道改造

## Stage 1：日志基础设施搭建与接入

### Task 1.1 新增日志工具模块
- 创建 `logging_utils.py`，实现目录创建、控制台彩色 formatter、文件 formatter、handler 构建、统一初始化函数。

### Task 1.2 应用启动接入
- 修改 `app.py`，移除 `basicConfig`，改用 `configure_logging()` 初始化。

### Task 1.3 关键日志完整性增强
- 在 `service.py`、`app.py` 对关键大 payload 日志补充 `extra.full_message`，确保文件日志尽量写完整。

### Task 1.4 本地验证
- 运行编译/静态检查类命令，验证代码正确性与日志配置可导入。

### Task 1.5 阶段提交
- 完成 Stage 1 后执行一次中文 commit，并追加 `progress.md` 记录。
