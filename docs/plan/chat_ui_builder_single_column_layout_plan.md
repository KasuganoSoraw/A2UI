# 开发计划：Chat UI Builder 布局收敛为单列

关联设计：`docs/chat_ui_builder_single_column_layout_design.md`

## Stage 1：设计与计划
### Task 1.1
梳理当前双栏 scaffold、side bucket、arrangement 分支与 flow 事件处理路径。

### Task 1.2
输出设计文档与分阶段开发计划。

## Stage 2：核心代码收敛
### Task 2.1
修改 `skeleton_compiler.py`：删除双栏 scaffold / side context / 双栏 hint 依赖，统一单列 bucket parent。

### Task 2.2
实现 flow diagram 独占 region（workflow 专用 region 自动复用/创建）。

### Task 2.3
必要时调整 `region_archetypes.py`，保证 supporting/actions 等在单列展示语义下稳定。

## Stage 3：验证与收尾
### Task 3.1
更新/新增测试，覆盖单列收敛与 flow 独占行为。

### Task 3.2
运行检查命令并修正问题。

### Task 3.3
追加 `progress.md`、分阶段提交并生成 PR 信息。
