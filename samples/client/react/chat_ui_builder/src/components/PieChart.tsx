import {memo} from 'react';
import {useA2UIComponent} from '@a2ui/react';
import type {A2UIComponentProps} from '@a2ui/react';
import {
  Cell,
  Legend,
  Pie,
  PieChart as RechartsPieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

type PieSlice = {
  value: number;
  name: string;
  selected?: boolean;
};

type PieSeries = {
  data: PieSlice[];
  radius?: string;
};

interface PieChartSpec {
  title?: string;
  width?: string;
  settings?: Record<string, unknown>;
  chartData: PieSeries[];
}

interface SpecBinding {
  path?: string;
  literal?: unknown;
  literalString?: string;
  valueString?: string;
}

interface PieChartNodeProps {
  spec?: string | PieChartSpec | SpecBinding;
}

const SLICE_COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#14b8a6'];

function isPieChartSpec(value: unknown): value is PieChartSpec {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<PieChartSpec>;
  return Array.isArray(candidate.chartData);
}

function extractSpecCandidate(value: unknown): string | PieChartSpec | null {
  if (value == null) return null;
  if (typeof value === 'string') return value;
  if (isPieChartSpec(value)) return value;
  if (typeof value !== 'object') return String(value);

  const binding = value as SpecBinding;
  if (typeof binding.literalString === 'string') return binding.literalString;
  if (typeof binding.valueString === 'string') return binding.valueString;
  if (binding.literal != null) return extractSpecCandidate(binding.literal);

  return null;
}

function parseSpec(raw: string | PieChartSpec | null): PieChartSpec | null {
  if (!raw) return null;
  if (isPieChartSpec(raw)) return raw;

  try {
    const parsed = JSON.parse(raw) as unknown;
    return isPieChartSpec(parsed) ? parsed : null;
  } catch (error) {
    console.warn('[PieChart] Failed to parse spec payload:', error, raw);
    return null;
  }
}

function normalizeSeries(series: PieSeries[]): PieSeries[] {
  return series
    .map((item) => ({
      radius: item.radius,
      data: (item.data || []).filter((slice) => Number.isFinite(slice.value) && !!slice.name),
    }))
    .filter((item) => item.data.length > 0);
}

function parseRadius(radius: string | undefined, fallbackOuter: number) {
  if (!radius) return fallbackOuter;
  if (radius.endsWith('%')) {
    const value = Number(radius.slice(0, -1));
    if (Number.isFinite(value)) return `${value}%`;
    return fallbackOuter;
  }
  const numeric = Number(radius);
  return Number.isFinite(numeric) ? numeric : fallbackOuter;
}

export const PieChart = memo(function PieChart({node, surfaceId}: A2UIComponentProps<any>) {
  const {getValue} = useA2UIComponent(node, surfaceId);
  const props = node.properties as PieChartNodeProps;

  const rawSpecValue =
    props.spec && typeof props.spec === 'object' && 'path' in props.spec && props.spec.path
      ? getValue(props.spec.path)
      : props.spec;

  const specSource = extractSpecCandidate(rawSpecValue);
  const spec = parseSpec(specSource);

  if (!spec) {
    return (
      <div className="a2ui-pie-chart">
        <div className="a2ui-pie-chart-empty">图表数据暂不可用</div>
      </div>
    );
  }

  if (!Array.isArray(spec.chartData) || spec.chartData.length === 0) {
    return (
      <div className="a2ui-pie-chart">
        <div className="a2ui-pie-chart-empty">暂无图表数据</div>
      </div>
    );
  }

  const series = normalizeSeries(spec.chartData);
  if (series.length === 0) {
    return (
      <div className="a2ui-pie-chart">
        <div className="a2ui-pie-chart-empty">暂无可绘制数据</div>
      </div>
    );
  }

  const chartWidthStyle = spec.width ? {width: spec.width} : undefined;

  return (
    <div className="a2ui-pie-chart" style={chartWidthStyle}>
      <div className="a2ui-pie-chart-card">
        {spec.title ? <div className="a2ui-pie-chart-title">{spec.title}</div> : null}

        <div className="a2ui-pie-chart-canvas">
          <ResponsiveContainer width="100%" height="100%">
            <RechartsPieChart>
              <Tooltip formatter={(value: number | string) => String(value)} />
              <Legend />
              {series.map((item, seriesIndex) => {
                const inner = seriesIndex === 0 ? 0 : 24 + seriesIndex * 36;
                const fallbackOuter = 56 + seriesIndex * 36;
                const outer = parseRadius(item.radius, fallbackOuter);
                return (
                  <Pie
                    key={`series-${seriesIndex}`}
                    data={item.data}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={inner}
                    outerRadius={outer}
                    paddingAngle={2}
                    isAnimationActive={false}
                  >
                    {item.data.map((slice, sliceIndex) => {
                      const color = SLICE_COLORS[sliceIndex % SLICE_COLORS.length];
                      return (
                        <Cell
                          key={`${slice.name}-${sliceIndex}`}
                          fill={color}
                          stroke={slice.selected ? '#111827' : '#ffffff'}
                          strokeWidth={slice.selected ? 3 : 1}
                        />
                      );
                    })}
                  </Pie>
                );
              })}
            </RechartsPieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
});
