# chat_ui_builder table cell visual_weight 升级设计

## 需求详情
在不改变 `add_region_table` 事件名、`Table.spec.path` 与 A2UI frame 结构的前提下，将 table cell 从仅 primitive 扩展为：
- primitive（保持兼容）
- `{value, visual_weight?}`

其中：
- `visual_weight` 可选，若提供必须是 `1..5`
- 不引入 `semantic`
- 不允许模型输出 CSS class/颜色名/样式字符串
- 后端负责接收/校验/透传
- 前端负责根据 `visual_weight` 映射样式类

## 澄清结果
1. 事件结构保持不变：仍使用 `add_region_table` -> `add_table`。
2. 编译链保持不变：`spec_json` 继续经 `json.dumps(..., ensure_ascii=False)` 写入 `/content/<id>/spec`。
3. 后端只做合法性校验，不做任何样式决策，不将对象压平。
4. 前端按单元格粒度做样式增强，文本展示仍来自 `value`。

## WHAT
### 后端
- 在 `models.py` 新增 `TableCellSpec`，并让 `rows` 支持 primitive 与 `TableCellSpec`。
- 对 `visual_weight` 增加范围约束（1~5）。
- 更新 `prompting.py` table contract 与规则说明（仅文案，不改 event 名）。
- 保持 `skeleton_compiler.py` 现有 table 编译路径，仅验证“对象 cell 原样透传”。
- 新增/更新测试：schema 接受 primitive/object；超范围拒绝；spec_json 透传。

### 前端
- `Table.tsx` 新增 cell union 类型与判定逻辑，支持 primitive/object。
- 新增 `renderCell` 辅助函数：显示 `value`，并将 `visual_weight` 映射到 `.a2ui-table-cell-weight-1..5`。
- `App.css` 新增最小必要样式，作用域限定在 table 组件。
- 新增前端组件测试覆盖 primitive/object/class 映射。

## WHY
- 程度/等级类字段需要轻量视觉层级，但不应让模型输出样式细节，避免协议污染。
- 将展示强度抽象为数值（1..5）有利于后续跨主题/跨端一致渲染。
- 兼容旧 primitive 格式，降低存量数据迁移成本。

## HOW
1. 使用 pydantic 模型表达 table cell union，并在 `visual_weight` 字段上添加约束。
2. skeleton compiler 保持 `rows` 原样写入 `table_spec`，不新增样式字段。
3. 前端将 `visual_weight` 解释为 class，不改变 cell 文本内容。
4. 测试覆盖 schema、编译透传、前端渲染与 class 映射。
