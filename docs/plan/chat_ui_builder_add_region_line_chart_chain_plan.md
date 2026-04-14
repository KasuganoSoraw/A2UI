# Chat UI Builder add_region_line_chart 全链路接入计划

关联设计：`docs/chat_ui_builder_add_region_line_chart_chain_design.md`

## Stage 1：模型与协议
### Task 1.1
- 在 `models.py` 新增 line chart planning/low-level schema。

### Task 1.2
- 接入 `SkeletonDelta` 与 `Delta` 适配器。

## Stage 2：编译链路
### Task 2.1
- 在 `skeleton_compiler.py` 新增 add_region_line_chart -> AddLineChartDelta 路由（text 默认落点）。

### Task 2.2
- 在 `compiler.py` 新增 `AddLineChartDelta` 编译与 `LineChart.spec.path` 输出。

### Task 2.3
- 在 `prompting.py` 增加 contract 与使用规则。

## Stage 3：测试与收尾
### Task 3.1
- 补充 tests：schema 解析、skeleton 路由、frame 输出与 spec 字段断言。

### Task 3.2
- 执行测试/语法检查并记录环境限制。

### Task 3.3
- 追加 progress 并按阶段中文提交。
