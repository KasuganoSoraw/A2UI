# chat_ui_builder table richer cell 普通 dict 化与序列化修复设计

## 需求详情
本次目标是在保持 table 事件与 frame 结构不变的前提下，修复 richer cell 使用 `TableCellSpec` 导致的 JSON 序列化报错问题（`TableCellSpec is not JSON serializable`）。

关键约束：
- cell 仅支持两种形态：primitive 或普通 dict `{value, visual_weight?}`。
- 不引入 `semantic`。
- 不允许模型输出 CSS class、颜色名或样式字符串。
- 后端只做轻量校验并原样透传。

## 澄清结果
1. `add_region_table` / `add_table` 事件名保持不变。
2. `Table.spec.path` 与 `/content/<id>/spec` 写入结构保持不变。
3. 不通过“把 Pydantic 子模型 dump 成 dict”修复，而是彻底避免把 cell 构造成 Pydantic 对象。
4. 前端继续固定 class 映射，不依赖模型样式字符串。

## WHAT
### 后端
- 删除 `TableCellSpec`。
- 将 `rows` 回退为宽松类型（普通 dict），通过 validator 做轻量校验：
  - primitive 允许；
  - dict 必须有 `value`，`visual_weight` 可选且必须是 1..5 整数；
  - dict 不允许额外 key；
  - 非法结构拒绝。
- skeleton 编译路径保持不变，`rows` 原样进入 `spec_json`。

### 前端
- 保持 primitive/object 渲染能力。
- 将权重 class 逻辑显式收敛为 `getCellWeightClass`，只允许映射 1..5。

### 测试
- 后端新增/调整 schema 测试（primitive、object、缺 value、越界）。
- 验证 skeleton 输出 richer cell 仍是普通 dict 且可 JSON 序列化。
- 前端验证 primitive/object 渲染与 class 映射。

## WHY
- 当前报错根因是 `json.dumps(table_spec)` 不能直接序列化自定义 Pydantic 子对象。
- 将 cell 保持为 primitive/普通 dict 可消除序列化风险，并满足“轻校验 + 原样透传”目标。

## HOW
1. 在 `AddRegionTableDelta` 上实现 rows validator，返回值保持原结构（不升格为模型对象）。
2. 不改 `skeleton_compiler.py` table 路径，继续 `json.dumps(..., ensure_ascii=False)`。
3. 前端用固定 `weight -> class` 映射渲染强调样式。
