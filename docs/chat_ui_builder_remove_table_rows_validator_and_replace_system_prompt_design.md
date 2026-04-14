# chat_ui_builder 移除 table rows validator 并替换 SYSTEM_PROMPT 设计

## 需求详情
用户要求两项明确改动：
1. 删除 `AddRegionTableDelta` 上的 `@field_validator("rows")` 整段实现。
2. 将 `prompting.py` 内 `SYSTEM_PROMPT` 替换为用户给定的完整文本。

并要求：不要修改其他位置（仅限必要文件）。

## 澄清结果
- 本次只改 `models.py` 和 `prompting.py` 的指定内容。
- 不改事件名、frame 结构与其他组件逻辑。
- 由于用户提供的是完整 prompt 文本，按原文替换，不做语义重写。

## WHAT
- 在 `models.py` 删除 `validate_rows` 校验器。
- 在 `prompting.py` 用用户提供内容完整替换 `SYSTEM_PROMPT`。

## WHY
- 直接响应用户对代码实现与 prompt 约束的强制要求，避免额外解释层导致偏差。

## HOW
1. 精确删除 validator 代码块，保留其余结构不变。
2. 精确替换 `SYSTEM_PROMPT` 多行字符串。
3. 最小化验证（文件级检查/语法检查）。
