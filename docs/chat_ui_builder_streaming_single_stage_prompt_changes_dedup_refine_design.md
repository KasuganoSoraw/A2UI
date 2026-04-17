# chat_ui_builder 单阶段 streaming prompt changes 去重收敛设计

## 需求详情
定向优化单阶段 streaming prompt，减少重复展示，明确模型本轮只应响应 `changes` 对应新增，而不是重述整个 `visible_snapshot`。

## 澄清结果
- 仅改 prompt 文案与必要 message builder 文案。
- 不改 runtime/service/compiler/ws/event schema。
- 规则保持泛化：新增 vs 历史、复用已有承载位置、语义去重。

## WHAT
- 强化 changes 主任务：新增内容优先，snapshot 仅作上下文。
- 加入去重规则：
  - 同一新增只保留一个主表达
  - 避免重复 create 语义重叠 block
  - 概览与明细不互相重复
- 保持并合并小步增量规则，避免 prompt 膨胀。

## WHY
- 重复展示本质上是“本轮任务边界不清”的问题。
- 通过 prompt 明确“本轮新增响应 + 去重约束”，可减少重复卡片与重复摘要。

## HOW
- 仅修改 `stream_event_prompt.py` 的规则段与 builder 注释。
- 合并重复表述，保留高密度规则集合。
