# chat_ui_builder 单路径收敛设计

## 需求详情
用户要求将 `samples/agent/adk/chat_ui_builder` 收敛为单一路径：仅保留 planning delta 流式链路，移除 IntentPlan fallback 与 legacy line-by-line fallback，确保渐进式渲染仍可用。

## 澄清结果
- 本次不是 feature flag 隐藏，而是实际删除 fallback 逻辑。
- 保留 loading/error 运行时反馈，但反馈服务于 planning 主链。
- 不做大规模重写，优先收敛与清理。

## WHAT
1. 简化 `service.py` 控制流为：LLM stream -> parser -> skeleton compiler -> frames。
2. 删除 IntentPlan fallback 与 legacy fallback 相关函数、状态、解析逻辑。
3. 删除仅服务 fallback 的后端模块文件（若无主链依赖）。
4. 增补测试，验证：
   - planning delta 可持续产出帧；
   - 非 planning 输出触发错误面板，不再进入 fallback。

## WHY
- 当前真实主路径已经是 planning delta，fallback 仅增加复杂度与维护负担。
- 多分支控制流增加调试和测试成本。
- 单路径更符合 demo 目标：突出渐进式生成与渲染。

## HOW
- 重写 `ChatUIService.stream_frames` 后半段逻辑，移除 Intent/legacy 分支。
- 新增 planning-only 错误提示帧函数（或复用 error 帧）。
- 清理 import 与未使用 helper。
- 删除 `design_lint.py`、`intent_compiler.py`、`intent_plan.py`、`layout_ir.py`、`layout_policy.py`。
- 新增 `tests/test_service_stream.py` 使用 monkeypatch 模拟 litellm 流输出，覆盖成功和失败路径。
