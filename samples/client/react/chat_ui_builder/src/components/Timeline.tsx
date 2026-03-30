import {memo} from 'react';
import {ComponentNode, useA2UIComponent} from '@a2ui/react';
import type {A2UIComponentProps, Types} from '@a2ui/react';

export const Timeline = memo(function Timeline({node, surfaceId}: A2UIComponentProps<any>) {
  useA2UIComponent(node, surfaceId);

  const props = node.properties as {children?: unknown};
  const children = Array.isArray(props.children) ? props.children : [];

  const hostStyle: React.CSSProperties =
    node.weight !== undefined ? ({'--weight': node.weight} as React.CSSProperties) : {};

  return (
    <ol className="a2ui-timeline" style={hostStyle}>
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
    </ol>
  );
});
