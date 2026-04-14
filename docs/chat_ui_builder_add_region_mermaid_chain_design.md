# chat_ui_builder add_region_mermaid 全链路设计

## 需求详情
新增 Mermaid 展示能力，路径必须与现有重组件一致：
planning event -> skeleton compiler 组装 spec_json -> low-level event -> frame compiler 输出 `Mermaid.spec.path` -> 前端按 `spec.path` 渲染。

## 澄清结果
- 新增统一事件 `add_region_mermaid`，不为每种图拆事件。
- 后端协议/规格中禁止加入 `width/height` 等前端表现字段。
- 不新增 role/layout/slot，不改 Table/LineChart/PieChart/FlowDiagram 既有行为。

## WHAT
1. `models.py` 新增 `AddRegionMermaidDelta` 与 `AddMermaidDelta`，并接入 union/adapter。
2. `skeleton_compiler.py` 新增 Mermaid 编译分支：
   - spec 仅包含 `title/diagramType/definition`
   - `diagram_type -> diagramType`
   - 根据 diagram_type 路由 slot：
     - `flowchart/sequenceDiagram/stateDiagram-v2` -> `flow`
     - `erDiagram/classDiagram` -> `text`
3. `compiler.py` 新增 `_add_mermaid()`，输出 `Mermaid.spec.path` 与 `/content/<id>/spec` 的 valueString。
4. `prompting.py` 扩展 contract 与 Mermaid 使用规则（role 限制、与 flow_diagram/table 去重）。
5. 前端新增 `Mermaid.tsx`，按 Table/LineChart 同样 spec 解析链路 + Mermaid 库渲染。
6. `App.tsx` 注册 Mermaid，`App.css` 增加最小样式。
7. 测试覆盖 schema、路由、frame 输出、spec 字段完整性与无 width/height。

## WHY
- Mermaid 更适合 sequence/state/ER/class 等关系结构图；但协议要保持语义纯净，前端表现应由前端控制。
- 统一事件+分流路由可降低协议复杂度，同时复用既有渲染/编译链路。

## HOW
- 后端严格沿用重组件模式：skeleton 产 spec_json，frame 只输出 `spec.path`。
- 前端只消费 spec，不推断后端意图：直接按 `diagramType + definition` 渲染 Mermaid。
- 渲染失败显示降级文案并 `console.warn`，不抛异常中断页面。
