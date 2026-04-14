# chat_ui_builder LineChart 折线可见性稳定修复设计

## 需求详情
当前 LineChart 中网格线与 tooltip 已恢复，但折线本体仍不可见。用户要求删除错误的 CSS 颜色接管（`--a2ui-line-color` + `.recharts-line-curve stroke !important`），改为由 Recharts `<Line>` props 稳定控制线/点颜色。

## 澄清结果
- 仅修改 `App.css` 与 `LineChart.tsx`。
- 不改后端协议，不改组件名，不改数据结构，不移除 recharts。
- 保留当前空态逻辑。

## WHAT
1. 删除 `.recharts-line-curve` 上对 `stroke: var(--a2ui-line-color) !important` 的覆盖。
2. 保留曲线可见性保护（`fill:none`、`stroke-opacity`、`opacity`）。
3. 删除 `<Line>` 的 CSS 变量透传实现（`className/style --a2ui-line-color`）。
4. 将 `<Line>` 改为完全依赖 Recharts props 控制视觉：`stroke/strokeWidth/strokeOpacity/fill/dot/activeDot`。

## WHY
- 折线颜色应由 `<Line stroke={...}>` 直接控制，避免被外层 CSS 二次接管。
- 减少 `!important + CSS 变量 + SVG class` 组合带来的不确定性，提升跨样式环境稳定性。

## HOW
- `App.css`：仅删除折线颜色接管与 dot 颜色变量接管，保留网格/坐标轴保护样式与曲线可见性保护。
- `LineChart.tsx`：
  - 去掉 `CSSProperties` 引入。
  - 每条 `Line` 显式设置 `fill="none"`。
  - `dot` 使用对象（或 false）并显式设置 `fill/stroke`。
  - `activeDot` 显式设置半径与颜色。
- 验证：运行构建命令并记录环境依赖限制。
