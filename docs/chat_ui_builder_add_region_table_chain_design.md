# Chat UI Builder add_region_table 全链路接入设计

## 需求详情
- 在现有 planning-delta -> SkeletonCompiler -> FrameCompiler 链路中新增 `add_region_table` 事件。
- 后端输出 `Table` 组件，并通过 `spec.path` 传递完整表格 spec。
- 当前阶段重点打通 schema / compiler / prompt / tests，不新增 role 或 layout。

## 澄清结果
- 不新增 `role=table`。
- 不新增 `AddSectionDelta.layout='Table'`。
- 不为所有 role 扩展专属 `table` slot。
- table 先复用通用正文落点（text slot 对应路径）。

## WHAT
1. `models.py` 新增：
   - `TableColumnSpec`
   - `AddRegionTableDelta`（planning 事件）
   - `AddTableDelta`（low-level 事件，使用 `spec_json`）
   - 并加入 `SkeletonDelta` 与 `Delta` 联合类型。
2. `skeleton_compiler.py` 新增 `add_region_table` 分支：
   - 路由到 `slot_name='text'`
   - 构造 table spec（title/columns/rows/row_key/striped/bordered）
   - `json.dumps(..., ensure_ascii=False)` 后生成 `AddTableDelta`。
3. `compiler.py` 新增 `AddTableDelta` 编译：
   - 先挂载 parent children
   - 输出 `Table` 组件，`spec.path=/content/<id>/spec`
   - dataModelUpdate 写入 `spec_json`。
4. `prompting.py` 补充 `add_region_table` contract 与使用规则说明。
5. 增加测试覆盖 schema 解析、skeleton 路由、frame 输出、与 text/fact 共存。

## WHY
- table 属于结构化内容块，不是页面职责或布局骨架。
- 复用 text 通用落点可以避免 slot 爆炸，保持当前架构简单稳定。
- spec 整体传递更适合复杂二维数据和后续前端自由实现。

## HOW
1. 以最小增量扩展 models 与 compiler/skeleton 分支。
2. 不触碰 role/layout 语义，仅新增 event 与低层组件生成能力。
3. 用单测保证从 planning event 到最终 frame 的关键链路可验证。
