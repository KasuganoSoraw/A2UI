# chat_ui_builder hero_fact 容器级 appearance 改造设计

## 需求详情
为 hero 区 fact 整块容器增加容器级样式标记：`appearance='hero_fact'`。该标记必须挂在 fact slot 容器（`hero_fact_row`）层，不改 `usageHint` 语义，不加到单个 fact item。

## 澄清结果
- `usageHint` 继续只用于 `Text`（如 fact 的 label/value）。
- 新增字段 `appearance` 为容器级字段，先只用于 hero 的 fact slot。
- 不影响 details/summary/list/workflow 等其他 archetype 行为。

## WHAT
1. `models.py`：`AddSectionDelta` 增加 `appearance: str | None = None`。
2. `region_archetypes.py`：
   - `SlotSpec` 增加 `appearance`
   - `_base_region` 下发 `appearance`
   - `HeroArchetypeBuilder` 的 `fact` slot 指定 `appearance='hero_fact'`
3. `compiler.py`：在 Row/Column payload 输出时透传 `appearance` 字段。
4. 前端 Row/Column 渲染：读取 payload.appearance 并映射为 `data-appearance`。
5. `App.css`：只对 `.a2ui-row[data-appearance='hero_fact']` 增加样式。
6. 测试：验证 section/compiled frame/fact 挂载关系/usageHint 保持不变。

## WHY
- hero fact 是容器语义，不应复用 text usageHint。
- 用 `appearance` 可把“容器样式标记”与“文本语义标记”解耦，协议更清晰且可扩展。

## HOW
- 以最小增量扩展现有 AddSection->FrameCompiler->Row/Column 渲染链路。
- 保持现有 children/alignment/distribution 逻辑不变；无 appearance 的容器行为完全不变。
