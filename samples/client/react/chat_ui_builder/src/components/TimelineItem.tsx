import {memo, type PropsWithChildren} from 'react';
import type {A2UIComponentProps} from '@a2ui/react';

export const TimelineItem = memo(function TimelineItem({children}: PropsWithChildren<A2UIComponentProps<any>>) {
  return (
    <li className="a2ui-timeline-item">
      <span className="a2ui-timeline-item__dot" aria-hidden="true" />
      <span className="a2ui-timeline-item__line" aria-hidden="true" />
      <div className="a2ui-timeline-item__content">{children}</div>
    </li>
  );
});
