# chat_ui_builder streaming 编译链路定向修正计划

关联设计：`docs/chat_ui_builder_streaming_block_compiler_review_fix_design.md`

## Stage 1：table append 最小修复
### Task 1.1
在 `models.py` 增加 `UpdateTableSpecDelta` low-level 模型并纳入 `Delta` union。

### Task 1.2
在 `compiler.py` 增加 `update_table_spec` 分支与最小处理逻辑，仅刷新已有 table spec 数据。

### Task 1.3
在 `streaming/stream_compiler.py` 的 table append 路径改为调用 `UpdateTableSpecDelta`。

## Stage 2：text/list/init 三项结构修复
### Task 2.1
为 text block 增加 `text_line_count` 状态，修复 append 编号连续性。

### Task 2.2
将 list block 改为“外层 Column + 内层 List host”，并修复 append parent 路由。

### Task 2.3
移除 `init_stream_surface` 默认过程型 summary，改为可选透传。

## Stage 3：收尾
### Task 3.1
执行最小自检（至少语法检查）。

### Task 3.2
追加 `progress.md` 记录。

### Task 3.3
提交代码并创建 PR 记录。
