# Chat UI Builder 单列布局收敛设计

## 需求详情
将 `chat_ui_builder` 的布局编译逻辑彻底收敛为单列结构：移除双栏 scaffold、侧栏 bucket 与对应语义分支，保留 planning delta 主路径，确保所有 region 在单一主内容流中稳定纵向展示。同时强化 flow diagram 的“重组件独占 region”规则，避免与普通文本/事实/动作混排拥挤。

## 澄清结果
- 不是通过开关隐藏双栏逻辑，而是删除相关生成分支。
- 兼容历史输入：即使模型仍输出 `two_column` / `hero_plus_action_panel` 等 hint，也要归一化为单列，不报错。
- `supporting`、`actions` 等角色不可再走 side rail。
- flow diagram 必须独占 workflow region；若目标 region 非 workflow，则自动重定向到独立 workflow region。

## WHAT
1. `skeleton_compiler.py` 删除双栏 scaffold 和 side context：
   - 不再创建 `layout_split_row/layout_main_lane/layout_side_lane/layout_side_rail`。
   - `LayoutRecipe` 仅保留单列父容器。
   - `bucket_context` 去除 `side`，统一主列（可保留 footer，但本次进一步收敛为仅 main）。
2. 收敛 arrangement：
   - 去掉 side rail 相关特判，改为稳定的单列默认排布。
3. 增加 flow diagram 独占规则：
   - `add_region_flow_diagram` 仅进入 workflow region。
   - 非 workflow region 自动重定向到专用 workflow region（自动创建）。
4. 更新测试：
   - 不再断言 side rail/双栏行为。
   - 增加双栏 hint 归一化与 flow 独占行为测试。

## WHY
- 双栏逻辑引入大量额外 scaffold 与上下文分支，增加维护和排障成本。
- 单列更稳健，阅读流清晰，适合通用场景。
- flow diagram 属于重组件，独占 region 能显著改善可读性与交互稳定性。

## HOW
1. 重构 `LayoutRecipe` 与 `_build_layout_scaffold`，移除所有双栏节点常量与分支。
2. 收敛 `_arrangement_for`：去掉 `context == side` 分支，保留单列友好语义。
3. 在 `AddRegionFlowDiagramDelta` 处理链路加入 region 解析器：
   - 优先复用已有 workflow region；
   - 否则创建 `auto_workflow_region` 并将 flow 注入其 `flow` slot。
4. 更新 `tests/test_region_archetypes.py`，验证：
   - 不出现双栏节点；
   - actions/supporting 落到主列 bucket；
   - flow 自动独占 workflow region。
