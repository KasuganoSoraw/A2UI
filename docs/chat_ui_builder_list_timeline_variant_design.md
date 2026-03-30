# Chat UI Builder：list 的 timeline 展示变体设计

## 需求详情
在不新增 role 的前提下，为 `role=list` 引入 `presentation.variant`，当前支持：
- `standard`（默认）
- `timeline`

当 `role=list + presentation.variant=timeline` 时，后端编译输出应使用 `Timeline` / `TimelineItem` 组件名；`TimelineItem` 内部继续复用 `Card/Column/Text`。

## 澄清结果
- 不新增 `timeline` role。
- 不实现前端 timeline 渲染，仅输出后端 A2UI frames。
- 保持 `append_region_list_item` 与 usage_hint 扩展能力。

## WHAT
1. contract/prompt：`add_region` 新增 `presentation.variant` 说明；补充 role×presentation 最小矩阵。
2. schema：新增 `RegionPresentationConfig` 并挂到 `AddRegionDelta.presentation`。
3. skeleton/archetype：list region 在 timeline 变体下创建 `Timeline` 容器。
4. compiler：
   - standard list 保持原行为；
   - timeline list 输出 `Timeline` host + `TimelineItem` item，item 内仍是 Card/Text。
5. tests：覆盖 standard/timeline 两种 list 行为与 usage_hint 优先级。

## WHY
- 将 timeline 作为 list 的展示变体比新增 role 更通用、抽象更干净。
- 先打通后端编译链，前端组件可后续增量实现。

## HOW
1. `models.py` 扩展 `AddRegionDelta.presentation` 与 `AddSectionDelta.layout='Timeline'`。
2. `prompting.py` 增加 presentation contract 和使用规则。
3. `region_archetypes.py` 在 list builder 按 variant 选择 `List` / `Timeline`。
4. `skeleton_compiler.py` 将 presentation_variant 传入 archetype context。
5. `compiler.py` 根据 parent 容器类型选择 `Card` 或 `TimelineItem` 包装。
6. 测试中断言 frame component 包含 `Timeline` / `TimelineItem`。
