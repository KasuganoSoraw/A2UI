# chat_ui_builder streaming 编译链路定向修正设计

## 需求详情
在当前 streaming 方向不变（block-first / dataset-first / incremental-first）的前提下，
对现有实现做 4 个定向修正：

1. `append_table_rows` 不能重复创建 table，需要刷新同一个 table 数据。
2. `append_text_lines` 不能重复从 `line_0` 编号。
3. `create_list_block` 不能把标题和 list items 混在同一个 List 容器。
4. `init_stream_surface` 不应默认写过程型 summary。

## 澄清结果
1. 不推翻现有 streaming 方案，不改 non-streaming 主链路。
2. 允许对 `compiler.py` 做极小改动，仅补 table 数据刷新能力。
3. 保持命名直白，避免复杂抽象框架。
4. 继续保留中文注释，解释“为什么这么改”。

## WHAT
- 新增 low-level delta：`UpdateTableSpecDelta`，用于刷新已存在 table 的 spec 数据。
- 在 `FrameCompiler` 增加该 delta 的最小处理逻辑，避免重复创建 table 组件。
- 在 `StreamCompiler` 增加 text 行计数状态并修复 list host 结构。
- `init_stream_surface` 去掉默认过程型 summary。

## WHY
- 直接复用 `AddTableDelta` 做 append rows 会触发 `_register_id()` + `_append_child()`，从而生成新 table 组件，不符合“刷新同一个表”的需求。
- 文本行编号若每次从 0 开始，会依赖底层自动改名，导致 id 语义不稳定。
- List 容器应只承载列表项，标题应由外层 block 承载，结构上更贴近 non-streaming 实践。
- 过程型 summary 会混入最终页面内容，不符合“只展示会留下来的内容”的原则。

## HOW
### 1) table append 修复
- 在 `models.py` 新增 `UpdateTableSpecDelta(event='update_table_spec')`。
- `FrameCompiler.apply` 增加该类型分支。
- 新增 `_update_table_spec`：
  - 通过 alias 解析到已有 table 组件 id；
  - 仅写 `/content/{table_id}/spec` 数据；
  - 不创建组件，不追加 child。
- `StreamCompiler._handle_append_table_rows` 改为发 `UpdateTableSpecDelta`。

### 2) text 追加编号修复
- `StreamBlockState` 增加 `text_line_count`。
- create 写入首批文本时从 0 开始并更新计数。
- append 从当前计数继续编号，并更新计数。

### 3) list 标题承载结构修复
- `create_list_block` 改为：
  - 外层 `block_id` 使用 `Column`；
  - 标题挂外层；
  - 新建 `block_id__list_host`（`List`）承载条目。
- `append_list_items` 改为写入 `list_host_id`。
- `StreamBlockState` 增加 `list_host_id` 字段保存该路由。

### 4) init summary 修复
- `InitStreamSurfaceEvent` 增加可选 `summary` 字段。
- `StreamCompiler` 初始化时不再注入默认过程型说明，直接透传 `event.summary`（默认 `None`）。

### 5) 最小自检
- 语法检查：`py_compile` 覆盖 models/compiler/streaming。
- 运行最小示例（若环境缺依赖则记录 warning）。
