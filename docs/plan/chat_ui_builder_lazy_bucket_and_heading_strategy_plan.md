# Chat UI Builder 业务骨架懒创建与标题层级治理计划

关联设计：`docs/chat_ui_builder_lazy_bucket_and_heading_strategy_design.md`

## Stage 1：方案固化
### Task 1.1
- 审查 `skeleton_compiler.py` 中 layout scaffold 与 bucket 预创建逻辑。

### Task 1.2
- 明确 hero h1 与页面 title 的去重/降级规则及触发时机。

## Stage 2：编码实现
### Task 2.1
- 删除 `init_plan` 后全量 bucket 预创建路径，保留最小硬骨架。

### Task 2.2
- 实现 `ensure bucket exists` 懒创建机制：在 `add_region` 首次落某 role 时创建 bucket。

### Task 2.3
- 实现 hero h1 冲突治理（重叠则去重，否则降级 h2）。

## Stage 3：测试与收尾
### Task 3.1
- 新增/更新测试验证懒创建与标题层级治理。

### Task 3.2
- 运行测试或最小语法检查并记录环境限制。

### Task 3.3
- 追加 `progress.md`，并按阶段提交中文 commit。
