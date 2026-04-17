# chat_ui_builder streaming ws frames 序列化修复设计

## 需求详情
定向修复 `samples/agent/adk/chat_ui_builder/app.py` 中 `/api/chat/ws/stream` 的成功回包序列化问题。

当前问题：`frames` 中元素可能是 `A2UIFrame` 对象，直接放入 `websocket.send_json(...)` 会触发
`TypeError: Object of type A2UIFrame is not JSON serializable`。

## 澄清结果
- 仅修一个 bug：`frames` 返回前先转为 JSON 可序列化 dict。
- 不改协议形状，仍返回整体 `frames` 数组。
- 不改 runtime/service/extractor。
- 不做其它重构。

## WHAT
- 在发送 `a2ui_frames` 前新增转换步骤：
  - 对每个 frame，若具备 `model_dump` 则调用 `model_dump(exclude_none=True)`。
  - 否则按原值透传（保持兼容 dict 场景）。
- 将回包里的 `frames` 字段替换为 `serializable_frames`。

## WHY
- `send_json` 只能处理 JSON 可序列化对象。
- `A2UIFrame` 是 Pydantic 模型对象，需先显式转 dict。
- 保持协议不变可避免影响前端联调。

## HOW
- 保留现有主链：`submit_snapshot -> processed 判断 -> a2ui_frames 回包`。
- 仅在回包前插入 list 转换，不改其它字段。
