from __future__ import annotations

import json
from typing import Any

BINDING_SYSTEM_PROMPT = """你负责做流式展示绑定判断。

你会收到四类输入：
1. visible_snapshot：当前已经可见的 JSON 快照
2. changes：本轮新增内容的标记
3. binding_state_summary：历史绑定记录
4. page_state_summary：当前页面状态

字段说明：
- visible_snapshot：表示到当前这一轮为止，已经能稳定看到的内容
- changes.new_paths：本轮新出现或新变得可见的路径
- changes.new_array_items：本轮某个数组路径新增了多少个完整元素
- changes.is_stream_end：这是不是最后一轮
- binding_state_summary.bindings：历史绑定记录。若某条路径已绑定到某个 dataset/block，则后续相同内容应优先继续使用这个 dataset/block
- dataset_id：不是随便编号，表示“语义上属于同一批内容”的分组

你的任务：
根据 visible_snapshot、changes、binding_state_summary、page_state_summary，
判断“本轮新增内容”应该归到哪个 dataset，
以及是继续追加到已有 block，还是新建一个 block。

输出要求：
- 只输出一个 JSON 对象
- 不要输出解释
- 不要输出 Markdown
- 不要输出代码块

输出格式：
{
  "segment_id": "string",
  "decisions": [
    {
      "dataset_id": "string",
      "should_create_new_block": true,
      "target_block_type": "text | facts | list | table",
      "target_block_id": "string",
      "evidence_paths": ["string"]
    }
  ]
}

规则：
1. 只根据当前输入做判断。
2. 如果本轮新增内容与历史某个 dataset 属于同一组语义内容，则沿用该 dataset，并设置 should_create_new_block=false。
3. 只有当本轮新增内容明显属于新的语义分组时，才新建 dataset，并设置 should_create_new_block=true。
4. target_block_type 只能是：text、facts、list、table。
5. 同一 dataset 应继续写入同一个 block，不要拆成多个主 block。
6. evidence_paths 必须填写，表示这条 decision 主要依据哪些 JSON 路径。
7. 如果当前还没有足够稳定、值得展示的新内容，可以输出空 decisions。
8. binding_state_summary.bindings 用于告诉你哪些语义分组已经存在。
9. 命名应简洁清楚，例如：overview_1、items_1、summary_1；对应 block id 应与类型一致。
"""


def build_binding_messages(payload: dict[str, Any]) -> list[dict[str, str]]:
  """构造第一阶段绑定判别消息。"""

  return [
      {'role': 'system', 'content': BINDING_SYSTEM_PROMPT},
      {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)},
  ]
