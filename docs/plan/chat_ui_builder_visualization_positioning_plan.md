# 开发计划：A2UI 展示层定位收敛

关联设计：`docs/chat_ui_builder_visualization_positioning_design.md`

## Stage 1：设计与计划
### Task 1.1
分析 prompt、service、API 请求模型与测试覆盖点。

### Task 1.2
产出定位收敛设计文档与分阶段开发计划。

## Stage 2：实现展示层主逻辑
### Task 2.1
修改 `prompting.py`：改为 source_data 驱动，并明确“只展示、不编造”。

### Task 2.2
修改 `service.py`：支持 `source_data/user_query`，并新增动作区域最小约束。

### Task 2.3
修改 `app.py` 和 README，支持新请求形态并保留兼容。

## Stage 3：测试与收尾
### Task 3.1
更新/新增测试，覆盖数据驱动输入与 action 过滤行为。

### Task 3.2
运行检查命令并记录环境限制。

### Task 3.3
追加 progress.md，分阶段提交并生成 PR 信息。
