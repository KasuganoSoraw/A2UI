# Chat UI Builder add_region_line_chart 全链路接入设计

## 需求详情
- 在现有 table 同模式下新增折线图链路：planning 事件 `add_region_line_chart` -> skeleton 组装 `spec_json` -> low-level `add_line_chart` -> frame 输出 `LineChart.spec.path`。
- 保持最小增量：不新增 role/layout/专属 slot。

## 澄清结果
- 不改前端、不改现有 table 行为。
- `add_region_line_chart` 作为内容事件，挂在现有 region（通过 text 默认落点）。
- `chart_data` 写入 spec 时转换为 `chartData` 字段。

## WHAT
1. `models.py` 新增：
   - `LineChartSettings`
   - `AddRegionLineChartDelta`
   - `AddLineChartDelta`
   - 并接入 `SkeletonDelta/Delta` union。
2. `skeleton_compiler.py` 新增 `AddRegionLineChartDelta` 分支：
   - 组装 spec（title/width/settings/chartData）
   - `json.dumps(..., ensure_ascii=False)` 产出 `spec_json`
   - 经 `_apply_region_delta(..., 'text', ...)` 输出 `AddLineChartDelta`。
3. `compiler.py` 新增 `_add_line_chart`：
   - 挂接 parent children
   - 输出 `LineChart.spec.path`
   - dataModelUpdate 写 `spec` 字符串。
4. `prompting.py` 合同与规则补充 `add_region_line_chart`。
5. 测试覆盖 schema 解析、skeleton 路由、frame 输出、spec 关键字段。

## WHY
- 与 table 复用同一编译模式可减少复杂度并保证协议一致性。
- 折线图属于结构化内容，不应扩展页面职责系统。

## HOW
- 仿照 add_region_table 最小复制式接入，确保行为、数据路径和 dataModel 写法一致。
