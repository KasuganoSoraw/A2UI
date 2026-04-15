# chat_ui_builder streaming json_extractor 定向修复计划

关联设计：`docs/chat_ui_builder_streaming_json_extractor_partial_container_fix_design.md`

## Stage 1：对象字段部分可见子容器保留修复
### Task 1.1
修改 `_parse_object()` 在 `value_result.complete=False` 时的写入策略。

### Task 1.2
确保仅对非空 dict/list 做保留，半截基础类型不写入。

## Stage 2：数组计数覆盖风险最小修复
### Task 2.1
检查 `_count_array_items_by_path()` 的同路径覆盖行为。

### Task 2.2
如存在覆盖风险，改为安全合并（取较大值）。

## Stage 3：自检与收尾
### Task 3.1
安装缺失依赖并执行语法检查。

### Task 3.2
执行 `json_extractor.py` 底部 4 个最小自检。

### Task 3.3
追加 `progress.md`、提交并创建 PR 记录。
