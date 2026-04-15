# chat_ui_builder streaming json_extractor 定向修复设计（部分可见子容器保留）

## 需求详情
定向修复 `streaming/json_extractor.py` 的对象字段写入策略：
当字段值是“部分可见但未闭合的子对象/子数组”时，父对象应保留该字段的已可见部分。

## 澄清结果
1. 不重写 extractor，不改文件职责边界。
2. 只修复当前对象字段写入 bug，并顺手检查数组计数覆盖风险。
3. 文件底部 4 个最小自检要真实通过。

## WHAT
- 修改 `_parse_object()`：
  - `value_result.complete == False` 时，若 `value_result.value` 是非空 `dict` 或非空 `list`，仍写入当前 key 后返回。
  - 对半截 string/number/literal 仍不写入 key。
- 修改 `_count_array_items_by_path()`：
  - 嵌套数组统计改为“取更大值”合并，避免后写覆盖造成计数回退。

## WHY
- 之前 `_parse_object()` 在 `complete=False` 时无条件丢弃当前 key，导致 case2/case3 中父对象失去已可见子结构。
- 数组计数在深层递归时存在同路径被后写覆盖的风险，最小修复可提升稳定性。

## HOW
1. 在 `_parse_object()` 的 incomplete 分支加入“部分可见子容器保留”判断。
2. 在 `_count_array_items_by_path()` 合并子计数时改为 `max(existing, child)`。
3. 安装缺失依赖并执行：
   - `python -m py_compile ...`
   - `python streaming/json_extractor.py`（运行文件底部自检）
