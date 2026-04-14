# chat_ui_builder add_region_pie_chart 全链路开发计划

## Stage 1：设计与计划
### Task 1.1
- 编写 PieChart 全链路设计文档（WHAT/WHY/HOW）。
### Task 1.2
- 形成分阶段开发计划与测试范围。

## Stage 2：后端协议与编译链路
### Task 2.1
- `models.py` 新增 PieChart planning/low-level schema 并接入 adapter union。
### Task 2.2
- `skeleton_compiler.py` 新增 `AddRegionPieChartDelta -> AddPieChartDelta` 路由，组装 spec_json。
### Task 2.3
- `compiler.py` 新增 `_add_pie_chart` 并在 `apply()` 接入，输出 `PieChart.spec.path` 和 dataModelUpdate。
### Task 2.4
- `prompting.py` 更新 planning contract 与 pie chart 适用规则。

## Stage 3：前端接入与样式
### Task 3.1
- 新增 `components/PieChart.tsx`，解析链路严格仿照 LineChart。
### Task 3.2
- `App.tsx` 注册 `PieChart` 组件。
### Task 3.3
- `App.css` 新增最小 pie chart 样式。

## Stage 4：测试与收尾
### Task 4.1
- 扩展测试覆盖 schema、skeleton、frame、spec 字段。
### Task 4.2
- 运行最小测试集并记录结果。
### Task 4.3
- 追加 `progress.md` 并分阶段中文提交。
