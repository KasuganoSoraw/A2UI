# chat_ui_builder LineChart CSS 覆盖修复设计

## 需求详情
当前 `LineChart` 中 tooltip/legend 可见且可命中点位，但折线和网格线几乎不可见，怀疑 SVG 样式被全局规则覆盖。

## 澄清结果
- 不改后端协议、不改图表数据逻辑、不移除 recharts。
- 以最小改动修复样式污染：优先定位来源，再做作用域内保护样式。
- 保持现有组件契约与空态逻辑不变。

## WHAT
1. 排查全局样式来源，确认影响 Recharts SVG 线条的真实规则。
2. 在 `LineChart` 作用域增加最小保护样式，恢复折线/网格/坐标轴/点位可见性。
3. 在 `LineChart.tsx` 增加系列颜色变量传递，避免颜色被 reset 后丢失。

## WHY
- 命中点与 tooltip 正常说明数据和坐标映射没问题，主要是可视样式层被覆盖。
- 采用作用域保护比全局覆盖更安全，避免影响 Table/Timeline/FlowDiagram。

## HOW
- 定位来源：`renderers/react/src/styles/reset.ts` 存在 `.a2ui-surface * { all: revert; }`，会重置 SVG 的 `stroke/fill` CSS 属性，导致依赖 presentation attributes 的 Recharts 线条不可见。
- 修复策略：
  - `App.css` 在 `.render-surface .a2ui-line-chart` 作用域补充 Recharts 保护样式（curve/grid/axis/dot）。
  - `LineChart.tsx` 的 `<Line>` 传入 CSS 变量 `--a2ui-line-color`，由 scoped CSS 显式指定 `stroke/fill`。
- 验证：执行前端构建检查并记录环境限制。
