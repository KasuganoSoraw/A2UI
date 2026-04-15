# chat_ui_builder streaming 两阶段 prompt 与 service 最小串联计划

关联设计：`docs/chat_ui_builder_streaming_two_stage_prompt_service_design.md`

## Stage 1：两阶段 prompt 落地
### Task 1.1
创建 `streaming/prompt/binding_prompt.py`，放置第一阶段系统 prompt 与输入消息构造函数。

### Task 1.2
创建 `streaming/prompt/stream_event_prompt.py`，放置第二阶段系统 prompt 与输入消息构造函数。

### Task 1.3
创建 `streaming/prompt/__init__.py` 统一导出。

## Stage 2：最小 service 串联落地
### Task 2.1
创建 `streaming/service.py`，定义输入/决策最小模型与服务类。

### Task 2.2
实现第一阶段调用、解析、最小校验与 accepted decisions 过滤。

### Task 2.3
实现 binding_state_summary 更新规则（create 才新增 binding；append 必须命中已有 binding）。

### Task 2.4
实现第二阶段调用、NDJSON 事件解析、`StreamCompiler` 编译并返回 frames。

## Stage 3：自检与收尾
### Task 3.1
执行最小语法检查与最小运行示例（可注入假 LLM 调用）。

### Task 3.2
追加 `progress.md` 记录。

### Task 3.3
提交代码并创建 PR 记录。
