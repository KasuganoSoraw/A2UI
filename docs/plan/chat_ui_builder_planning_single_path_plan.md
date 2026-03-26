# 开发计划：Chat UI Builder 收敛为 Planning Delta 单路径

关联设计：`docs/chat_ui_builder_planning_single_path_design.md`

## Stage 1：现状梳理与主链确认
### Task 1.1
审阅 `service.py`、`planning_stream.py`、`skeleton_compiler.py`、`compiler.py`、`models.py`，确认主链与 fallback 交叉点。

### Task 1.2
盘点 IntentPlan/legacy fallback 的直接依赖文件与引用关系，形成删除清单。

## Stage 2：代码收敛与清理
### Task 2.1
改造 `service.py` 为 planning-only 控制流，删除 IntentPlan 和 legacy fallback 分支与辅助函数。

### Task 2.2
删除 fallback-only 文件与 import 依赖，更新 README 架构说明。

### Task 2.3
清理死代码和无用符号，保证静态检查通过。

## Stage 3：验证与收尾
### Task 3.1
新增/更新测试覆盖单路径行为（流式渐进输出、解析失败报错）。

### Task 3.2
运行测试/检查命令并修复问题。

### Task 3.3
更新 `progress.md`（追加记录）、执行 git 提交、创建 PR 信息。
