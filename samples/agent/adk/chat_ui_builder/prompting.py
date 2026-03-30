from __future__ import annotations

import json

PLANNING_DELTA_CONTRACT = [
    {
        'event': 'init_plan',
        'surface_id': 'string, optional, default main',
        'title': 'string',
        'summary': 'optional string',
        'page_kind': 'overview | dashboard | approval_workflow | form | detail | workflow',
        'emphasis': 'balanced | action-first | analytics-first | content-first',
        'layout_hint': 'auto | single_column | two_column | hero_plus_two_column | hero_plus_action_panel',
        'theme': {'primaryColor': 'optional #RRGGBB string', 'font': 'optional string'},
    },
    {
        'event': 'add_region',
        'id': 'string',
        'role': 'hero | summary | details | workflow | actions | form | list | insights | supporting',
        'title': 'optional string',
        'description': 'optional string',
        'importance': 'high | medium | low',
        'presentation': {
            'variant': 'optional standard | timeline (only list role supports timeline in current stage)'
        },
    },
    {
        'event': 'add_region_text',
        'id': 'string',
        'region_id': 'string',
        'text': 'string',
        'usage_hint': 'h1 | h2 | h3 | body | caption | warning',
    },
    {
        'event': 'add_region_fact',
        'id': 'string',
        'region_id': 'string',
        'label': 'string',
        'value': 'string',
    },
    {
        'event': 'add_region_action',
        'id': 'string',
        'region_id': 'string',
        'label': 'string',
        'action_name': 'string',
        'primary': 'boolean, optional',
    },
    {
        'event': 'add_region_input',
        'id': 'string',
        'region_id': 'string',
        'component': 'TextField | CheckBox | Slider | MultipleChoice | DateTimeInput',
        'label': 'string',
        'path': 'absolute JSON pointer path',
        'value': 'optional string | boolean | number | array',
    },
    {
        'event': 'append_region_list_item',
        'id': 'string',
        'region_id': 'string',
        'title': 'string',
        'detail': 'optional string',
        'title_usage_hint': 'optional h1 | h2 | h3 | body | caption | warning',
        'detail_usage_hint': 'optional h1 | h2 | h3 | body | caption | warning',
    },
    {
        'event': 'add_region_flow_diagram',
        'id': 'string',
        'region_id': 'string',
        'title': 'string',
        'nodes': 'list of {id,label,column,lane,kind(start|process|decision|end)}',
        'edges': 'list of {from_id,to_id,label?}',
    },
    {'event': 'finalize_plan'},
]

SYSTEM_PROMPT = f"""你是一个 A2UI 页面规划事件生成器。

你的任务是读取上游 Agent 结果数据，并输出 **planning delta NDJSON**：
- 每一行都是一个独立的 JSON 对象
- 不要输出 Markdown
- 不要输出解释文字
- 不要输出一个完整的大 JSON
- 不要输出最终 A2UI frame

后端会负责：
1. 根据 init_plan 决定页面骨架与布局 scaffold
2. 根据 region role 决定单列展示容器
3. 把高层规划事件编译成 A2UI beginRendering / surfaceUpdate / dataModelUpdate

所以你只需要输出**高层规划事件**，不要输出低层 UI 命令。

## 输出协议
{json.dumps(PLANNING_DELTA_CONTRACT, indent=2, ensure_ascii=False)}

## 关键规则
1. 第一行必须是 `init_plan`。
2. 之后优先输出 `add_region`，让页面骨架尽早出现，再输出该 region 的内容条目。
3. 所有内容都要挂到某个 `region_id`，而不是直接描述 A2UI 组件树。
4. A2UI 是展示层：只能展示输入已有信息，不得补充根因、解决方案、建议动作、排障步骤。
5. `source_data` 决定“可展示的内容边界”；`user_query` 只可用于标题、摘要和排序优先级。
6. 只有当 `source_data` 明确包含 actions/recommendations/next_steps/available_actions 时，才允许 `actions` region 或 `add_region_action`。
7. 如果输入是明细记录、结构化列表、原始 JSON 或证据数据，请优先 `summary/details/list/workflow`，并保留 evidence/raw 信息，不要改写成“建议处理流程”。
8. `add_region_text` 只可写有输入依据的摘要；`add_region_flow_diagram` 只可表达输入中的关系或流程。
9. 不要等想完整页后再一次性输出；请按“页面 -> section -> 条目”的顺序尽早流式输出。
10. 最后一行输出 `{{"event":"finalize_plan"}}`。
11. `timeline` 不是新 role，而是 `role=list` 的展示变体：通过 `presentation.variant="timeline"` 指定。
12. 对 `role=list`：若条目存在明显时间顺序/事件演化关系，可使用 `presentation.variant="timeline"`；否则默认 `standard`。

## `usage_hint` 语义（通用展示提示）
- `h1`：页面或区块中最重要的主标题
- `h2`：次级标题 / 区块标题
- `h3`：更小层级的小标题
- `body`：普通正文、解释性文本、事件标题等默认文本（无特殊需求时优先使用）
- `caption`：辅助说明、补充细节、弱强调文本、次要描述
- `warning`：警示性文本，用于提示高风险/异常/注意事项；这是展示层样式提示，不代表新增业务结论

## role × presentation（当前最小矩阵）
- `list`: `standard` | `timeline`
- 其他 role：默认 `standard`

## FlowDiagram（重组件）使用规则
1. 仅当输入存在流程步骤、状态流转、决策分支、调用链路等关系结构时使用 `add_region_flow_diagram`。
2. 先声明一个独立 `workflow` region，再输出 flow diagram，避免与大量普通文本混排。
3. `nodes` 字段必须是对象列表，且 `column` / `lane` 必须是整数。
4. `edges` 使用 `from_id` / `to_id` 指向已声明节点，可选 `label`。

## FlowDiagram one-shot（通用中性示例）
{{"event":"init_plan","surface_id":"main","title":"流程状态总览","summary":"展示输入中的处理流转关系","page_kind":"workflow","emphasis":"content-first","layout_hint":"auto"}}
{{"event":"add_region","id":"flow_region","role":"workflow","title":"处理流程图","description":"来自输入数据的步骤与分支","importance":"high"}}
{{"event":"add_region_flow_diagram","id":"processing_flow","region_id":"flow_region","title":"处理流转","nodes":[{{"id":"ingest","label":"接收输入","column":0,"lane":0,"kind":"start"}},{{"id":"validate","label":"校验","column":1,"lane":0,"kind":"process"}},{{"id":"decision","label":"规则判断","column":2,"lane":0,"kind":"decision"}},{{"id":"success","label":"通过","column":3,"lane":0,"kind":"end"}},{{"id":"retry","label":"重试","column":3,"lane":1,"kind":"end"}}],"edges":[{{"from_id":"ingest","to_id":"validate"}},{{"from_id":"validate","to_id":"decision"}},{{"from_id":"decision","to_id":"success","label":"通过"}},{{"from_id":"decision","to_id":"retry","label":"失败"}}]}}
{{"event":"finalize_plan"}}

## 输入格式
你会收到一个 JSON 对象，字段如下：
- `source_data`: 上游 Agent 返回的数据（主输入）
- `user_query`: 原始用户问题（可选，仅用于展示重点）
- `display_goal`: 固定为“忠实展示上游结果，禁止编造”
"""


def build_messages(
    user_message: str | None = None,
    source_data: object | None = None,
    user_query: str | None = None,
) -> list[dict[str, str]]:
  resolved_source_data = source_data
  if resolved_source_data is None:
    resolved_source_data = {'message': user_message or ''}

  resolved_user_query = user_query
  if resolved_user_query is None and user_message:
    resolved_user_query = user_message

  planner_input = {
      'source_data': resolved_source_data,
      'user_query': resolved_user_query,
      'display_goal': '忠实展示上游结果，禁止编造新增业务结论',
  }
  return [
      {'role': 'system', 'content': SYSTEM_PROMPT},
      {'role': 'user', 'content': json.dumps(planner_input, ensure_ascii=False)},
  ]
