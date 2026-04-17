# chat_ui_builder streaming block 编译链路开发计划

关联设计：`docs/chat_ui_builder_streaming_block_compiler_design.md`

## Stage 1：流式模型层落地（streaming/models.py）
### Task 1.1
创建 `streaming/models.py`，定义辅助模型：`TextLine`、`FactItem`、`ListItem`。

### Task 1.2
定义 11 个 stream event model，并补齐默认值、类型约束。

### Task 1.3
定义 `StreamEvent` discriminated union 与 `STREAM_EVENT_ADAPTER`，保证可直接解析事件 payload。

## Stage 2：流式编译器落地（streaming/stream_compiler.py）
### Task 2.1
实现 `StreamBlockState` 与 `StreamCompiler` 最小状态结构。

### Task 2.2
实现 `apply` 的直接 `isinstance` 分发，并接入各 `_handle_*` 方法。

### Task 2.3
实现 create/append 事件到 low-level delta 的编译逻辑，并通过 `FrameCompiler.apply` 返回 `A2UIFrame`。

### Task 2.4
实现 dataset 唯一绑定校验、block 存在性校验、summary block 的特殊规则。

## Stage 3：table 折中策略与最小自检
### Task 3.1
实现 table rows 缓存与 append 时全量 spec_json 刷新策略。

### Task 3.2
执行最小自检脚本，覆盖 text/facts/list/table/final summary 全链路。

### Task 3.3
更新 `progress.md` 追加本次任务记录。
