# Chat UI Builder 展示层定位收敛设计

## 需求详情
将 A2UI 从“二次求解/方案生成”定位收敛为“上游 Agent 结果的展示编译层”。核心要求：
- 主输入是 `source_data`（上游结果），`user_query` 仅作可选展示辅助。
- planning prompt/contract 明确“只展示、不编造”。
- 无显式动作项时，后端不应通过默认逻辑渲染 actions 区域。
- 保持 planning delta 主链稳定可运行。

## 澄清结果
- 可兼容旧 `message` 输入，但新语义以数据展示为中心。
- 不新增复杂 fallback 路径；仍是 planning delta 单链路。
- 轻量后端约束优先落在 service 编译入口，避免模型偶发越界。

## WHAT
1. 改写 prompt 与 contract 说明：
   - A2UI 是展示编译器，不补根因/方案/建议。
   - `add_region_action` 仅当输入存在动作项。
   - `user_query` 只影响标题、排序、摘要重点。
2. 扩展服务入口输入：支持 `source_data` + `user_query`，并兼容 `message`。
3. 后端最小约束：
   - 若未检测到动作项，过滤 `actions` region 与 `add_region_action` 事件。
4. 同步 API 请求模型、README 与测试样例。

## WHY
- 真实业务链路中，A2UI是上游结果展示层，不应再次“解题”。
- 将业务结论生成留在上游 Agent，可降低误导和幻觉风险。
- 引入最小后端约束可降低 prompt 偏移导致的越界输出。

## HOW
1. 在 `prompting.py` 重写系统提示词和输入封装，强化展示层边界。
2. 在 `service.py` 引入 `source_data/user_query` 入参，并增加动作项检测与事件过滤。
3. 在 `app.py` 扩展请求体结构并兼容旧字段。
4. 更新 `tests/test_service_single_path.py`：
   - 覆盖新输入结构；
   - 覆盖“无动作项时过滤 actions”。
5. 更新 README 的 API 与定位说明。
