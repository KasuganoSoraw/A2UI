import {memo} from 'react';
import {useA2UIComponent} from '@a2ui/react';
import type {A2UIComponentProps} from '@a2ui/react';

type ColumnAlign = 'left' | 'center' | 'right';

interface TableColumnSpec {
  key: string;
  label: string;
  width?: number | string;
  align?: ColumnAlign;
  ellipsis?: boolean;
}

export type TableCellPrimitive = string | number | boolean | null;

export interface TableCellObject {
  value: TableCellPrimitive;
  visual_weight?: number;
}

export type TableCellValue = TableCellPrimitive | TableCellObject;

interface TableSpec {
  title?: string;
  columns: TableColumnSpec[];
  rows: Array<Record<string, TableCellValue>>;
  row_key?: string;
  striped?: boolean;
  bordered?: boolean;
}

interface SpecBinding {
  path?: string;
  literal?: unknown;
  literalString?: string;
  valueString?: string;
}

interface TableNodeProps {
  spec?: string | TableSpec | SpecBinding;
}

function isTableSpec(value: unknown): value is TableSpec {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<TableSpec>;
  if (!Array.isArray(candidate.columns) || !Array.isArray(candidate.rows)) return false;

  const columnsValid = candidate.columns.every((column) => {
    if (!column || typeof column !== 'object') return false;
    const item = column as Partial<TableColumnSpec>;
    const alignValid = item.align == null || item.align === 'left' || item.align === 'center' || item.align === 'right';
    const widthValid = item.width == null || typeof item.width === 'number' || typeof item.width === 'string';
    const ellipsisValid = item.ellipsis == null || typeof item.ellipsis === 'boolean';
    return typeof item.key === 'string' && typeof item.label === 'string' && alignValid && widthValid && ellipsisValid;
  });

  const rowsValid = candidate.rows.every((row) => row && typeof row === 'object' && !Array.isArray(row));
  return columnsValid && rowsValid;
}

function extractSpecCandidate(value: unknown): string | TableSpec | null {
  if (value == null) return null;
  if (typeof value === 'string') return value;
  if (isTableSpec(value)) return value;
  if (typeof value !== 'object') return String(value);

  const binding = value as SpecBinding;
  if (typeof binding.literalString === 'string') return binding.literalString;
  if (typeof binding.valueString === 'string') return binding.valueString;
  if (binding.literal != null) return extractSpecCandidate(binding.literal);

  return null;
}

function parseSpec(raw: string | TableSpec | null): TableSpec | null {
  if (!raw) return null;
  if (isTableSpec(raw)) return raw;

  try {
    const parsed = JSON.parse(raw) as unknown;
    return isTableSpec(parsed) ? parsed : null;
  } catch (error) {
    console.warn('[Table] Failed to parse spec payload:', error, raw);
    return null;
  }
}

function normalizeCellValue(value: unknown): string {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function isTableCellObject(value: unknown): value is TableCellObject {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  if (!('value' in value)) return false;
  const candidate = value as {value: unknown; visual_weight?: unknown};
  const primitiveValid =
    candidate.value === null ||
    typeof candidate.value === 'string' ||
    typeof candidate.value === 'number' ||
    typeof candidate.value === 'boolean';
  const weightValid = candidate.visual_weight == null || typeof candidate.visual_weight === 'number';
  return primitiveValid && weightValid;
}

function normalizeVisualWeight(visualWeight: number | undefined): number | null {
  if (typeof visualWeight !== 'number' || !Number.isFinite(visualWeight)) return null;
  const normalized = Math.trunc(visualWeight);
  if (normalized < 1 || normalized > 5) return null;
  return normalized;
}

export function resolveTableCellRender(cell: TableCellValue | undefined): {text: string; weightClassName?: string} {
  if (isTableCellObject(cell)) {
    const weight = normalizeVisualWeight(cell.visual_weight);
    return {
      text: normalizeCellValue(cell.value),
      weightClassName: weight ? `a2ui-table-cell-weight-${weight}` : undefined,
    };
  }
  return {text: normalizeCellValue(cell)};
}

function renderCell(cell: TableCellValue | undefined) {
  const rendered = resolveTableCellRender(cell);
  if (!rendered.weightClassName) return rendered.text;
  return <span className={rendered.weightClassName}>{rendered.text}</span>;
}

function resolveAlignClass(align?: ColumnAlign): string {
  if (align === 'center') return 'is-align-center';
  if (align === 'right') return 'is-align-right';
  return 'is-align-left';
}

function resolveRowKey(spec: TableSpec, row: Record<string, TableCellValue>, index: number): string {
  if (spec.row_key) {
    const keyValue = row[spec.row_key];
    if (keyValue !== null && keyValue !== undefined && keyValue !== '') return String(keyValue);
  }
  if (row.id !== null && row.id !== undefined && row.id !== '') return String(row.id);
  return `row-${index}`;
}

export const Table = memo(function Table({node, surfaceId}: A2UIComponentProps<any>) {
  const {getValue} = useA2UIComponent(node, surfaceId);
  const props = node.properties as TableNodeProps;

  const rawSpecValue =
    props.spec && typeof props.spec === 'object' && 'path' in props.spec && props.spec.path
      ? getValue(props.spec.path)
      : props.spec;

  const specSource = extractSpecCandidate(rawSpecValue);
  const spec = parseSpec(specSource);

  if (!spec) {
    return (
      <div className="a2ui-table">
        <div className="a2ui-table-empty">表格数据暂不可用</div>
      </div>
    );
  }

  if (spec.columns.length === 0) {
    return (
      <div className="a2ui-table">
        <div className="a2ui-table-empty">表格列定义为空</div>
      </div>
    );
  }

  const tableClassName = [
    'a2ui-table-element',
    spec.striped ? 'is-striped' : '',
    spec.bordered ? 'is-bordered' : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className="a2ui-table">
      <div className="a2ui-table-card">
        {spec.title ? <div className="a2ui-table-title">{spec.title}</div> : null}
        <div className="a2ui-table-scroll">
          <table className={tableClassName}>
            <thead>
              <tr>
                {spec.columns.map((column) => {
                  const alignClass = resolveAlignClass(column.align);
                  const ellipsisClass = column.ellipsis ? 'is-ellipsis' : '';
                  const widthStyle = column.width !== undefined ? {width: column.width} : undefined;
                  return (
                    <th key={column.key} className={[alignClass, ellipsisClass].filter(Boolean).join(' ')} style={widthStyle}>
                      {column.label}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {spec.rows.length === 0 ? (
                <tr>
                  <td colSpan={spec.columns.length} className="a2ui-table-empty">暂无数据</td>
                </tr>
              ) : (
                spec.rows.map((row, index) => {
                  const rowKey = resolveRowKey(spec, row, index);
                  return (
                    <tr key={rowKey}>
                      {spec.columns.map((column) => {
                        const alignClass = resolveAlignClass(column.align);
                        const ellipsisClass = column.ellipsis ? 'is-ellipsis' : '';
                        const widthStyle = column.width !== undefined ? {width: column.width} : undefined;
                        return (
                          <td
                            key={`${rowKey}-${column.key}`}
                            className={[alignClass, ellipsisClass].filter(Boolean).join(' ')}
                            style={widthStyle}
                          >
                            {renderCell(row[column.key])}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
});
