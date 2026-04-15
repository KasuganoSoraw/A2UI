from __future__ import annotations

import json
from typing import Any

STREAM_EVENT_SYSTEM_PROMPT = """你负责把绑定判断翻译成流式展示事件。

你会收到：
1. binding_decisions：第一阶段输出的 decisions
2. visible_snapshot：当前已经可见的 JSON 快照
3. changes：本轮新增内容标记
4. binding_state_summary：历史绑定记录
5. page_state_summary：当前页面状态

你的任务：
根据 binding_decisions，
从 visible_snapshot 中提取对应内容，
输出 JSON 事件。

输出要求：
- 只输出 NDJSON
- 每行一个 JSON 对象
- 不要输出解释
- 不要输出 Markdown
- 不要输出数组

允许输出的事件：

init_stream_surface
{"event":"init_stream_surface","surface_id":"main","title":"optional string","summary":"optional string"}

create_text_block
{"event":"create_text_block","block_id":"string","dataset_id":"string","title":"optional string","lines":[{"text":"string","usage_hint":"h1|h2|h3|body|caption|warning"}]}

append_text_lines
{"event":"append_text_lines","block_id":"string","lines":[{"text":"string","usage_hint":"h1|h2|h3|body|caption|warning"}]}

create_facts_block
{"event":"create_facts_block","block_id":"string","dataset_id":"string","title":"optional string","facts":[{"fact_id":"string","label":"string","value":"string"}]}

append_facts
{"event":"append_facts","block_id":"string","facts":[{"fact_id":"string","label":"string","value":"string"}]}

create_list_block
{"event":"create_list_block","block_id":"string","dataset_id":"string","title":"optional string","items":[{"item_id":"string","title":"string","detail":"optional string","title_usage_hint":"optional h1|h2|h3|body|caption|warning","detail_usage_hint":"optional h1|h2|h3|body|caption|warning"}]}

append_list_items
{"event":"append_list_items","block_id":"string","items":[{"item_id":"string","title":"string","detail":"optional string","title_usage_hint":"optional h1|h2|h3|body|caption|warning","detail_usage_hint":"optional h1|h2|h3|body|caption|warning"}]}

create_table_block
{"event":"create_table_block","block_id":"string","dataset_id":"string","title":"optional string","columns":[{"key":"string","label":"string","width":"optional string","align":"optional left|center|right","ellipsis":"optional boolean"}],"rows":[{}]}

append_table_rows
{"event":"append_table_rows","block_id":"string","rows":[{}]}

set_final_summary_text
{"event":"set_final_summary_text","block_id":"final_summary_text","title":"optional string","lines":[{"text":"string","usage_hint":"h1|h2|h3|body|caption|warning"}]}

set_final_summary_facts
{"event":"set_final_summary_facts","block_id":"final_summary_facts","title":"optional string","facts":[{"fact_id":"string","label":"string","value":"string"}]}

规则：
1. 必须严格遵守 binding_decisions。
2. 如果 should_create_new_block=true，则输出对应 create 事件。
3. 如果 should_create_new_block=false，则输出对应 append 事件。
4. 不要改变已有 block 类型。
5. 不要自己发明新的 dataset_id 或 block_id。
6. facts 适合少量概览字段；list 适合逐项条目；table 适合结构稳定的多行多列数据；text 适合说明性文本。
7. 只有 changes.is_stream_end=true 时，才允许输出 final summary 事件。
8. 如果 page_state_summary.surface_initialized=false，且本轮需要展示内容，则先输出一条 init_stream_surface。
"""


def build_stream_event_messages(payload: dict[str, Any]) -> list[dict[str, str]]:
  """构造第二阶段事件生成消息。"""

  return [
      {'role': 'system', 'content': STREAM_EVENT_SYSTEM_PROMPT},
      {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)},
  ]
