# Chat UI Builder 通用 prompt 语义增强设计（FlowDiagram + usage_hint）

## 需求详情
在保持通用展示框架定位下，增强 planning prompt 与 contract：
1) 提升 FlowDiagram 重组件的可生成性与正确率；
2) 强化 `usage_hint` 语义说明；
3) 把 `usage_hint` 决策尽量交回模型，后端仅做默认兜底。

## 澄清结果
- 不回退到场景模板（不引入日志 one-shot）。
- 允许新增一个通用 FlowDiagram one-shot（中性流程示例）。
- `warning` 继续作为通用 usage_hint。

## WHAT
1. prompt/contract 增强：
   - 明确 `h1/h2/h3/body/caption/warning` 含义和选用原则。
   - 增加 FlowDiagram 专门规则（适用条件、独立 region、合法字段）。
   - 增加通用 FlowDiagram one-shot。
2. schema 扩展：
   - `append_region_list_item` 新增可选 `title_usage_hint/detail_usage_hint`。
   - low-level `append_list_item` 同步新增对应可选字段。
3. compiler/skeleton 调整：
   - list item 的 usage_hint 使用“模型优先、后端兜底”策略。
4. 测试更新：
   - 增加 list item usage_hint 透传测试。

## WHY
- 仅靠事件名不足以让模型稳定生成重组件，需要结构化示例和字段提示。
- usage_hint 语义明确后，模型能更稳定地做展示表达，不必后端写死。

## HOW
1. 修改 `prompting.py`：补充 usage_hint 语义规则与 FlowDiagram one-shot。
2. 修改 `models.py`：为 list item usage_hint 扩展可选字段。
3. 修改 `skeleton_compiler.py` 与 `compiler.py`：透传 hint，缺省时回退 body/caption。
4. 更新 `tests/test_region_archetypes.py` 增加断言。
