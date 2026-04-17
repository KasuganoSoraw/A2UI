# chat_ui_builder streaming prompt 主组件选择收敛设计

## 需求详情
定向优化 streaming 两阶段 prompt 的组件选择约束，重点减少“记录型数组误判为 facts”的情况。

## 澄清结果
- 本次仅改 prompt 文案与必要提示构造内容。
- 不改 runtime/service/stream_compiler 主流程。
- 规则必须泛化，不写死具体业务词。

## WHAT
1. 第一阶段（binding prompt）
- 收紧 facts 适用范围：仅少量概览/摘要字段。
- 放大 list/table 适用范围：数组对象记录优先 list/table。
- 增加优先级规则：
  - 单对象概览 -> facts
  - 多条对象记录 -> list/table
  - 浏览阅读 -> list
  - 对齐比较 -> table
- 显式提醒：不要把记录集合拍平成 facts。

2. 第二阶段（stream_event prompt）
- 对 facts 增加“克制展开”约束：只保留少量概览字段。
- 对 list 增加“title/detail 提炼”约束。
- 对 table 增加“关键列选择”约束，避免全字段机械铺列。
- 对 final summary 增加“概括而非重复明细”约束。

## WHY
- 组件选型是页面观感与信息结构的上游决定因素。
- 记录集合错误地映射到 facts 会导致可读性和结构感显著下降。
- 泛化规则可迁移到更多数据形态，避免领域词过拟合。

## HOW
- 仅修改 `binding_prompt.py` 和 `stream_event_prompt.py` 的系统提示词。
- 保持输出格式与事件协议不变。
