import {memo, useMemo} from 'react';
import {useA2UIComponent} from '@a2ui/react';
import type {A2UIComponentProps} from '@a2ui/react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart as RechartsLineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

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

const METRIC_COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

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

function buildDisplayData(spec: LineChartSpec) {
  return spec.chartData.map((row) => {
    const normalized: Record<string, string | number | null> = {
      __dimension: String(row[spec.settings.dimension] ?? ''),
    };

    spec.settings.metrics.forEach((metric) => {
      normalized[metric] = parseNumber(row[metric]);
    });

    return normalized;
  });
}

function getRenderableMetrics(metrics: string[], rows: Array<Record<string, string | number | null>>) {
  return metrics.filter((metric) => rows.some((row) => typeof row[metric] === 'number'));
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

  const chartWidthStyle = spec?.width ? {width: spec.width} : undefined;

  const displayData = useMemo(() => {
    if (!spec || !Array.isArray(spec.chartData)) return [];
    return buildDisplayData(spec);
  }, [spec]);

  const metrics = useMemo(() => {
    if (!spec || !Array.isArray(spec.settings.metrics)) return [];
    return getRenderableMetrics(spec.settings.metrics, displayData);
  }, [displayData, spec]);

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

  if (metrics.length === 0) {
    return (
      <div className="a2ui-line-chart">
        <div className="a2ui-line-chart-empty">暂无可绘制数据</div>
      </div>
    );
  }

  return (
    <div className="a2ui-line-chart" style={chartWidthStyle}>
      <div className="a2ui-line-chart-card">
        {spec.title ? <div className="a2ui-line-chart-title">{spec.title}</div> : null}

        <div className="a2ui-line-chart-canvas">
          <ResponsiveContainer width="100%" height="100%">
            <RechartsLineChart data={displayData} margin={{top: 12, right: 12, left: 0, bottom: 10}}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="__dimension" tick={{fill: '#64748b', fontSize: 12}} minTickGap={16} />
              <YAxis tick={{fill: '#64748b', fontSize: 12}} width={46} />
              <Tooltip
                contentStyle={{borderRadius: 8, borderColor: '#dbe3ef'}}
                formatter={(value: number | string | null) => (value == null ? '--' : String(value))}
              />
              <Legend wrapperStyle={{fontSize: 12}} />

              {metrics.map((metric, index) => (
                <Line
                  key={metric}
                  type="monotone"
                  dataKey={metric}
                  stroke={METRIC_COLORS[index % METRIC_COLORS.length]}
                  strokeWidth={2.5}
                  dot={Boolean(spec.settings.markPoint)}
                  connectNulls
                  isAnimationActive={false}
                />
              ))}
            </RechartsLineChart>
          </ResponsiveContainer>
        </div>

        <div className="a2ui-line-chart-axis-titles">
          <span>{spec.settings.xTitle ?? ''}</span>
          <span>{spec.settings.yTitle ?? ''}</span>
        </div>
      </div>
    </div>
  );
});
