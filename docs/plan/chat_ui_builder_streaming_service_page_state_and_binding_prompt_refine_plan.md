# chat_ui_builder streaming 定向修正计划（page_state + binding prompt）

关联设计：`docs/chat_ui_builder_streaming_service_page_state_and_binding_prompt_refine_design.md`

## Stage 1：binding prompt 精修
### Task 1.1
精修 `streaming/prompt/binding_prompt.py`，补充 dataset 语义分组解释，保持 prompt 短小。

## Stage 2：service page_state 闭环
### Task 2.1
在 `streaming/service.py` 新增 `_apply_events_to_page_state(...)`。

### Task 2.2
在 `project_segment()` 中调用该函数，用 parsed events 更新 `page_state_summary`。

### Task 2.3
返回结果中显式包含最新 `page_state_summary`。

## Stage 3：自检与收尾
### Task 3.1
执行最小语法检查。

### Task 3.2
追加 `progress.md` 记录。

### Task 3.3
提交并创建 PR 记录。
