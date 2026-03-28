# Chat UI Builder 单路径收敛设计（Planning Delta Only）

## 需求详情
本次仅针对 `samples/agent/adk/chat_ui_builder` demo 做收敛改造：删除 IntentPlan fallback 与 legacy line-by-line fallback，保留并强化 planning delta 主链，确保前端继续逐帧渐进式渲染。

## 澄清结果
- 不做 feature flag，不做“隐藏 fallback”。
- 直接清理 fallback 相关控制流、状态、解析逻辑与依赖。
- 保留 loading/error 运行时反馈，但其语义必须服务 planning 主链。
- 不扩展为架构重写；仅做收敛与清理。

## WHAT
1. `service.py` 收敛为单一路径：
   - LLM stream -> `PlanningDeltaStreamParser` -> `SkeletonCompiler` -> `FrameCompiler` -> A2UI frames。
   - 移除 IntentPlan parse + design lint + layout policy + intent compiler 路径。
   - 移除 legacy line-by-line fallback 解析与渲染路径。
2. 清理不再使用的模块依赖与文档描述。
3. 增加/更新测试，验证：
   - planning delta 可持续产出帧（渐进式）。
   - 无 planning delta 时按单路径策略返回错误 surface，不再 fallback。

## WHY
- 当前真实主链已经是 planning delta 流式渲染；fallback 不再是主要价值路径。
- fallback 增加 service 控制流复杂度、日志噪音、排障分叉和维护成本。
- 单路径可提升可读性、可测试性和行为可预期性，符合 demo 当前目标。

## HOW
1. 精简 `ChatUIService`：
   - 去掉 IntentPlan/legacy 分支、对应 helper 和状态变量。
   - 去掉 `_planning_wait_frames` 这类仅用于 fallback 过渡的逻辑。
   - 保留 loading 与 error frame，改为 planning-only 语义。
2. 删除 fallback-only 模块文件（若无其他引用）：
   - `intent_plan.py`
   - `layout_ir.py`
   - `layout_policy.py`
   - `design_lint.py`
   - `intent_compiler.py`
3. 更新 README 中架构说明，明确 planning-only 主链。
4. 补充服务层测试（mock `acompletion` 流）：
   - 验证流式输入逐 chunk 输出帧。
   - 验证仅返回非 planning 文本时产出 error frame。
