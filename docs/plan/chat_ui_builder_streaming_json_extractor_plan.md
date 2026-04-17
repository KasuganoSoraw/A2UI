# chat_ui_builder streaming json_extractor 开发计划

关联设计：`docs/chat_ui_builder_streaming_json_extractor_design.md`

## Stage 1：提取器主体实现
### Task 1.1
新增 `streaming/json_extractor.py`，定义 `JsonExtractionResult` 与 `JsonExtractor.extract(...)`。

### Task 1.2
实现保守结构提取逻辑，支持对象根节点与数组“前若干完整元素可见”。

## Stage 2：changes 计算实现
### Task 2.1
实现 `_collect_paths`，生成 JSON 路径集合。

### Task 2.2
实现 `_count_array_items_by_path`，统计数组路径元素数量。

### Task 2.3
实现 `_build_changes`，输出 `new_paths/new_array_items/is_stream_end`。

## Stage 3：最小自检与收尾
### Task 3.1
添加最小自检示例（4 个用例）。

### Task 3.2
执行语法检查与最小运行自检。

### Task 3.3
追加 `progress.md`、提交并创建 PR 记录。
