# 开发计划：chat_ui_builder 非流式加载页移除与初始化收敛

## Stage 1：实现与验证（单阶段提交）

### Task 1.1 代码改造
- 删除 `service.py` 中 `_loading_frames` 方法。
- 删除 `stream_frames()` 启动时发 loading frame 的逻辑。
- 收敛 `compiler.py::_init_surface` 为最小初始化实现。

### Task 1.2 测试调整
- 更新 `tests/test_service_single_path.py` 中对旧 `/title` 预制路径的断言。
- 改为断言 planning 主链可正常产出页面结构与错误兜底输出。

### Task 1.3 本地验证
- 运行目标测试文件，确认改动不破坏主链行为。

### Task 1.4 阶段提交
- 完成 Stage 1 后执行一次 git commit（中文简述）。
- 提交后补充 `progress.md` 追加记录。
