# chat_ui_builder 单阶段 streaming prompt 增量策略收敛设计

## 需求详情
定向优化单阶段 streaming prompt，使模型更早输出首个可显示事件，并控制单个事件负载，减少“一次性 append 过多内容”。

## 澄清结果
- 本次只改 prompt 与必要的 prompt 构造文案。
- 不改 runtime/service/compiler/ws 协议。
- 规则必须泛化，不能写死业务词。

## WHAT
- 在单阶段 prompt 中强化统一增量策略：
  1. 先显示后补全（不要等大而全）。
  2. 单事件小负载（避免一次 append 太多）。
  3. 对 text/facts/list/table/final summary 全组件统一生效。
  4. 围绕 changes 组织事件，避免重述完整 snapshot。
  5. 组件选择兼顾“是否适合渐进生长”。
- 压缩重复表达，保持 prompt 高密度且不膨胀。

## WHY
- 仅工程层流式并不足以带来体感流式；模型输出粒度是关键。
- 统一规则可避免只优化 list 而忽略 text/facts/table。
- 泛化规则更稳定，不受具体行业语义影响。

## HOW
- 只修改 `stream_event_prompt.py` 的系统提示词。
- 强化“avoid”风格限制项（一次 append 过多、过重 create、summary 重复明细）。
- 保留事件 schema 与输出格式不变。
