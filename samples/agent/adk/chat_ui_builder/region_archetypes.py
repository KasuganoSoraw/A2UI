from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal

from models import A2UIFrame, AddRegionDelta, AddSectionDelta, AddTextDelta

EmitLowLevel = Callable[[object], list[A2UIFrame]]


@dataclass(frozen=True)
class ArrangementSemantics:
  body_layout: Literal['column', 'row', 'none'] = 'column'
  actions_layout: Literal['row', 'column'] = 'row'
  facts_layout: Literal['row', 'column'] = 'row'


@dataclass
class RegionBuildContext:
  slot_parent: str
  delta: AddRegionDelta
  page_kind: str
  emphasis: str
  layout_hint: str
  arrangement: ArrangementSemantics
  presentation_variant: str = 'standard'


@dataclass
class RegionBuildResult:
  archetype: str
  frames: list[A2UIFrame] = field(default_factory=list)
  slot_parents: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SlotSpec:
  name: str
  section_id: str
  layout: str
  order: int
  appearance: str | None = None


class RegionArchetypeBuilder:
  archetype_name = 'details_group'

  def build(self, context: RegionBuildContext, emit: EmitLowLevel) -> RegionBuildResult:
    raise NotImplementedError

  def _base_region(
      self,
      context: RegionBuildContext,
      emit: EmitLowLevel,
      *,
      region_layout: str = 'Column',
      include_body_slot: bool = True,
      slot_specs: list[SlotSpec] | None = None,
      slot_parents: dict[str, str] | None = None,
  ) -> RegionBuildResult:
    region_id = context.delta.id
    frames = emit(
        AddSectionDelta(
            event='add_section',
            id=region_id,
            parent_id=context.slot_parent,
            layout=region_layout,
        )
    )

    resolved_slot_parents = {
        'text': region_id,
        'fact': region_id,
        'action_primary': region_id,
        'action_secondary': region_id,
        'input': region_id,
        'image': region_id,
        'list_item': region_id,
        'flow': region_id,
        'divider': region_id,
    }

    content_parent = region_id
    if context.delta.title or context.delta.description:
      header_id = f'{region_id}_header'
      frames.extend(
          emit(
              AddSectionDelta(
                  event='add_section',
                  id=header_id,
                  parent_id=region_id,
                  layout='Column',
                  order=10,
              )
          )
      )
      if context.delta.title:
        frames.extend(
            emit(
                AddTextDelta(
                    event='add_text',
                    id=f'{header_id}_title',
                    parent_id=header_id,
                    text=context.delta.title,
                    usage_hint='h2',
                )
            )
        )
      if context.delta.description:
        frames.extend(
            emit(
                AddTextDelta(
                    event='add_text',
                    id=f'{header_id}_description',
                    parent_id=header_id,
                    text=context.delta.description,
                    usage_hint='body',
                )
            )
        )
      if include_body_slot:
        body_layout = 'Column' if context.arrangement.body_layout == 'column' else 'Row'
        body_id = f'{region_id}_body'
        frames.extend(
            emit(
                AddSectionDelta(
                    event='add_section',
                    id=body_id,
                    parent_id=region_id,
                    layout=body_layout,
                    order=20,
                )
            )
        )
        content_parent = body_id

    resolved_slot_parents['text'] = content_parent
    resolved_slot_parents['image'] = content_parent
    resolved_slot_parents['divider'] = content_parent

    for spec in slot_specs or []:
      frames.extend(
          emit(
              AddSectionDelta(
                  event='add_section',
                  id=spec.section_id,
                  parent_id=region_id,
                  layout=spec.layout,
                  order=spec.order,
                  appearance=spec.appearance,
              )
          )
      )
      resolved_slot_parents[spec.name] = spec.section_id

    if slot_parents:
      resolved_slot_parents.update(slot_parents)

    return RegionBuildResult(archetype=self.archetype_name, frames=frames, slot_parents=resolved_slot_parents)


class HeroArchetypeBuilder(RegionArchetypeBuilder):
  archetype_name = 'hero_header'

  def build(self, context: RegionBuildContext, emit: EmitLowLevel) -> RegionBuildResult:
    region_id = context.delta.id
    actions_id = f'{region_id}_actions'
    return self._base_region(
        context,
        emit,
        include_body_slot=context.arrangement.body_layout != 'none',
        slot_specs=[
            SlotSpec(
                name='fact',
                section_id=f'{region_id}_facts',
                layout='Row' if context.arrangement.facts_layout == 'row' else 'Column',
                order=30,
                appearance='hero_fact',
            ),
            SlotSpec(
                name='action_primary',
                section_id=actions_id,
                layout='Row' if context.arrangement.actions_layout == 'row' else 'Column',
                order=40,
            ),
        ],
        slot_parents={'action_secondary': actions_id},
    )


class SummaryArchetypeBuilder(RegionArchetypeBuilder):
  archetype_name = 'summary_strip'

  def build(self, context: RegionBuildContext, emit: EmitLowLevel) -> RegionBuildResult:
    region_id = context.delta.id
    facts_id = f'{region_id}_facts'
    return self._base_region(
        context,
        emit,
        include_body_slot=False,
        slot_specs=[
            SlotSpec(
                name='fact',
                section_id=facts_id,
                layout='Row' if context.arrangement.facts_layout == 'row' else 'Column',
                order=20,
            )
        ],
        slot_parents={
            'text': facts_id,
            'image': facts_id,
            'divider': facts_id,
        },
    )


class DetailsArchetypeBuilder(RegionArchetypeBuilder):
  archetype_name = 'details_group'

  def build(self, context: RegionBuildContext, emit: EmitLowLevel) -> RegionBuildResult:
    region_id = context.delta.id
    actions_id = f'{region_id}_actions'
    return self._base_region(
        context,
        emit,
        include_body_slot=True,
        slot_specs=[
            SlotSpec(
                name='fact',
                section_id=f'{region_id}_facts',
                layout='Row' if context.arrangement.facts_layout == 'row' else 'Column',
                order=30,
            ),
            SlotSpec(
                name='action_primary',
                section_id=actions_id,
                layout='Row' if context.arrangement.actions_layout == 'row' else 'Column',
                order=40,
            ),
        ],
        slot_parents={'action_secondary': actions_id},
    )


class ActionsArchetypeBuilder(RegionArchetypeBuilder):
  archetype_name = 'action_panel'

  def build(self, context: RegionBuildContext, emit: EmitLowLevel) -> RegionBuildResult:
    region_id = context.delta.id
    actions_layout = 'Row' if context.arrangement.actions_layout == 'row' else 'Column'
    if context.arrangement.actions_layout == 'row':
      actions_id = f'{region_id}_actions'
      return self._base_region(
          context,
          emit,
          include_body_slot=False,
          slot_specs=[SlotSpec(name='action_primary', section_id=actions_id, layout=actions_layout, order=30)],
          slot_parents={'action_secondary': actions_id},
      )

    return self._base_region(
        context,
        emit,
        include_body_slot=False,
        slot_specs=[
            SlotSpec(name='action_primary', section_id=f'{region_id}_actions_primary', layout=actions_layout, order=30),
            SlotSpec(name='action_secondary', section_id=f'{region_id}_actions_secondary', layout=actions_layout, order=40),
        ],
    )


class WorkflowArchetypeBuilder(RegionArchetypeBuilder):
  archetype_name = 'workflow_panel'

  def build(self, context: RegionBuildContext, emit: EmitLowLevel) -> RegionBuildResult:
    region_id = context.delta.id
    actions_id = f'{region_id}_actions'
    return self._base_region(
        context,
        emit,
        include_body_slot=True,
        slot_specs=[
            SlotSpec(name='flow', section_id=f'{region_id}_flow', layout='Column', order=30),
            SlotSpec(
                name='action_primary',
                section_id=actions_id,
                layout='Row' if context.arrangement.actions_layout == 'row' else 'Column',
                order=40,
            ),
        ],
        slot_parents={'action_secondary': actions_id},
    )


class SupportingArchetypeBuilder(RegionArchetypeBuilder):
  archetype_name = 'supporting_block'

  def build(self, context: RegionBuildContext, emit: EmitLowLevel) -> RegionBuildResult:
    return self._base_region(
        context,
        emit,
        include_body_slot=True,
    )


class ListArchetypeBuilder(RegionArchetypeBuilder):
  archetype_name = 'list_panel'

  def build(self, context: RegionBuildContext, emit: EmitLowLevel) -> RegionBuildResult:
    region_id = context.delta.id
    actions_id = f'{region_id}_actions'
    list_layout = 'Timeline' if context.presentation_variant == 'timeline' else 'List'
    return self._base_region(
        context,
        emit,
        include_body_slot=False,
        slot_specs=[
            SlotSpec(name='list_item', section_id=f'{region_id}_list_items', layout=list_layout, order=30),
            SlotSpec(
                name='action_primary',
                section_id=actions_id,
                layout='Row' if context.arrangement.actions_layout == 'row' else 'Column',
                order=40,
            ),
        ],
        slot_parents={'action_secondary': actions_id},
    )


class FormArchetypeBuilder(RegionArchetypeBuilder):
  archetype_name = 'form_panel'

  def build(self, context: RegionBuildContext, emit: EmitLowLevel) -> RegionBuildResult:
    region_id = context.delta.id
    actions_id = f'{region_id}_actions'
    return self._base_region(
        context,
        emit,
        include_body_slot=True,
        slot_specs=[
            SlotSpec(name='input', section_id=f'{region_id}_inputs', layout='Column', order=30),
            SlotSpec(
                name='action_primary',
                section_id=actions_id,
                layout='Row' if context.arrangement.actions_layout == 'row' else 'Column',
                order=40,
            ),
        ],
        slot_parents={'action_secondary': actions_id},
    )


class RegionArchetypeRegistry:
  def __init__(self) -> None:
    details = DetailsArchetypeBuilder()
    summary = SummaryArchetypeBuilder()
    self._builders: dict[str, RegionArchetypeBuilder] = {
        'hero': HeroArchetypeBuilder(),
        'summary': summary,
        'details': details,
        'workflow': WorkflowArchetypeBuilder(),
        'actions': ActionsArchetypeBuilder(),
        'form': FormArchetypeBuilder(),
        'list': ListArchetypeBuilder(),
        'insights': summary,
        'supporting': SupportingArchetypeBuilder(),
    }
    self._default_builder = details

  def builder_for(self, role: str) -> RegionArchetypeBuilder:
    return self._builders.get(role, self._default_builder)
