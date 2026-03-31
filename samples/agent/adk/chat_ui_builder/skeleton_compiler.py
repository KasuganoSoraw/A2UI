from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Callable

from compiler import FrameCompiler
from models import (
    A2UIFrame,
    AddButtonDelta,
    AddDividerDelta,
    AddFlowDiagramDelta,
    AddImageDelta,
    AddInputDelta,
    AddKeyValueDelta,
    AddRegionActionDelta,
    AddRegionDelta,
    AddRegionDividerDelta,
    AddRegionFactDelta,
    AddRegionFlowDiagramDelta,
    AddRegionImageDelta,
    AddRegionInputDelta,
    AddRegionTextDelta,
    AddRegionTableDelta,
    AddSectionDelta,
    AddTableDelta,
    AddTextDelta,
    AppendListItemDelta,
    AppendRegionListItemDelta,
    FinalizeDelta,
    InitPlanDelta,
    InitSurfaceDelta,
)
from region_archetypes import ArrangementSemantics, RegionArchetypeRegistry, RegionBuildContext

logger = logging.getLogger(__name__)

BUCKET_ORDER = {
    'hero_bucket': 10,
    'summary_bucket': 20,
    'details_bucket': 30,
    'workflow_bucket': 40,
    'form_bucket': 50,
    'list_bucket': 60,
    'supporting_bucket': 70,
    'actions_bucket': 80,
}

@dataclass
class PendingRegionDelta:
  slot_name: str
  delta_builder: Callable[[str], object]


@dataclass
class RegionBinding:
  region_id: str
  role: str
  section_id: str
  archetype: str
  importance: str
  slot_parents: dict[str, str] = field(default_factory=dict)

  def parent_for(self, slot_name: str) -> str:
    return self.slot_parents.get(slot_name, self.slot_parents.get('text', self.section_id))


@dataclass
class LayoutRecipe:
  role_slots: dict[str, str]


class SkeletonCompiler:
  def __init__(self) -> None:
    self.frame_compiler = FrameCompiler()
    self.archetypes = RegionArchetypeRegistry()
    self.initialized = False
    self.layout_hint = 'single_column'
    self.page_kind = 'overview'
    self.emphasis = 'balanced'
    self.role_slots: dict[str, str] = {}
    self.regions: dict[str, RegionBinding] = {}
    self.pending_region_deltas: dict[str, list[PendingRegionDelta]] = {}
    self.flow_region_overrides: dict[str, str] = {}
    self.created_buckets: set[str] = set()
    self.page_title: str = ''

  def apply(self, delta: object) -> list[A2UIFrame]:
    payload = delta.model_dump() if hasattr(delta, 'model_dump') else delta
    logger.info('Compiling skeleton delta type=%s payload=%s', type(delta).__name__, payload)
    if isinstance(delta, InitPlanDelta):
      return self._init_plan(delta)
    if isinstance(delta, AddRegionDelta):
      return self._add_region(delta)
    if isinstance(delta, AddRegionTextDelta):
      resolved = self._resolve_text_delta(delta)
      return self._apply_region_delta(
          delta.region_id,
          'text',
          lambda parent_id: resolved.model_copy(update={'parent_id': parent_id}),
      )
    if isinstance(delta, AddRegionTableDelta):
      table_spec = {
          'title': delta.title,
          'columns': [column.model_dump(exclude_none=True) for column in delta.columns],
          'rows': delta.rows,
          'row_key': delta.row_key,
          'striped': delta.striped,
          'bordered': delta.bordered,
      }
      table_spec_json = json.dumps(table_spec, ensure_ascii=False)
      return self._apply_region_delta(
          delta.region_id,
          'text',
          lambda parent_id: AddTableDelta(
              event='add_table',
              id=delta.id,
              parent_id=parent_id,
              spec_json=table_spec_json,
          ),
      )
    if isinstance(delta, AddRegionFactDelta):
      return self._apply_region_delta(
          delta.region_id,
          'fact',
          lambda parent_id: AddKeyValueDelta(
              event='add_key_value',
              id=delta.id,
              parent_id=parent_id,
              label=delta.label,
              value=delta.value,
          ),
      )
    if isinstance(delta, AddRegionImageDelta):
      return self._apply_region_delta(
          delta.region_id,
          'image',
          lambda parent_id: AddImageDelta(
              event='add_image',
              id=delta.id,
              parent_id=parent_id,
              url=delta.url,
              usage_hint=delta.usage_hint,
          ),
      )
    if isinstance(delta, AddRegionActionDelta):
      slot_name = 'action_primary' if delta.primary else 'action_secondary'
      return self._apply_region_delta(
          delta.region_id,
          slot_name,
          lambda parent_id: AddButtonDelta(
              event='add_button',
              id=delta.id,
              parent_id=parent_id,
              label=delta.label,
              action_name=delta.action_name,
              primary=delta.primary,
          ),
      )
    if isinstance(delta, AddRegionInputDelta):
      return self._apply_region_delta(
          delta.region_id,
          'input',
          lambda parent_id: AddInputDelta(
              event='add_input',
              id=delta.id,
              parent_id=parent_id,
              component=delta.component,
              label=delta.label,
              path=delta.path,
              value=delta.value,
              text_field_type=delta.text_field_type,
              min_value=delta.min_value,
              max_value=delta.max_value,
              options=delta.options,
              enable_date=delta.enable_date,
              enable_time=delta.enable_time,
          ),
      )
    if isinstance(delta, AddRegionDividerDelta):
      return self._apply_region_delta(
          delta.region_id,
          'divider',
          lambda parent_id: AddDividerDelta(
              event='add_divider',
              id=delta.id,
              parent_id=parent_id,
          ),
      )
    if isinstance(delta, AppendRegionListItemDelta):
      return self._apply_region_delta(
          delta.region_id,
          'list_item',
          lambda parent_id: AppendListItemDelta(
              event='append_list_item',
              id=delta.id,
              parent_id=parent_id,
              title=delta.title,
              detail=delta.detail,
              title_usage_hint=delta.title_usage_hint,
              detail_usage_hint=delta.detail_usage_hint,
          ),
      )
    if isinstance(delta, AddRegionFlowDiagramDelta):
      flow_region_id, prefix_frames = self._resolve_flow_region(delta.region_id)
      frames = list(prefix_frames)
      frames.extend(
          self._apply_region_delta(
              flow_region_id,
              'flow',
              lambda parent_id: AddFlowDiagramDelta(
                  event='add_flow_diagram',
                  id=delta.id,
                  parent_id=parent_id,
                  title=delta.title,
                  nodes=delta.nodes,
                  edges=delta.edges,
              ),
          )
      )
      return frames
    if isinstance(delta, FinalizeDelta):
      return self._finalize()
    return []

  def _apply_low_level(self, delta: object) -> list[A2UIFrame]:
    return self.frame_compiler.apply(delta)

  def _resolve_layout(self, delta: InitPlanDelta) -> str:
    return 'single_column'

  def _init_plan(self, delta: InitPlanDelta) -> list[A2UIFrame]:
    self.initialized = True
    self.layout_hint = self._resolve_layout(delta)
    self.page_kind = delta.page_kind
    self.emphasis = delta.emphasis
    self.role_slots = {}
    self.regions = {}
    self.pending_region_deltas = {}
    self.flow_region_overrides = {}
    self.created_buckets = set()
    self.page_title = delta.title

    frames = self._apply_low_level(
        InitSurfaceDelta(
            event='init_surface',
            surface_id=delta.surface_id,
            title=delta.title,
            summary=delta.summary,
            theme=delta.theme,
        )
    )
    frames.extend(self._build_layout_scaffold())
    return frames

  def _build_layout_scaffold(self) -> list[A2UIFrame]:
    recipe = self._layout_recipe()
    frames: list[A2UIFrame] = []
    self.role_slots = recipe.role_slots
    logger.info(
        'Initialized layout scaffold=%s role_slots=%s',
        self.layout_hint,
        self.role_slots,
    )
    return frames

  def _slot_for_role(self, role: str) -> str:
    return self.role_slots.get(role, 'root')

  def _layout_recipe(self) -> LayoutRecipe:
    role_slots = {
        'hero': 'hero_bucket',
        'summary': 'summary_bucket',
        'details': 'details_bucket',
        'workflow': 'workflow_bucket',
        'form': 'form_bucket',
        'list': 'list_bucket',
        'insights': 'summary_bucket',
        'supporting': 'supporting_bucket',
        'actions': 'actions_bucket',
    }
    return LayoutRecipe(role_slots=role_slots)

  def _bucket_order(self, bucket_id: str) -> int:
    return BUCKET_ORDER.get(bucket_id, 1000)

  @staticmethod
  def _normalize_text(value: str) -> str:
    return ''.join(ch.lower() for ch in value if ch.isalnum())

  def _is_title_overlap(self, text: str) -> bool:
    normalized_text = self._normalize_text(text)
    normalized_title = self._normalize_text(self.page_title)
    if not normalized_text or not normalized_title:
      return False
    if normalized_text == normalized_title:
      return True
    shorter, longer = sorted((normalized_text, normalized_title), key=len)
    if shorter and shorter in longer:
      overlap_ratio = len(shorter) / len(longer)
      return overlap_ratio >= 0.9
    return False

  def _ensure_bucket_for_role(self, role: str) -> list[A2UIFrame]:
    bucket_id = self.role_slots.get(role)
    if not bucket_id or bucket_id == 'root' or bucket_id in self.created_buckets:
      return []

    frames = self._apply_low_level(
        AddSectionDelta(
            event='add_section',
            id=bucket_id,
            parent_id='root',
            layout='Column',
            order=self._bucket_order(bucket_id),
        )
    )
    self.created_buckets.add(bucket_id)
    return frames

  def _coerce_text_for_binding(self, binding: RegionBinding, delta: AddTextDelta) -> AddTextDelta | None:
    if binding.role == 'hero' and delta.usage_hint == 'h1':
      if self._is_title_overlap(delta.text):
        logger.info('Dropping duplicate hero h1 text region=%s text=%s', binding.region_id, delta.text)
        return None
    return delta

  def _resolve_text_delta(self, delta: AddRegionTextDelta) -> AddTextDelta:
    return AddTextDelta(
        event='add_text',
        id=delta.id,
        parent_id='',
        text=delta.text,
        usage_hint=delta.usage_hint,
    )

  def _arrangement_for(self, delta: AddRegionDelta) -> ArrangementSemantics:
    role_defaults: dict[str, ArrangementSemantics] = {
        'hero': ArrangementSemantics(body='stacked', facts='fact_row', actions='action_row'),
        'summary': ArrangementSemantics(body='compact_group', facts='fact_row', actions='action_row'),
        'insights': ArrangementSemantics(body='compact_group', facts='fact_grid', actions='action_row'),
        'details': ArrangementSemantics(body='stacked', facts='fact_row', actions='action_row'),
        'workflow': ArrangementSemantics(body='stacked', facts='fact_row', actions='action_row'),
        'form': ArrangementSemantics(body='stacked', facts='fact_row', actions='action_row'),
        'actions': ArrangementSemantics(body='compact_group', facts='fact_row', actions='action_row'),
        'supporting': ArrangementSemantics(body='stacked', facts='fact_row', actions='action_row'),
        'list': ArrangementSemantics(body='compact_group', facts='fact_row', actions='action_row'),
    }
    arrangement = role_defaults.get(delta.role, ArrangementSemantics())

    if delta.role in {'summary', 'insights'} and self.page_kind in {'dashboard', 'overview'}:
      arrangement = ArrangementSemantics(body='compact_group', facts='fact_grid', actions=arrangement.actions)

    if delta.role == 'details' and self.emphasis == 'content-first':
      arrangement = ArrangementSemantics(body='stacked', facts='fact_row', actions='action_row')

    return arrangement

  def _resolve_flow_region(self, source_region_id: str) -> tuple[str, list[A2UIFrame]]:
    if source_region_id in self.regions and self.regions[source_region_id].role == 'workflow':
      return source_region_id, []

    target_region_id = self.flow_region_overrides.get(source_region_id)
    if target_region_id is None:
      base_id = f'{source_region_id}_workflow_region'
      target_region_id = base_id
      suffix = 2
      while target_region_id in self.regions and self.regions[target_region_id].role != 'workflow':
        target_region_id = f'{base_id}_{suffix}'
        suffix += 1
      self.flow_region_overrides[source_region_id] = target_region_id

    if target_region_id in self.regions:
      return target_region_id, []

    title = '流程图'
    if source_region_id in self.regions and self.regions[source_region_id].role != 'workflow':
      title = f'{source_region_id}流程图'
    frames = self._add_region(
        AddRegionDelta(
            event='add_region',
            id=target_region_id,
            role='workflow',
            title=title,
            description='为流程图重组件自动创建的独立区域。',
            importance='medium',
        )
    )
    return target_region_id, frames

  def _add_region(self, delta: AddRegionDelta) -> list[A2UIFrame]:
    if not self.initialized:
      raise ValueError('init_plan must be emitted before add_region')
    if delta.id in self.regions:
      raise ValueError(f'Duplicate region id: {delta.id}')

    frames = self._ensure_bucket_for_role(delta.role)

    builder = self.archetypes.builder_for(delta.role)
    context = RegionBuildContext(
        slot_parent=self._slot_for_role(delta.role),
        delta=delta,
        page_kind=self.page_kind,
        emphasis=self.emphasis,
        layout_hint=self.layout_hint,
        arrangement=self._arrangement_for(delta),
        presentation_variant=delta.presentation.variant if delta.presentation else 'standard',
    )
    result = builder.build(context, self._apply_low_level)
    self.regions[delta.id] = RegionBinding(
        region_id=delta.id,
        role=delta.role,
        section_id=delta.id,
        archetype=result.archetype,
        importance=delta.importance,
        slot_parents=result.slot_parents,
    )
    frames.extend(result.frames)
    frames.extend(self._flush_pending_region_deltas(delta.id))
    return frames

  def _apply_region_delta(
      self,
      region_id: str,
      slot_name: str,
      delta_builder: Callable[[str], object],
  ) -> list[A2UIFrame]:
    if region_id not in self.regions:
      logger.info('Region %s not ready; queueing %s', region_id, slot_name)
      self.pending_region_deltas.setdefault(region_id, []).append(
          PendingRegionDelta(slot_name=slot_name, delta_builder=delta_builder)
      )
      return []
    binding = self.regions[region_id]
    low_level_delta = delta_builder(binding.parent_for(slot_name))
    if isinstance(low_level_delta, AddTextDelta):
      low_level_delta = self._coerce_text_for_binding(binding, low_level_delta)
      if low_level_delta is None:
        return []
    return self._apply_low_level(low_level_delta)

  def _flush_pending_region_deltas(self, region_id: str) -> list[A2UIFrame]:
    binding = self.regions[region_id]
    queued = self.pending_region_deltas.pop(region_id, [])
    frames: list[A2UIFrame] = []
    for item in queued:
      low_level_delta = item.delta_builder(binding.parent_for(item.slot_name))
      if isinstance(low_level_delta, AddTextDelta):
        low_level_delta = self._coerce_text_for_binding(binding, low_level_delta)
        if low_level_delta is None:
          continue
      frames.extend(self._apply_low_level(low_level_delta))
    return frames

  def _finalize(self) -> list[A2UIFrame]:
    frames: list[A2UIFrame] = []
    orphan_region_ids = list(self.pending_region_deltas.keys())
    for region_id in orphan_region_ids:
      frames.extend(
          self._add_region(
              AddRegionDelta(
                  event='add_region',
                  id=region_id,
                  role='details',
                  title='补建内容区',
                  description='模型在 region 声明前先发送了条目，后端已自动兜底创建。',
              )
          )
      )
    return frames
