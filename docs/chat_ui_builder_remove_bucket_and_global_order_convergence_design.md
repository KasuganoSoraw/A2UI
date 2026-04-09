# chat_ui_builder 去 bucket + 去全局 order 结构收敛设计

## 需求详情
目标：
- 移除 Skeleton 侧 role->bucket 中间层，region 直接挂页面主父容器。
- 移除 FrameCompiler 跨 region 全局排序，页面级顺序保持 LLM 流式输出顺序。
- 保留 region 内部局部顺序（header/body/fact/action）。

## 澄清结果
1. 不改 role/archetype/slot 语义。
2. 不改 A2UI 协议结构和前端消费协议。
3. 仅清理 bucket 和全局 order 机制，不做额外语义调整。

## WHAT
- `skeleton_compiler.py`：
  - 删除 BUCKET_ORDER、role_slots_recipe、bucket_order。
  - 删除 runtime 的 role_slots/created_buckets。
  - 删除 RegionHandler 的 `_slot_for_role`/`_ensure_bucket_for_role`。
  - region 构建时 `slot_parent` 固定页面主父容器（`root`）。
- `compiler.py`：
  - 去掉全局 child 排序状态（child_order/insertion_counter）。
  - 页面主容器禁用 order 排序，按 append 顺序渲染。
  - 非页面主容器仍可按局部 order 保持稳定结构。
- `tests`：移除 bucket 相关断言，调整 hero h1 过滤预期。

## WHY
- 单列页面不需要 bucket 中间层，简化结构与调试路径。
- 取消全局 order 可避免后生成 region 被插入前面，保证流式顺序可信。

## HOW
1. 先改 skeleton，确保 region 直接落主容器。
2. 再改 compiler 排序策略：页面级 append-only，局部容器可按 order。
3. 更新测试并执行最小检查。
