from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from models import AddRegionActionDelta, AddRegionDelta, AddRegionFactDelta, InitPlanDelta
from skeleton_compiler import SkeletonCompiler


def _slot_component_ids(frames: list[object]) -> set[str]:
  component_ids: set[str] = set()
  for frame in frames:
    surface_update = getattr(frame, 'surfaceUpdate', None)
    if not surface_update:
      continue
    for component in surface_update.components:
      component_ids.add(component.id)
  return component_ids


def _data_paths(frames: list[object]) -> list[str]:
  paths: list[str] = []
  for frame in frames:
    data_update = getattr(frame, 'dataModelUpdate', None)
    if not data_update:
      continue
    paths.append(data_update.path)
  return paths


def test_summary_region_uses_explicit_header_and_body_slots() -> None:
  compiler = SkeletonCompiler()
  compiler.apply(InitPlanDelta(event='init_plan', title='Summary page'))
  frames = compiler.apply(
      AddRegionDelta(
          event='add_region',
          id='summary_region',
          role='summary',
          title='Summary',
          description='Daily KPI snapshot',
      )
  )

  binding = compiler.regions['summary_region']
  component_ids = _slot_component_ids(frames)
  data_paths = _data_paths(frames)

  assert binding.parent_for('text') == 'summary_region_body'
  assert binding.parent_for('fact') == 'summary_region_summary_facts'
  assert 'summary_region_header' in component_ids
  assert 'summary_region_header_title' in component_ids
  assert 'summary_region_header_description' in component_ids
  assert '/sections/summary_region' not in data_paths
  assert '/content/summary_region_header_title' in data_paths
  assert '/content/summary_region_header_description' in data_paths


def test_actions_region_has_stable_primary_and_secondary_slots() -> None:
  compiler = SkeletonCompiler()
  compiler.apply(
      InitPlanDelta(
          event='init_plan',
          title='Approval',
          page_kind='detail',
          emphasis='action-first',
          layout_hint='two_column',
      )
  )
  frames = compiler.apply(AddRegionDelta(event='add_region', id='actions_region', role='actions', title='Actions'))
  binding = compiler.regions['actions_region']
  component_ids = _slot_component_ids(frames)

  assert binding.parent_for('action_primary') == 'actions_region_actions_primary'
  assert binding.parent_for('action_secondary') == 'actions_region_actions_secondary'
  assert 'actions_region_actions_primary' in component_ids
  assert 'actions_region_actions_secondary' in component_ids


def test_layout_scaffold_keeps_bucket_order_with_split_layout() -> None:
  compiler = SkeletonCompiler()
  frames = compiler.apply(
      InitPlanDelta(
          event='init_plan',
          title='Dashboard',
          page_kind='dashboard',
          emphasis='analytics-first',
          layout_hint='hero_plus_two_column',
      )
  )
  component_ids = _slot_component_ids(frames)

  assert 'layout_split_row' in component_ids
  assert 'layout_main_content' in component_ids
  assert 'layout_side_rail' in component_ids
  assert 'hero_bucket' in component_ids
  assert 'actions_bucket' in component_ids


def test_pending_region_deltas_flush_through_structural_slot_mapping() -> None:
  compiler = SkeletonCompiler()
  compiler.apply(InitPlanDelta(event='init_plan', title='Detail page'))

  compiler.apply(
      AddRegionActionDelta(
          event='add_region_action',
          id='details_cta',
          region_id='details_region',
          label='Review',
          action_name='review',
          primary=True,
      )
  )
  compiler.apply(
      AddRegionFactDelta(
          event='add_region_fact',
          id='details_fact',
          region_id='details_region',
          label='Owner',
          value='Ops',
      )
  )

  frames = compiler.apply(AddRegionDelta(event='add_region', id='details_region', role='details', title='Details'))
  component_ids = _slot_component_ids(frames)

  assert 'details_region_header' in component_ids
  assert 'details_region_body' in component_ids
  assert 'details_region_details_actions' in component_ids
  assert 'details_region_details_facts' in component_ids
  assert 'details_cta' in component_ids
  assert 'details_fact' in component_ids
