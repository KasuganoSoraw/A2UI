# chat_ui_builder add_region_pie_chart 全链路设计

## 需求详情
在当前分支继续新增 `PieChart` 图表事件，要求后端到前端的接入路径严格仿照现有 `LineChart`：
- planning：`add_region_pie_chart`
- low-level：`add_pie_chart`
- frame：`PieChart.spec.path=/content/<id>/spec`
- dataModelUpdate：`path=/content/<id>` 下 `key=spec` 且 `valueString=spec_json`

## 澄清结果
- 不新增 role / layout / slot，不修改现有 Table / LineChart 行为。
- 不让前端拼 spec，仍由 skeleton compiler 组装 `spec_json`。
- 前端图表库沿用 recharts，组件结构与 LineChart 保持一致的解析链路与降级策略。

## WHAT
1. 后端协议新增 `add_region_pie_chart` 与 `add_pie_chart` schema，并接入现有 union/adapter。
2. SkeletonCompiler 新增 pie chart 编译分支：`chart_data -> chartData`，打包为 `spec_json`，走 `_apply_region_delta(region_id, 'text', ...)`。
3. FrameCompiler 新增 `_add_pie_chart`，输出 `PieChart.spec.path` 与 `/content/<id>/spec` 的 `valueString` 数据写入。
4. Prompt contract 与规则补充 pie chart 事件定义与适用场景。
5. 前端新增 `PieChart.tsx`（spec.path 解析与 LineChart 同路径），并在 `App.tsx` 注册、`App.css` 增加最小样式。
6. 补充最小必要测试：schema 解析、skeleton 路由、frame 输出、spec 字段完整性。

## WHY
- 与 LineChart 统一链路可保证协议一致性、维护成本可控、测试模式复用。
- 占比/构成型数据通过 pie chart 展示更直观，避免强行文本化。

## HOW
- 复用 LineChart 的四层路径：`models -> skeleton_compiler -> compiler -> frontend component`。
- spec 形状统一为：`{title,width,settings,chartData}`，其中 planning 事件字段 `chart_data` 在 skeleton 阶段转换为 `chartData`。
- 前端 `PieChart.tsx` 复用 `extractSpecCandidate + parseSpec + empty fallback`，并用 recharts 的 `PieChart/Pie/Tooltip/Legend/Cell` 完成渲染。
