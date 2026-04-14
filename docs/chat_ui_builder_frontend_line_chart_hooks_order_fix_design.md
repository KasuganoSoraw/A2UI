# chat_ui_builder LineChart Hooks 顺序修复设计

## 需求详情
`LineChart.tsx` 当前存在 React Hooks 顺序错误：在多个 early return 之后才调用 `useMemo`，会触发 `Rendered more hooks than during the previous render`。

## 澄清结果
- 组件契约保持不变：`useA2UIComponent(node, surfaceId)`、`spec.path`、当前 spec 结构、recharts 全部保留。
- 仅修复 Hooks 顺序问题，不改后端协议，不做无关重构。
- 采用最小修改方案：保留 `useMemo`，但将相关 hooks 前置到任何条件 return 之前。

## WHAT
1. 将 `displayData` 的 `useMemo` 前置到所有 early return 之前。
2. 将 `metrics` 的 `useMemo` 前置到所有 early return 之前。
3. 在 memo 回调内加入空值/结构判断，保证 `spec` 不可用时返回空数组。
4. 维持现有空态分支逻辑与 Recharts 渲染逻辑。

## WHY
- React 要求 hooks 调用顺序在每次渲染中完全一致。
- 通过“hooks 顶层前置 + 回调内兜底”可在最小改动下彻底消除顺序漂移。

## HOW
- 先解析 `spec`。
- 立即计算 `chartWidthStyle`、`displayData(useMemo)`、`metrics(useMemo)`。
- 再执行 `!spec` / metrics 空 / chartData 空 / renderable metrics 空等 early return。
- 保持原有 UI 文案、数据契约、recharts 组件树不变。
