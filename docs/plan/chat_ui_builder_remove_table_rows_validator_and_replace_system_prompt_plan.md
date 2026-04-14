# chat_ui_builder 移除 rows validator + 替换 SYSTEM_PROMPT 计划

## Stage 1：设计与边界确认
### Task 1.1
- 记录需求与边界：仅改 `models.py` 与 `prompting.py`。

## Stage 2：后端代码修改
### Task 2.1
- 删除 `AddRegionTableDelta.validate_rows` 方法。
### Task 2.2
- 将 `SYSTEM_PROMPT` 替换为用户提供版本。

## Stage 3：最小验证与收尾
### Task 3.1
- 执行最小检查（如语法检查）。
### Task 3.2
- 追加 progress 记录并提交。
