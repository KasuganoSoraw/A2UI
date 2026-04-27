# chat_ui_builder streaming runtime 设计文档

## 需求详情
在 `chat_ui_builder/streaming/runtime.py` 新增一个独立的 runtime 层，专门负责 session 级串行调度与调用时机控制。

该层只负责：
1. 按 `session_id` 维护会话状态。
2. 保证同 session 强串行处理。
3. 决定何时调用 `JsonExtractor.extract(...)`。
4. 决定何时调用 `StreamingPromptService.project_segment(...)`。

该层不负责 HTTP/WebSocket 接口、不负责 prompt 细节、不负责语义判断和组件选择。

## 澄清结果
- runtime 采用“最新累计 raw_text 覆盖”策略，不做 FIFO 小片段队列。
- 同一 session 在任意时刻最多只有一轮 processing。
- 首屏/后续触发规则由工程规则控制，不交给模型。
- 本次只新增 `runtime.py` 代码文件，不修改 `app.py`。

## WHAT
新增：
- `StreamingSessionState`：存放 session 运行态。
- `StreamingRuntime`：提供 `submit_snapshot(...)` 与内部 `_drain_session(...)`。
- 触发判断辅助方法：
  - `_should_trigger_first_render(...)`
  - `_should_trigger_incremental_render(...)`
  - `_has_meaningful_changes(...)`

核心流程：
1. `submit_snapshot` 更新该 session 的 `latest_raw_text`、`is_stream_end`、`has_pending_update`。
2. 若该 session 正在 processing，则立即返回 `processed=false`。
3. 若未 processing，则启动 `_drain_session` 循环。
4. 每轮 drain 使用“当前最新 raw_text”执行 extract，按阈值决定是否调用 `project_segment`。
5. 调用成功后回写 state，并在有新更新时继续下一轮。

## WHY
- 将“调度/节流/串行/触发时机”从 prompt/service 逻辑中剥离，降低耦合，提高可读性与可维护性。
- 采用最新快照覆盖可避免模型慢时的过期分段处理，确保每轮模型看到的是最新累计 JSON。
- 将首屏与后续触发规则固化在工程层，避免把调用时机不稳定地交给模型。

## HOW
### 数据结构
- `StreamingSessionState` 包含：
  - `latest_raw_text`
  - `last_visible_snapshot`
  - `binding_state_summary`
  - `page_state_summary`
  - `is_processing`
  - `has_pending_update`
  - `is_stream_end`
  - `next_segment_index`
  - `first_render_done`

### 串行机制
- 为每个 session 配置 `asyncio.Lock`。
- `submit_snapshot` 先加锁更新 state；若 `is_processing=True` 直接返回。
- 首个进入者将 `is_processing=True` 后执行 drain；drain 结束后恢复 `is_processing=False`。

### 触发规则
- 首屏前触发：
  - 任一 `changes.new_array_items[path] >= 2`；或
  - `is_stream_end=True` 且 `visible_snapshot` 非空。
- 首屏后触发：
  - 任一 `changes.new_array_items[path] >= 2`；或
  - `is_stream_end=True` 且本轮 `changes` 有增量。
- 跳过规则：
  - `visible_snapshot` 未变化 且 `new_paths/new_array_items` 为空 且 `is_stream_end=False`，则跳过本轮模型调用。

### service 调用与回写
- 按指定 payload 调用 `await self._prompt_service.project_segment(payload)`。
- 回写：
  - `last_visible_snapshot`
  - `binding_state_summary`
  - `page_state_summary`
  - `first_render_done`（frames/events 任一非空）
  - `next_segment_index += 1`
