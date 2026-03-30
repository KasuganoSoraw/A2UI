import {memo, type PropsWithChildren} from 'react';
import type {A2UIComponentProps} from '@a2ui/react';

export const Timeline = memo(function Timeline({children}: PropsWithChildren<A2UIComponentProps<any>>) {
  return <ol className="a2ui-timeline">{children}</ol>;
});
