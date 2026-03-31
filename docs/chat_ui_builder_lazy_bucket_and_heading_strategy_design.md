# Chat UI Builder 业务骨架懒创建与标题层级治理设计

## 需求详情
- 取消 `init_plan` 后预创建全量 role bucket 的策略，改为按需懒创建。
- 修复页面标题与 hero 文本重复导致双 h1 的问题。
- 保持 loading 阶段与 beginRendering 主流程不变，仅调整业务骨架生成策略。

## 澄清结果
- 不改 compiler/models/service 的协议定义。
- 不引入新模板或新 loading 机制。
- 仅在实际有 `add_region(role=...)` 使用时创建对应 bucket。
- 页面级标题保持唯一 h1，hero 区遇到 h1 时需去重/降级。

## WHAT
1. SkeletonCompiler 初始化仅建立最小硬骨架与 role->bucket 映射，不再创建空 bucket。
2. 在处理 `add_region` 时新增 `ensure bucket exists`：首次使用 role 时才创建 bucket。
3. 为 hero 文本新增标题冲突治理：
   - hero `h1` 与页面标题重叠时丢弃；
   - hero `h1` 非重叠时降级为 `h2`。
4. 新增测试覆盖：
   - init 后无空 bucket；
   - bucket 首次使用才创建；
   - hero h1 去重/降级。

## WHY
- 预创建空 bucket 会导致空容器、结构噪声和流式内容跳位。
- 懒创建能让业务结构由 planning 事件自然长出，更符合“单硬骨架 + 意图驱动”的架构。
- 页面唯一 h1 可改善视觉层级，减少标题语义重复。

## HOW
1. 调整 `skeleton_compiler.py`：
   - `_build_layout_scaffold` 不再调用全量 bucket 创建；
   - 新增 `_ensure_bucket_for_role` 并在 `_add_region` 前调用；
   - 新增 hero 标题规范化函数并在 text 事件落地时处理。
2. 追加 `test_region_archetypes.py` 用例验证懒创建与标题去重行为。
3. 语法检查与进度记录追加。
