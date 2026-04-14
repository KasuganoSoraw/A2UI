# Chat UI Builder 日志搜索展示模板设计

## 需求详情
实现一个面向日志搜索结果的展示模板（`log_search_result_template`），并打通从输入层到前端渲染的全链路。模板目标是忠实展示上游 Agent 返回的日志数据，不做根因/方案/动作编造。

## 澄清结果
- 模板是展示模板，不是求解模板。
- 优先复用现有原子组件与 planning delta 事件。
- 若输入为日志/事件集合，允许后端走模板化直编排路径，保证稳定输出。
- `user_query` 仅影响标题和重点排序，不扩展业务结论。

## WHAT
1. 新增日志模板生成器：
   - 输入 `source_data + user_query`
   - 产出稳定 planning deltas（概览、事件列表、上下文、原始数据）
2. 在 service 层新增日志模板判定：
   - 命中日志场景时走模板直编译
   - 否则保持现有 LLM planning delta 主链
3. 更新 prompt：补充日志场景下的推荐事件组合与禁止事项。
4. 前端 demo 支持提交 `source_data`（JSON）与 `user_query`，确保链路可实测。
5. 增加测试覆盖模板检测与输出约束（无默认 actions、包含 raw-data）。

## WHY
- 日志搜索结果结构稳定，模板化可显著提升可读性和一致性。
- 模板直编排可减少 LLM 抖动，保证“展示层”职责边界。
- 保留原始 JSON 区块有助于证据追溯。

## HOW
1. 新增 `log_template.py`：
   - 检测日志数据特征
   - 规范化事件
   - 生成 planning delta 列表
2. `service.py`：
   - 若命中日志模板，直接走 `SkeletonCompiler` 逐条编译并流式输出
   - 保留现有 planning parser 主路径作为默认路径
3. `prompting.py`：
   - 增加日志模板示例和约束
4. `samples/client/react/chat_ui_builder/src/App.tsx`：
   - 增加 `source_data` JSON 输入框
   - 请求体支持 `{source_data, user_query}`
5. 更新测试与 README。
