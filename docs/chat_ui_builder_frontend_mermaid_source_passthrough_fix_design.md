# chat_ui_builder 前端 Mermaid source 透传修复设计

## 需求详情
当前 `Mermaid.tsx` 的 `buildMermaidSource()` 在 definition 已经是完整 Mermaid 定义（如 `graph TD ...`）时，仍可能拼接 `diagramType` 前缀，导致 source 变成非法组合（例如 `flowchart\ngraph TD ...`）并渲染失败。

## 澄清结果
- 只修改前端 Mermaid 渲染逻辑，不改后端协议 / planning event / spec 字段。
- 不新增 `width/height` 或其他表现字段。
- 保留现有空态、`console.warn`、初始化逻辑与 App.tsx 注册状态。

## WHAT
1. 将 `buildMermaidSource()` 改为：仅返回 `definition.trim()`。
2. 不再基于 `diagramType` 做任何前缀拼接。
3. 保留现有 `definition` 为空时空态分支逻辑。

## WHY
- Mermaid 定义通常自带完整头部（`graph TD`、`flowchart TD` 等），二次拼接会破坏语法。
- 对完整定义做“原样透传”是最稳健且最小改动方案。

## HOW
- 在 `Mermaid.tsx` 的 `buildMermaidSource()` 中移除 `startsWith(diagramType)` 判断与拼接逻辑。
- 返回值仅依赖 `definition.trim()`，空字符串时沿用现有空态。
