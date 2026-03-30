# 开发计划：通用 prompt 语义增强（FlowDiagram + usage_hint）

关联设计：`docs/chat_ui_builder_prompt_semantics_enhancement_design.md`

## Stage 1：设计与计划
### Task 1.1
梳理当前 prompt、schema、list item usage_hint 硬编码点。

### Task 1.2
提交设计文档和开发计划。

## Stage 2：后端与 prompt 改造
### Task 2.1
增强 prompt：usage_hint 语义 + FlowDiagram 规则 + one-shot。

### Task 2.2
扩展 models：list item 可选 usage_hint 字段。

### Task 2.3
调整 skeleton/compiler：模型优先，默认兜底。

## Stage 3：测试与收尾
### Task 3.1
新增/更新测试覆盖 usage_hint 透传行为。

### Task 3.2
运行检查命令并记录环境限制。

### Task 3.3
追加 progress、分阶段提交并创建 PR 信息。
