# chat_ui_builder 前端 LineChart 展示质量改造设计（Recharts）

## 需求详情
当前 `LineChart` 组件使用手写 SVG 折线绘制，展示效果较差（线段形态异常、可读性低、坐标与图例表现简陋）。
用户要求直接修改代码，并允许引入成熟前端组件包，不再自行实现底层绘图。

## 澄清结果
- 保持现有 A2UI 协议链路不变：`spec.path -> getValue(path) -> 解析 spec -> 渲染`。
- 仅改进前端 LineChart 视觉与稳定性，不改后端协议结构。
- 可引入成熟组件包，优先使用 React 生态图表库以降低维护成本。

## WHAT
1. 在前端示例工程中引入 `recharts` 依赖。
2. 将 `LineChart.tsx` 从手写 SVG 改为基于 Recharts 的实现：
   - `ResponsiveContainer + LineChart + CartesianGrid + XAxis + YAxis + Tooltip + Legend + Line`
   - 支持多指标折线与可选圆点（映射 `markPoint`）
   - 支持标题、轴标题、空态
3. 保持 `spec.path` 解析逻辑与降级逻辑一致。
4. 调整样式，移除对手写 SVG 的强耦合样式，保留外层卡片风格。

## WHY
- 成熟图表库在插值、坐标映射、响应式布局、图例/提示层方面更稳定。
- 减少自研图形逻辑导致的视觉缺陷和维护成本。
- 在不改变协议的前提下显著提升展示质量和可扩展性。

## HOW
- 依赖层：在 `samples/client/react/chat_ui_builder/package.json` 增加 `recharts`。
- 组件层：
  - 保留 `isLineChartSpec / extractSpecCandidate / parseSpec` 解析链路。
  - 新增数据清洗方法：过滤不可绘制 metric（全为空或非数值）。
  - 将图表主渲染替换为 Recharts 组件，并设置统一配色。
- 样式层：
  - 保留 `.a2ui-line-chart-card` 等容器样式。
  - 新增/调整 `.a2ui-line-chart-axis-titles`、tooltip 与 legend 相关样式。
- 验证层：执行前端 build（若环境缺依赖则记录原因）。
