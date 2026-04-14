# 开发计划：list timeline 展示变体接入

关联设计：`docs/chat_ui_builder_list_timeline_variant_design.md`

## Stage 1：设计与计划
### Task 1.1
梳理 add_region/list/archetype/compiler 现状与 timeline 变体接入点。

### Task 1.2
提交设计文档与开发计划。

## Stage 2：后端链路实现
### Task 2.1
扩展 prompt/contract 与 schema（presentation.variant）。

### Task 2.2
在 skeleton/archetype 传递并应用 timeline 变体。

### Task 2.3
在 compiler 输出 Timeline / TimelineItem（standard 行为保持不变）。

## Stage 3：测试与收尾
### Task 3.1
更新测试覆盖 standard vs timeline 与 usage_hint 优先级。

### Task 3.2
运行检查命令并记录环境限制。

### Task 3.3
追加 progress、分阶段提交并创建 PR 信息。
