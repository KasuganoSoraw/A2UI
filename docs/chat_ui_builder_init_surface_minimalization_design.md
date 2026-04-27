# chat_ui_builder 非流式加载页移除与 FrameCompiler 初始化收敛设计

## 需求详情
本次需求要求 `samples/agent/adk/chat_ui_builder` 完成两项架构收敛：
1. `ChatUIService` 不再在模型首个 planning delta 到来前预制 loading 页面。
2. `FrameCompiler._init_surface` 从“叙事化页面预制”收敛为“最小 surface 初始化”。

## 澄清结果
- 仅调整非流式主线（`service.py` + `compiler.py`），不改 planning 主链（`SkeletonCompiler` 及 `add_region/finalize_plan` 语义不变）。
- loading 体验由前端负责，后端请求开始阶段不输出任何 A2UI frame。
- `init_surface` 阶段输出严格限制为：
  - `beginRendering`
  - 仅包含 root `Column` 的 `surfaceUpdate`
- 不再在 `init_surface` 阶段注入 title/summary，也不输出 `dataModelUpdate('/', ...)`。

## WHAT（做什么）
1. 删除 `ChatUIService._loading_frames` 及 `stream_frames` 中对该方法的调用和帧输出。
2. 重写 `FrameCompiler._init_surface`：
   - 仅初始化 runtime 状态（containers/used_ids/aliases/local_child_order/auto_sections/page_parent_id）
   - 仅输出 begin + root surfaceUpdate
3. 更新受影响测试，改为验证：
   - 开始阶段不再依赖 loading 预制标题
   - planning delta 到来后仍能正常渲染业务组件

## WHY（为什么）
- 避免把“加载态 UI”和“业务页面结构”混为一体，消除后端“伪页面”预制。
- 保证页面结构完全由 planning delta 决定，恢复模型在 `init_plan` 阶段的结构主导权。
- 支持“可无标题”的数据页目标：后端默认不再强行注入标题/摘要组件。

## HOW（如何做）
- 在 `service.py` 删除 loading frames 相关代码路径，使请求启动后直接等待 LLM delta。
- 在 `compiler.py` 的 `_init_surface` 中：
  - 重置并初始化最小必要状态。
  - 构建 root `Column(children=[])` 的单组件 surface 更新。
  - 设置 `page_parent_id = root`，确保后续 region 直接挂到 root，由 planning 渐进生长页面。
- 回归测试聚焦行为约束而非旧 title path：
  - 验证输出中出现 `beginRendering` 与业务组件。
  - 验证错误兜底仍可输出错误文案。
