from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from models import (
    AddRegionDelta,
    AddRegionFactDelta,
    AddRegionTextDelta,
    AppendRegionListItemDelta,
    FinalizeDelta,
    InitPlanDelta,
    SkeletonDelta,
)

LOG_COLLECTION_KEYS = {'exceptionInfos', 'logs', 'records', 'events', 'items'}


def is_log_search_source(source_data: Any) -> bool:
  if not isinstance(source_data, dict):
    return False

  if any(key in source_data for key in LOG_COLLECTION_KEYS):
    events = _extract_events(source_data)
    if events:
      return True

  lowered_keys = {str(key).lower() for key in source_data.keys()}
  return bool({'log', 'logcontent', 'abnormalityid', 'ciname'}.intersection(lowered_keys))


def build_log_template_deltas(source_data: dict[str, Any], user_query: str | None = None) -> list[SkeletonDelta]:
  events = _extract_events(source_data)
  normalized_events = [_normalize_event(event, index) for index, event in enumerate(events)]
  stats = _summary_stats(normalized_events, source_data)

  title = _derive_title(source_data, user_query)
  summary = _derive_summary(stats)

  deltas: list[SkeletonDelta] = [
      InitPlanDelta(
          event='init_plan',
          surface_id='main',
          title=title,
          summary=summary,
          page_kind='overview',
          emphasis='content-first',
          layout_hint='single_column',
      ),
      AddRegionDelta(event='add_region', id='log_overview_region', role='summary', title='概览', importance='high'),
      AddRegionFactDelta(
          event='add_region_fact',
          id='log_total_count_fact',
          region_id='log_overview_region',
          label='事件总数',
          value=str(stats['total_count']),
      ),
  ]

  if stats['severe_count'] is not None:
    deltas.append(
        AddRegionFactDelta(
            event='add_region_fact',
            id='log_severe_count_fact',
            region_id='log_overview_region',
            label='高优先级事件',
            value=str(stats['severe_count']),
        )
    )
  if stats['first_time']:
    deltas.append(
        AddRegionFactDelta(
            event='add_region_fact',
            id='log_first_time_fact',
            region_id='log_overview_region',
            label='首条时间',
            value=stats['first_time'],
        )
    )
  if stats['last_time']:
    deltas.append(
        AddRegionFactDelta(
            event='add_region_fact',
            id='log_last_time_fact',
            region_id='log_overview_region',
            label='末条时间',
            value=stats['last_time'],
        )
    )
  if stats['target_object']:
    deltas.append(
        AddRegionFactDelta(
            event='add_region_fact',
            id='log_target_object_fact',
            region_id='log_overview_region',
            label='目标对象',
            value=stats['target_object'],
        )
    )

  deltas.append(AddRegionDelta(event='add_region', id='log_event_timeline_region', role='list', title='事件时间线', importance='high'))
  if normalized_events:
    for index, event in enumerate(normalized_events, start=1):
      detail = _event_detail(event)
      deltas.append(
          AppendRegionListItemDelta(
              event='append_region_list_item',
              id=f'log_event_item_{index}',
              region_id='log_event_timeline_region',
              title=f"{event['time']} | {event['type']} | {event['level']}",
              detail=detail,
          )
      )
  else:
    deltas.append(
        AddRegionTextDelta(
            event='add_region_text',
            id='log_event_empty_text',
            region_id='log_event_timeline_region',
            text='输入数据未包含可解析事件列表，以下仅展示上下文与原始数据。',
            usage_hint='body',
        )
    )

  deltas.append(
      AddRegionDelta(event='add_region', id='log_context_region', role='supporting', title='对象与上下文', importance='medium')
  )
  for key, label in [
      ('ciName', '对象名称'),
      ('ciType', '对象类型'),
      ('ciSubType', '对象子类型'),
      ('abnormalityId', '异常ID'),
      ('query', '查询条件'),
      ('source', '数据来源'),
  ]:
    value = _lookup_value(source_data, key)
    if value:
      deltas.append(
          AddRegionFactDelta(
              event='add_region_fact',
              id=f'log_context_{key}_fact',
              region_id='log_context_region',
              label=label,
              value=str(value),
          )
      )

  if user_query:
    deltas.append(
      AddRegionTextDelta(
          event='add_region_text',
          id='log_query_text',
          region_id='log_context_region',
          text=f'原始用户查询：{user_query}',
          usage_hint='caption',
      )
    )

  raw_data_text = json.dumps(source_data, ensure_ascii=False, indent=2)
  deltas.extend(
      [
          AddRegionDelta(event='add_region', id='log_raw_data_region', role='details', title='原始数据', importance='medium'),
          AddRegionTextDelta(
              event='add_region_text',
              id='log_raw_data_text',
              region_id='log_raw_data_region',
              text=raw_data_text[:5000],
              usage_hint='caption',
          ),
          FinalizeDelta(event='finalize_plan'),
      ]
  )
  return deltas


def _extract_events(source_data: dict[str, Any]) -> list[dict[str, Any]]:
  for key in LOG_COLLECTION_KEYS:
    value = source_data.get(key)
    if isinstance(value, list):
      return [item for item in value if isinstance(item, dict)]
  return []


def _lookup_value(source_data: dict[str, Any], key: str) -> Any:
  if key in source_data:
    return source_data[key]
  for nested_key in ('meta', 'context', 'queryContext'):
    nested = source_data.get(nested_key)
    if isinstance(nested, dict) and key in nested:
      return nested[key]
  return None


def _derive_title(source_data: dict[str, Any], user_query: str | None) -> str:
  if user_query:
    return f'日志检索结果：{user_query[:36]}'
  explicit_title = source_data.get('title') or source_data.get('name')
  if isinstance(explicit_title, str) and explicit_title.strip():
    return explicit_title[:60]
  return '日志检索结果概览'


def _summary_stats(events: list[dict[str, str]], source_data: dict[str, Any]) -> dict[str, Any]:
  times = [item['time'] for item in events if item.get('time') and item['time'] != '未知时间']
  severe_levels = {'critical', 'fatal', 'error', 'high', '严重', '高'}
  severe_count = sum(1 for item in events if item.get('level', '').lower() in severe_levels)
  target_object = _lookup_value(source_data, 'ciName') or _lookup_value(source_data, 'target')
  return {
      'total_count': len(events),
      'severe_count': severe_count if events else None,
      'first_time': min(times) if times else None,
      'last_time': max(times) if times else None,
      'target_object': str(target_object) if target_object else None,
  }


def _derive_summary(stats: dict[str, Any]) -> str:
  if stats['total_count'] == 0:
    return '未解析到结构化事件，展示原始数据与上下文信息。'
  range_text = ''
  if stats['first_time'] and stats['last_time']:
    range_text = f"，时间范围 {stats['first_time']} 至 {stats['last_time']}"
  severe_text = ''
  if stats['severe_count'] is not None:
    severe_text = f"，高优先级 {stats['severe_count']} 条"
  return f"共 {stats['total_count']} 条日志事件{severe_text}{range_text}。"


def _normalize_event(event: dict[str, Any], index: int) -> dict[str, str]:
  time_value = _first_non_empty(event, ['time', 'timestamp', 'eventTime', 'occurredAt'])
  level_value = _first_non_empty(event, ['level', 'severity', 'priority'])
  type_value = _first_non_empty(event, ['type', 'exceptionType', 'logType', 'abnormalType'])
  content_value = _first_non_empty(event, ['logContent', 'message', 'content', 'detail'])
  ci_type = _first_non_empty(event, ['ciType'])
  ci_sub_type = _first_non_empty(event, ['ciSubType'])

  return {
      'time': _normalize_time(time_value) or f'第{index + 1}条',
      'level': level_value or 'unknown',
      'type': type_value or 'log_event',
      'content': content_value or json.dumps(event, ensure_ascii=False)[:180],
      'ciType': ci_type or '',
      'ciSubType': ci_sub_type or '',
  }


def _event_detail(event: dict[str, str]) -> str:
  extra_parts = []
  if event['ciType']:
    extra_parts.append(f"ciType={event['ciType']}")
  if event['ciSubType']:
    extra_parts.append(f"ciSubType={event['ciSubType']}")
  extra_text = f" | {'; '.join(extra_parts)}" if extra_parts else ''
  return f"{event['content']}{extra_text}"


def _first_non_empty(payload: dict[str, Any], keys: list[str]) -> str | None:
  for key in keys:
    value = payload.get(key)
    if value is None:
      continue
    text = str(value).strip()
    if text:
      return text
  return None


def _normalize_time(raw: str | None) -> str | None:
  if not raw:
    return None
  for pattern in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%fZ'):
    try:
      parsed = datetime.strptime(raw, pattern)
      return parsed.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
      continue
  return raw
