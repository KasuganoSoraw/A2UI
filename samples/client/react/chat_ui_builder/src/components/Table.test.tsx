import React from 'react';
import {render, screen} from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import {describe, expect, it, vi} from 'vitest';

import {Table, resolveTableCellRender} from './Table';

vi.mock('@a2ui/react', () => ({
  useA2UIComponent: () => ({
    getValue: () => null,
  }),
}));

describe('resolveTableCellRender', () => {
  it('handles primitive cell', () => {
    const rendered = resolveTableCellRender('3');
    expect(rendered.text).toBe('3');
    expect(rendered.weightClassName).toBeUndefined();
  });

  it('handles object cell and maps class', () => {
    const rendered = resolveTableCellRender({value: '3', visual_weight: 4});
    expect(rendered.text).toBe('3');
    expect(rendered.weightClassName).toBe('a2ui-table-cell-weight-4');
  });
});

describe('Table component cell rendering', () => {
  it('renders primitive cell as plain text', () => {
    render(
      <Table
        node={{
          properties: {
            spec: {
              columns: [{key: 'alarmLevel', label: '告警等级'}],
              rows: [{alarmLevel: '3'}],
            },
          },
        } as any}
        surfaceId="main"
      />
    );

    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.queryByText('3')?.className ?? '').not.toContain('a2ui-table-cell-weight-');
  });

  it('renders object cell value and weight class', () => {
    render(
      <Table
        node={{
          properties: {
            spec: {
              columns: [{key: 'alarmLevel', label: '告警等级'}],
              rows: [{alarmLevel: {value: '3', visual_weight: 5}}],
            },
          },
        } as any}
        surfaceId="main"
      />
    );

    const weighted = screen.getByText('3');
    expect(weighted).toHaveClass('a2ui-table-cell-weight-5');
  });
});
