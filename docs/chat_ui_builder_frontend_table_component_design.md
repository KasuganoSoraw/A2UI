# Chat UI Builder 前端 Table 组件接入设计

## 需求详情
- 新增 React 前端 `Table` 组件，消费后端输出的 A2UI `Table` 帧。
- 支持 `spec.path` -> data model 值读取 -> JSON 解析 -> HTML table 渲染。
- 在 `App.tsx` 注册 `Table`，并在 `App.css` 增加最小样式。

## 澄清结果
- 不改后端协议与组件名，仍为 `Table`。
- 不新增 UI 依赖库，使用原生 HTML table。
- 解析失败不抛异常，给降级 UI 并 `console.warn`。

## WHAT
1. 新增 `src/components/Table.tsx`：
   - `memo` + `useA2UIComponent(node, surfaceId)`。
   - 定义 `TableColumnSpec/TableSpec/SpecBinding/TableNodeProps`。
   - 提供 `isTableSpec/extractSpecCandidate/parseSpec/normalizeCellValue/resolveAlignClass`。
2. `App.tsx` 注册 `Table` 到 `ComponentRegistry`。
3. `App.css` 增加 table 相关最小样式（滚动、对齐、省略、空态、striped/bordered）。

## WHY
- 后端当前传的是 `Table.spec.path` + `valueString(JSON)`，前端必须显式完成 path 取值与 JSON 解析。
- 先用最小 HTML table 实现可保障链路可用，后续可平滑替换为更复杂组件库实现。

## HOW
1. 从 `node.properties.spec` 提取候选值：支持 string / 对象 / path binding / literalString/valueString/literal。
2. `parseSpec` 严格校验 `columns + rows` 结构，失败返回空态。
3. 按列定义渲染 thead/tbody，单元格统一值归一化，行 key 优先 `row_key -> row.id -> index`。
4. 用 class 控制 striped/bordered/align/ellipsis，不做 JS 截断。
