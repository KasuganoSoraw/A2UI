# 开发计划：日志搜索展示模板全链路接入

关联设计：`docs/chat_ui_builder_log_template_design.md`

## Stage 1：设计与计划
### Task 1.1
梳理当前输入、prompt、service、前端请求链路。

### Task 1.2
完成日志模板设计与开发计划文档。

## Stage 2：后端模板实现
### Task 2.1
新增日志模板生成模块并实现事件归一化与 planning delta 输出。

### Task 2.2
在 service 层接入模板判定与直编译流式输出。

### Task 2.3
更新 prompt 与 README 的日志模板说明。

## Stage 3：前端接入与验证
### Task 3.1
更新前端 demo 输入与请求体，支持 source_data + user_query。

### Task 3.2
新增/更新测试覆盖模板链路和约束行为。

### Task 3.3
运行检查、追加 progress、分阶段提交并创建 PR 信息。
