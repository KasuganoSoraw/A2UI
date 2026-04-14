# Chat UI Builder 去场景特化与通用语义增强设计

## 需求详情
本次重构目标是让 A2UI 回到通用展示框架：移除日志场景 one-shot 与场景直出模板路径，保留通用 role+archetype+原子组件链路；同时新增通用 `warning` usage_hint 并打通后端 schema 与前端样式消费。

## 澄清结果
- 优先删除 `log_template.py` 及其 service 调用链，不做“保留文件但绕过”。
- prompt 仅保留框架级约束：展示层、source_data 边界、user_query 辅助、无动作项不生成 actions。
- `warning` 是通用文本展示语义，不绑定日志场景。

## WHAT
1. 删除日志特化路径：
   - 删除 `log_template.py`
   - 删除 service 中日志场景直出分支
   - 删除依赖该路径的测试
2. 清理通用 prompt：
   - 去掉日志 one-shot/日志模板强引导
   - 保留展示层约束与通用 contract
3. 接入 `warning` usage_hint：
   - `models.py` 中 `AddRegionTextDelta/AddTextDelta` 枚举新增 `warning`
   - `prompting.py` contract 同步新增
   - 前端样式增加 warning 显示规则
4. 保持主链不变：`source_data/user_query -> planning delta -> skeleton/archetype -> frame -> frontend`

## WHY
- 场景模板直出会诱导框架向“每个场景一个模板文件”扩散，违背通用框架方向。
- `warning` 能提升通用展示表达力，但不改变“只展示不编造”的职责边界。

## HOW
1. 代码清理：删除日志模板模块并恢复纯通用 service 主链。
2. prompt 重写：移除日志示例与日志优先规则。
3. schema 与样式：加入 `warning` usage_hint 的后端类型与前端视觉映射。
4. 测试调整：删除日志模板直出测试，补充 `warning` 枚举/渲染链路相关断言。
