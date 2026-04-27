# chat_ui_builder streaming block 编译链路设计

## 需求详情
在 `chat_ui_builder/` 下新增一条**独立于 non-streaming SkeletonCompiler** 的 streaming 编译链路最小实现。
本次只交付：
- `streaming/models.py`
- `streaming/stream_compiler.py`

并要求该链路尽量复用既有 `FrameCompiler`，不改造现有 non-streaming 逻辑。

## 澄清结果
1. streaming 链路不复用 `SkeletonCompiler` 的 region/archetype 模型。
2. streaming 页面固定为单画布竖排增长，block 按创建顺序挂载。
3. 第一版仅支持 text/facts/list/table/final summary（text/facts）。
4. chart/pie/mermaid 暂不实现。
5. append-only 优先，避免 replace 引发抖动。
6. table append 采用“缓存全量 rows + 低频整体刷新 spec_json”折中。

## WHAT
新增 streaming 专用模型和编译器：
- 模型层定义 stream event、辅助数据结构、discriminated union adapter。
- 编译层接收 `StreamEvent`，产出 low-level delta 并通过 `FrameCompiler.apply(...)` 输出 `A2UIFrame`。

## WHY
- non-streaming 的 page-level planning 抽象（role/region/archetype）与 streaming 的增量 block-first 目标不一致。
- 若继续复用旧 SkeletonCompiler，会引入不必要的布局语义与维护负担。
- 复用 FrameCompiler 可最大化兼容现有 low-level 到 A2UI frame 的翻译能力，降低改动风险。

## HOW
### 1. `streaming/models.py`
- 定义 `TextLine`、`FactItem`、`ListItem`。
- 定义 11 个 stream event：
  - `InitStreamSurfaceEvent`
  - `CreateTextBlockEvent` / `AppendTextLinesEvent`
  - `CreateFactsBlockEvent` / `AppendFactsEvent`
  - `CreateListBlockEvent` / `AppendListItemsEvent`
  - `CreateTableBlockEvent` / `AppendTableRowsEvent`
  - `SetFinalSummaryTextEvent` / `SetFinalSummaryFactsEvent`
- 复用现有 `models.TableColumnSpec`。
- 提供 `StreamEvent` union + `STREAM_EVENT_ADAPTER`。

### 2. `streaming/stream_compiler.py`
- 定义 `StreamBlockState`（block_id/dataset_id/block_type/title）。
- 定义 `StreamCompiler`，维护最小状态：
  - `surface_initialized`
  - `surface_id`
  - `blocks`
  - `dataset_to_block`
  - `block_order`
  - `table_data_cache`（columns/rows/title/table_component_id）
- `apply` 采用直接 `isinstance` 分发。
- 各事件转换为 low-level delta（`InitSurfaceDelta`、`AddSectionDelta`、`AddTextDelta`、`AddKeyValueDelta`、`AppendListItemDelta`、`AddTableDelta`），再统一交给 `FrameCompiler`。
- 数据约束：
  - create 同名 block 报错。
  - append 到不存在 block 报错。
  - 一个 dataset 只能绑定一个 block。
  - summary block 不参与 dataset 绑定。

### 3. table append 折中策略
- 因第一版无 `AppendTableRowsDelta`，且不改造 FrameCompiler：
  1. StreamCompiler 缓存 table rows；
  2. append 时重建完整 spec_json；
  3. 通过 `AddTableDelta` 对同一 table component id 重新提交，触发 DataModel 更新。
- 该策略实现简单、侵入小，后续可平滑替换为更细粒度增量协议。

### 4. 最小自检
编写一段命令行脚本（一次性 python 片段）验证：
- init surface
- create/append text
- create/append facts
- create/append list
- create/append table
- set final summary text/facts
