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


def test_summary_region_uses_compact_fact_strip_slots() -> None:
  compiler = SkeletonCompiler()
  compiler.apply(
      InitPlanDelta(event='init_plan', title='Summary page', page_kind='dashboard', emphasis='analytics-first')
  )
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

  assert binding.parent_for('fact') == 'summary_region_fact_grid'
  assert binding.parent_for('text') == 'summary_region_fact_grid'
  assert 'summary_region_header' in component_ids
  assert 'summary_region_fact_grid' in component_ids


def test_actions_region_uses_stack_in_side_rail() -> None:
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

  assert compiler.role_slots['actions'] == 'actions_bucket'
  assert binding.parent_for('action_primary') == 'actions_region_action_primary'
  assert binding.parent_for('action_secondary') == 'actions_region_action_secondary'
  assert 'actions_region_action_primary' in component_ids
  assert 'actions_region_action_secondary' in component_ids


def test_form_action_first_routes_actions_to_footer_bucket() -> None:
  compiler = SkeletonCompiler()
  init_frames = compiler.apply(
      InitPlanDelta(
          event='init_plan',
          title='Form',
          page_kind='form',
          emphasis='action-first',
          layout_hint='hero_plus_action_panel',
      )
  )
  init_component_ids = _slot_component_ids(init_frames)

  assert compiler.role_slots['actions'] == 'actions_footer_bucket'
  assert 'actions_footer_bucket' in init_component_ids

  frames = compiler.apply(AddRegionDelta(event='add_region', id='actions_form', role='actions', title='Submit'))
  binding = compiler.regions['actions_form']
  component_ids = _slot_component_ids(frames)
  assert binding.parent_for('action_primary') == 'actions_form_action_primary'
  assert binding.parent_for('action_secondary') == 'actions_form_action_secondary'
  assert 'actions_form_action_primary' in component_ids


def test_pending_region_deltas_flush_through_semantic_slot_mapping() -> None:
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
  assert 'details_region_fact_row' in component_ids
  assert 'details_region_action_row' in component_ids
  assert 'details_cta' in component_ids
  assert 'details_fact' in component_ids
