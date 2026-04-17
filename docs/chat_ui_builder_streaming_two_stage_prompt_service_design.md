# chat_ui_builder streaming 两阶段 prompt 与最小 service 串联设计

## 需求详情
在现有 streaming 编译链路基础上，新增最小可用的两阶段 prompt + service 串联能力：
1. 第一阶段：绑定判别 prompt（输出 decisions）
2. 第二阶段：事件生成 prompt（输出 NDJSON 事件）
3. 新增 `streaming/service.py` 串联两阶段并调用 `StreamCompiler`

## 澄清结果
1. 不重构 non-streaming 链路，不修改旧 `prompting.py`。
2. prompt 保持短、直接、可操作。
3. service 采用最小实现，结构清楚即可，不引入复杂框架。
4. 允许复用现有 `litellm.acompletion` 调用方式，也支持注入自定义调用函数便于后续接入。

## WHAT
- 新增 `streaming/prompt/binding_prompt.py`：第一阶段系统 prompt + 消息构造。
- 新增 `streaming/prompt/stream_event_prompt.py`：第二阶段系统 prompt + 消息构造。
- 新增 `streaming/prompt/__init__.py`：统一导出。
- 新增 `streaming/service.py`：
  - 调第一阶段模型
  - 解析并校验 decisions
  - 根据 accepted decisions 更新 `binding_state_summary`
  - 调第二阶段模型
  - 解析 NDJSON 事件
  - 投喂 `StreamCompiler` 并返回 frames

## WHY
- 第一阶段与第二阶段职责不同，拆分后可减少模型负担并提高稳定性。
- service 串联后，工程层只需提供统一输入结构，不必直接处理展示语义。
- 最小 service 先打通链路，可在后续逐步替换具体模型调用实现。

## HOW
1. prompt 文件直接采用用户给定草案，保持短 prompt 风格，只做必要代码化封装。
2. `service.py` 中定义最小结构模型：
   - `BindingDecision` / `BindingResult`
   - `StreamingProjectionInput`
3. 第一阶段：
   - 使用 binding prompt 生成 messages
   - 调 LLM（非流式）拿到文本
   - 解析为 JSON 并最小校验
4. accepted decisions 更新规则：
   - `should_create_new_block=true`：通过最小校验后新增 binding
   - `should_create_new_block=false`：必须已存在同 `dataset_id + block_id` 绑定
5. 第二阶段：
   - 使用 stream event prompt 生成 messages
   - 调 LLM（非流式）拿到 NDJSON
   - 按行解析为 `StreamEvent`
   - 逐条调用 `StreamCompiler.apply` 汇总 frames
6. 保留必要中文注释，重点解释：
   - 为什么要做 accepted decisions 过滤
   - 为什么只在通过最小校验后写入 binding_state_summary
