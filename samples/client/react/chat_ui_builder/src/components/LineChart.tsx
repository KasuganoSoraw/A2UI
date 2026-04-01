import {memo} from 'react';
import {useA2UIComponent} from '@a2ui/react';
import type {A2UIComponentProps} from '@a2ui/react';

type MetricValue = string | number | boolean | null;

interface LineChartSettings {
  dimension: string;
  xTitle?: string;
  yTitle?: string;
  metrics: string[];
  markPoint?: boolean;
}

interface LineChartSpec {
  title?: string;
  width?: string;
  settings: LineChartSettings;
  chartData: Array<Record<string, MetricValue>>;
}

interface SpecBinding {
  path?: string;
  literal?: unknown;
  literalString?: string;
  valueString?: string;
}

interface LineChartNodeProps {
  spec?: string | LineChartSpec | SpecBinding;
}

interface MetricSeries {
  metric: string;
  points: Array<{x: number; y: number; value: number; index: number}>;
}

const CANVAS_WIDTH = 720;
const CANVAS_HEIGHT = 260;
const PADDING_LEFT = 56;
const PADDING_RIGHT = 20;
const PADDING_TOP = 20;
const PADDING_BOTTOM = 40;

function isLineChartSpec(value: unknown): value is LineChartSpec {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<LineChartSpec>;
  if (!candidate.settings || typeof candidate.settings !== 'object') return false;
  if (!Array.isArray(candidate.chartData)) return false;

  const settings = candidate.settings as Partial<LineChartSettings>;
  return typeof settings.dimension === 'string' && Array.isArray(settings.metrics);
}

function extractSpecCandidate(value: unknown): string | LineChartSpec | null {
  if (value == null) return null;
  if (typeof value === 'string') return value;
  if (isLineChartSpec(value)) return value;
  if (typeof value !== 'object') return String(value);

  const binding = value as SpecBinding;
  if (typeof binding.literalString === 'string') return binding.literalString;
  if (typeof binding.valueString === 'string') return binding.valueString;
  if (binding.literal != null) return extractSpecCandidate(binding.literal);

  return null;
}

function parseSpec(raw: string | LineChartSpec | null): LineChartSpec | null {
  if (!raw) return null;
  if (isLineChartSpec(raw)) return raw;

  try {
    const parsed = JSON.parse(raw) as unknown;
    return isLineChartSpec(parsed) ? parsed : null;
  } catch (error) {
    console.warn('[LineChart] Failed to parse spec payload:', error, raw);
    return null;
  }
}

function parseNumber(value: MetricValue): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim()) {
    const numberValue = Number(value);
    return Number.isFinite(numberValue) ? numberValue : null;
  }
  return null;
}

function buildMetricSeries(spec: LineChartSpec): MetricSeries[] {
  const metrics = spec.settings.metrics;
  const chartData = spec.chartData;
  if (chartData.length === 0) return [];

  const values: number[] = [];
  const normalizedRows = chartData.map((row) =>
    metrics.map((metric) => parseNumber(row[metric]))
  );
  normalizedRows.forEach((rowValues) => {
    rowValues.forEach((value) => {
      if (value !== null) values.push(value);
    });
  });

  if (values.length === 0) return [];

  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const valueSpan = maxValue - minValue || 1;
  const innerWidth = CANVAS_WIDTH - PADDING_LEFT - PADDING_RIGHT;
  const innerHeight = CANVAS_HEIGHT - PADDING_TOP - PADDING_BOTTOM;
  const xStep = chartData.length > 1 ? innerWidth / (chartData.length - 1) : 0;

  return metrics.map((metric, metricIndex) => {
    const points: MetricSeries['points'] = [];
    chartData.forEach((row, index) => {
      const value = normalizedRows[index][metricIndex];
      if (value === null) return;
      const x = PADDING_LEFT + xStep * index;
      const y = PADDING_TOP + ((maxValue - value) / valueSpan) * innerHeight;
      points.push({x, y, value, index});
    });
    return {metric, points};
  });
}

function colorForMetric(index: number): string {
  const palette = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];
  return palette[index % palette.length];
}

export const LineChart = memo(function LineChart({node, surfaceId}: A2UIComponentProps<any>) {
  const {getValue} = useA2UIComponent(node, surfaceId);
  const props = node.properties as LineChartNodeProps;

  const rawSpecValue =
    props.spec && typeof props.spec === 'object' && 'path' in props.spec && props.spec.path
      ? getValue(props.spec.path)
      : props.spec;

  const specSource = extractSpecCandidate(rawSpecValue);
  const spec = parseSpec(specSource);

  if (!spec) {
    return (
      <div className="a2ui-line-chart">
        <div className="a2ui-line-chart-empty">图表数据暂不可用</div>
      </div>
    );
  }

  if (!Array.isArray(spec.settings.metrics) || spec.settings.metrics.length === 0) {
    return (
      <div className="a2ui-line-chart">
        <div className="a2ui-line-chart-empty">图表指标为空</div>
      </div>
    );
  }

  if (!Array.isArray(spec.chartData) || spec.chartData.length === 0) {
    return (
      <div className="a2ui-line-chart">
        <div className="a2ui-line-chart-empty">暂无图表数据</div>
      </div>
    );
  }

  const series = buildMetricSeries(spec);
  const hasDrawableSeries = series.some((item) => item.points.length > 0);
  if (!hasDrawableSeries) {
    return (
      <div className="a2ui-line-chart">
        <div className="a2ui-line-chart-empty">暂无可绘制数据</div>
      </div>
    );
  }

  const chartWidthStyle = spec.width ? {width: spec.width} : undefined;
  const dimensionValues = spec.chartData.map((row) => String(row[spec.settings.dimension] ?? ''));

  return (
    <div className="a2ui-line-chart" style={chartWidthStyle}>
      <div className="a2ui-line-chart-card">
        {spec.title ? <div className="a2ui-line-chart-title">{spec.title}</div> : null}

        <div className="a2ui-line-chart-legend">
          {series.map((item, index) => (
            <span key={item.metric}>
              <i style={{backgroundColor: colorForMetric(index)}} />
              {item.metric}
            </span>
          ))}
        </div>

        <div className="a2ui-line-chart-canvas">
          <svg viewBox={`0 0 ${CANVAS_WIDTH} ${CANVAS_HEIGHT}`} preserveAspectRatio="none">
            <line x1={PADDING_LEFT} y1={PADDING_TOP} x2={PADDING_LEFT} y2={CANVAS_HEIGHT - PADDING_BOTTOM} stroke="#d1d5db" />
            <line
              x1={PADDING_LEFT}
              y1={CANVAS_HEIGHT - PADDING_BOTTOM}
              x2={CANVAS_WIDTH - PADDING_RIGHT}
              y2={CANVAS_HEIGHT - PADDING_BOTTOM}
              stroke="#d1d5db"
            />

            {series.map((item, index) => {
              if (item.points.length === 0) return null;
              const color = colorForMetric(index);
              const polylinePoints = item.points.map((point) => `${point.x},${point.y}`).join(' ');
              return (
                <g key={item.metric}>
                  <polyline fill="none" stroke={color} strokeWidth="2.5" points={polylinePoints} />
                  {spec.settings.markPoint
                    ? item.points.map((point) => (
                        <circle key={`${item.metric}-${point.index}`} cx={point.x} cy={point.y} r="3" fill={color} />
                      ))
                    : null}
                </g>
              );
            })}
          </svg>
        </div>

        <div className="a2ui-line-chart-axis-labels">
          {dimensionValues.map((label, index) => (
            <span key={`${label}-${index}`}>{label}</span>
          ))}
        </div>

        <div className="a2ui-line-chart-axis-titles">
          <span>{spec.settings.xTitle ?? ''}</span>
          <span>{spec.settings.yTitle ?? ''}</span>
        </div>
      </div>
    </div>
  );
});
