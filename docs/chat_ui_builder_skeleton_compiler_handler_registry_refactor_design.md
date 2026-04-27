# chat_ui_builder SkeletonCompiler handler registry 重构设计

## 需求详情
对 `chat_ui_builder/skeleton_compiler.py` 进行最小不破坏重构：
- 将 `apply()` 从大 if/elif 改为 handler registry。
- 拆分 Plan/Region/Content 职责。
- 抽离 region 路由与 pending 逻辑到 Router。
- 保持 event 名、frame 结构、slot/parent 路由与既有行为不变。

## 澄清结果
1. 只改 `skeleton_compiler.py`（代码行为不变）。
2. 不改 FrameCompiler、前端、协议结构。
3. 保留日志、pending flush、flow 自动 workflow region、hero h1 去重等逻辑。

## WHAT
- 新增 `SkeletonRuntime` 承载运行时状态。
- 新增 `RegionRouter` 负责 apply/queue/flush。
- 新增 `PlanHandler`、`RegionHandler`、`ContentHandler`。
- `SkeletonCompiler` 仅负责组装 handler registry 与分发。
- 合并/下沉薄方法（布局 recipe/bucket order/slot mapping 等）到更合适的 handler/runtime 层。

## WHY
- 降低 `apply` 复杂度，提升可读性。
- 扩展新 delta 时只需新增 handler 映射，减少回归风险。
- 路由与状态职责清晰，便于调试 pending 行为。

## HOW
1. 先抽 runtime/router，保持旧字段命名与行为。
2. 将 init_plan/finalize 下沉到 PlanHandler；add_region 下沉到 RegionHandler；内容事件下沉到 ContentHandler。
3. 用 registry 分发，确保每个 delta 对应旧逻辑等价实现。
4. 通过语法检查验证重构后文件可加载。
