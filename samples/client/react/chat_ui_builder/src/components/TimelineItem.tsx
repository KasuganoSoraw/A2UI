import {memo} from 'react';
import {ComponentNode, useA2UIComponent} from '@a2ui/react';
import type {A2UIComponentProps, Types} from '@a2ui/react';

interface TimelineItemProperties {
  child?: unknown;
  children?: unknown;
  timestamp?: unknown;
  placement?: unknown;
  center?: unknown;
  color?: unknown;
}

export const TimelineItem = memo(function TimelineItem({node, surfaceId}: A2UIComponentProps<any>) {
  useA2UIComponent(node, surfaceId);

  const props = node.properties as TimelineItemProperties;
  void props.timestamp;
  void props.placement;
  void props.center;
  void props.color;

  const rawChildren = props.child ?? props.children;
  const children = Array.isArray(rawChildren) ? rawChildren : rawChildren ? [rawChildren] : [];

  const hostStyle: React.CSSProperties =
    node.weight !== undefined ? ({'--weight': node.weight} as React.CSSProperties) : {};

  return (
    <li className="a2ui-timeline-item" style={hostStyle}>
      <span className="a2ui-timeline-item__dot" aria-hidden="true" />
      <span className="a2ui-timeline-item__line" aria-hidden="true" />
      <div className="a2ui-timeline-item__content">
        {children.map((child, index) => {
          const childId =
            typeof child === 'object' && child !== null && 'id' in child
              ? (child as Types.AnyComponentNode).id
              : `child-${index}`;
          const childNode =
            typeof child === 'object' && child !== null && 'type' in child
              ? (child as Types.AnyComponentNode)
              : null;

          return <ComponentNode key={childId} node={childNode} surfaceId={surfaceId} />;
        })}
      </div>
    </li>
  );
});
