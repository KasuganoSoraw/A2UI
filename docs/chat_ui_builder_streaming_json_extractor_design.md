# chat_ui_builder streaming json_extractor 设计

## 需求详情
新增 `chat_ui_builder/streaming/json_extractor.py`，只负责第一阶段输入准备：
- 从前端累计 JSON 文本中提取当前可见且结构完整的 `visible_snapshot`
- 基于上一轮 snapshot 计算 `changes`
- 返回可直接喂给第一阶段 prompt 的工程化结果

## 澄清结果
1. 文件职责收敛，不接入第一阶段/第二阶段模型，不更新 binding/page 状态。
2. 输入默认是“根为 object 的累计 JSON 文本”。
3. 采用保守提取：未闭合尾巴直接丢弃，不做智能补全。
4. 数组支持“前若干完整元素可见”。

## WHAT
- 定义 `JsonExtractionResult`：
  - `visible_snapshot: dict[str, Any]`
  - `changes: dict[str, Any]`
- 定义 `JsonExtractor.extract(...)`：
  - 输入：`raw_text` / `previous_snapshot` / `is_stream_end`
  - 输出：`JsonExtractionResult`
- 主要私有方法：
  - `_build_visible_snapshot`
  - `_build_changes`
  - `_collect_paths`
  - `_count_array_items_by_path`

## WHY
- 两阶段 service 需要稳定可解析的 snapshot 输入，断裂 JSON 不能直接送模型。
- `changes` 必须相对“上一轮已提交 snapshot”计算，才能准确表达本轮新增可见内容。

## HOW
1. 使用轻量字符扫描 + 递归下降解析：
   - 正确处理字符串、转义、对象/数组层级。
   - 遇到断裂时返回“当前已经完整解析出的前缀结构”。
2. object 规则：
   - 仅将“键和值都完整闭合”的字段放入 snapshot。
3. array 规则：
   - 即使数组末尾未闭合，也保留前面已完整闭合的元素。
4. `changes` 规则：
   - `new_paths = current_paths - previous_paths`
   - `new_array_items[path] = current_len - previous_len (仅 >0)`
   - `is_stream_end` 原样透传。
5. 在文件底部提供最小自检（4 个用例）：
   - 完整 JSON
   - 对象尾部断裂
   - 数组元素中间断裂
   - changes 计算
