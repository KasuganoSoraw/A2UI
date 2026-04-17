# chat_ui_builder streaming 定向修正设计（page_state 闭环 + binding prompt dataset 解释）

## 需求详情
在保持 streaming 两阶段方案不变的前提下，定向修复两点：
1. `StreamingPromptService` 每轮执行后闭环更新 `page_state_summary`
2. 第一阶段 binding prompt 更清楚解释 `dataset_id` 的语义分组含义

## 澄清结果
1. 不推翻现有两阶段流程，不改 non-streaming。
2. prompt 继续短小，不扩写成长篇。
3. page_state 第一版只维护 `surface_initialized` 与 `blocks(block_id, block_type)`。
4. page_state 更新来源以本轮 events 为主，不依赖前端 ack。

## WHAT
- 修改 `streaming/service.py`：
  - 新增 `_apply_events_to_page_state(...)`
  - 在 `project_segment()` 中对 parsed events 执行页面状态闭环更新
  - 返回值中新增（并显式返回）更新后的 `page_state_summary`
- 修改 `streaming/prompt/binding_prompt.py`：
  - 在保持简短的前提下，补充 `dataset_id=语义分组` 的关键说明

## WHY
- 若 page_state 不回灌，下一轮会缺少页面上下文，导致重复 init / 重复 create 风险。
- 第一阶段若不理解 dataset 的语义分组含义，会把 dataset 当随机编号，影响“沿用还是新建”的判断稳定性。

## HOW
1. `service.py`
   - 新增事件到 page_state 的最小映射：
     - `init_stream_surface` -> `surface_initialized=True`
     - `create_text_block` -> block_type `text`
     - `create_facts_block` -> block_type `facts`
     - `create_list_block` -> block_type `list`
     - `create_table_block` -> block_type `table`
     - `set_final_summary_text` -> block_type `text`
     - `set_final_summary_facts` -> block_type `facts`
   - block 去重策略：按 `block_id` 去重，已存在则不重复追加。
   - `project_segment()` 返回更新后的 `binding_state_summary` + `page_state_summary`。

2. `binding_prompt.py`
   - 用短句加入以下语义：
     - `dataset_id` 表示“语义上属于同一批内容”的分组
     - 同语义分组应沿用已有 dataset
     - 只有新语义分组才新建 dataset
     - 同一 dataset 应持续写入同一 block
     - `binding_state_summary.bindings` 用于告知已有语义分组
