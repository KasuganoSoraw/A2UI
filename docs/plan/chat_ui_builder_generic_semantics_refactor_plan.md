# 开发计划：A2UI 去场景特化与 warning 通用语义接入

关联设计：`docs/chat_ui_builder_generic_semantics_refactor_design.md`

## Stage 1：设计与计划
### Task 1.1
梳理日志模板特化点（prompt、service、测试、文件）和 warning 接入点。

### Task 1.2
提交设计文档与开发计划。

## Stage 2：后端去特化与 schema 改造
### Task 2.1
删除 `log_template.py` 与 service 调用链，恢复通用规划主路径。

### Task 2.2
清理 prompt 中日志场景 one-shot 与日志优先模板说明。

### Task 2.3
在 models/contract 中接入 `warning` usage_hint。

## Stage 3：前端样式与测试收尾
### Task 3.1
在前端渲染样式中接入 warning usageHint 显示。

### Task 3.2
更新测试（移除日志模板直出测试，补充 warning 能力相关校验）。

### Task 3.3
运行检查、追加 progress、分阶段提交并创建 PR 信息。
