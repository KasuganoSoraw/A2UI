# chat_ui_builder add_region_mermaid 全链路开发计划

## Stage 1：设计与计划
### Task 1.1
- 编写 Mermaid 全链路设计文档（协议边界、路由规则、前端渲染约束）。
### Task 1.2
- 形成分阶段开发计划与最小测试范围。

## Stage 2：后端协议与编译链路
### Task 2.1
- `models.py` 新增 Mermaid planning/low-level schema 并接入 adapter。
### Task 2.2
- `skeleton_compiler.py` 新增 `AddRegionMermaidDelta` 分支并按 diagram_type 路由 flow/text。
### Task 2.3
- `compiler.py` 新增 `_add_mermaid()` + `apply()` 接入，输出 Mermaid.spec.path 与 dataModel spec。
### Task 2.4
- `prompting.py` 更新 contract 与 Mermaid 使用规则（role 限制/去重规则）。

## Stage 3：前端接入
### Task 3.1
- 新增 `components/Mermaid.tsx`，解析路径严格仿照 Table/LineChart。
### Task 3.2
- `App.tsx` 注册 Mermaid。
### Task 3.3
- `App.css` 新增最小 Mermaid 样式（容器、标题、画布、空态）。
### Task 3.4
- `package.json` 增加 `mermaid` 依赖。

## Stage 4：测试与收尾
### Task 4.1
- 扩展测试覆盖：schema、diagram_type 路由、frame path、spec 字段、无 width/height。
### Task 4.2
- 运行最小测试集并记录结果。
### Task 4.3
- 追加 `progress.md` 并按阶段中文提交。
