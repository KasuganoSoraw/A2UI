# chat_ui_builder 前端 Mermaid source 透传修复计划

## Stage 1：设计与计划
### Task 1.1
- 编写 Mermaid source 透传修复设计文档。
### Task 1.2
- 制定最小改动执行计划。

## Stage 2：编码修复
### Task 2.1
- 修改 `Mermaid.tsx`：`buildMermaidSource()` 仅返回 `definition.trim()`。
### Task 2.2
- 确认未触及后端协议与 spec 字段。
### Task 2.3
- 确认 `App.tsx` Mermaid import/registry 仍存在。

## Stage 3：验证与收尾
### Task 3.1
- 执行最小检查并记录结果。
### Task 3.2
- 追加 `progress.md`。
### Task 3.3
- 分阶段中文提交。
