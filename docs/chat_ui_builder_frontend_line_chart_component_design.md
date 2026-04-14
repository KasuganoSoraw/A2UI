# Chat UI Builder 前端 LineChart 组件接入设计

## 需求详情
- 新增 `LineChart` 前端组件并注册到 `ComponentRegistry`。
- 组件必须按 `Table.tsx` 同路径消费协议：`spec.path -> getValue(path) -> extract -> parse -> render`。
- 使用原生 SVG 实现最小可用折线图，不引入图表库。

## 澄清结果
- 不改后端协议，A2UI 组件名保持 `LineChart`。
- 不重构其他组件，仅做最小增量。
- 解析失败时降级展示，`console.warn`，不抛异常。

## WHAT
1. 新增 `src/components/LineChart.tsx`：
   - `memo` + `useA2UIComponent(node, surfaceId)`。
   - 类型：`LineChartSettings`、`LineChartSpec`、`SpecBinding`、`LineChartNodeProps`。
   - 工具：`isLineChartSpec`、`extractSpecCandidate`、`parseSpec`。
   - 纯 SVG 折线图渲染，支持多指标、markPoint、标题、图例与 X 轴标签。
2. 修改 `src/App.tsx`：注册 `LineChart`。
3. 修改 `src/App.css`：增加 line chart 最小样式。

## WHY
- 与 `Table.tsx` 保持一致可降低协议理解成本，减少前后端契约偏差。
- 先做最小 SVG 渲染可快速验证 `LineChart.spec.path` 链路。

## HOW
1. 先解析 spec（支持 string/object/path/binding）。
2. 校验 `settings.dimension + settings.metrics + chartData`。
3. 提取每个 metric 的有效数值点，统一 min/max 映射到坐标系。
4. 输出 `<polyline>`，`markPoint=true` 时输出 `<circle>`。
5. 对空数据、空指标、无有效点分别输出空态文案。
