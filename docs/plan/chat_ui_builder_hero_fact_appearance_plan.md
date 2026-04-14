# chat_ui_builder hero_fact 容器级 appearance 改造计划

## Stage 1：设计与计划
### Task 1.1
- 输出需求设计文档（WHAT/WHY/HOW）。
### Task 1.2
- 定义最小改动实现计划与验收点。

## Stage 2：后端链路改造
### Task 2.1
- `AddSectionDelta` 增加 `appearance` 字段。
### Task 2.2
- archetype 层为 hero fact slot 下发 `appearance='hero_fact'`。
### Task 2.3
- 编译层在 Row/Column payload 透传 `appearance`。

## Stage 3：前端映射与样式
### Task 3.1
- Row/Column 读取 `appearance` 并映射到 DOM `data-appearance`。
### Task 3.2
- sample App.css 新增 `hero_fact` scoped 样式。

## Stage 4：测试与收尾
### Task 4.1
- 补充测试覆盖 AddSection appearance 与 compiled frame appearance。
### Task 4.2
- 验证 fact item 仍挂在 hero_fact_row 且 usageHint 保持 caption/body。
### Task 4.3
- 追加 progress.md 并分阶段中文提交。
