import {memo, useEffect, useMemo, useRef, useState} from 'react';
import {useA2UIComponent} from '@a2ui/react';
import type {A2UIComponentProps} from '@a2ui/react';
import {cn} from '../lib/cn';

type DiagramNodeKind = 'start' | 'process' | 'decision' | 'end';

interface DiagramNode {
  id: string;
  label: string;
  column: number;
  lane: number;
  kind: DiagramNodeKind;
}

interface DiagramEdge {
  from_id: string;
  to_id: string;
  label?: string;
}

interface DiagramSpec {
  title: string;
  nodes: DiagramNode[];
  edges: DiagramEdge[];
}

interface SpecBinding {
  path?: string;
  literal?: unknown;
  literalString?: string;
  valueString?: string;
}

interface FlowDiagramNodeProps {
  spec?: string | DiagramSpec | SpecBinding;
}

const nodeTone: Record<DiagramNodeKind, string> = {
  start: 'border-emerald-300 bg-emerald-50',
  process: 'border-slate-200 bg-white',
  decision: 'border-amber-300 bg-amber-50',
  end: 'border-emerald-300 bg-emerald-50',
};

function isDiagramSpec(value: unknown): value is DiagramSpec {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<DiagramSpec>;
  return typeof candidate.title === 'string' && Array.isArray(candidate.nodes) && Array.isArray(candidate.edges);
}

function extractSpecCandidate(value: unknown): string | DiagramSpec | null {
  if (value == null) return null;
  if (typeof value === 'string') return value;
  if (isDiagramSpec(value)) return value;
  if (typeof value !== 'object') return String(value);

  const binding = value as SpecBinding;
  if (typeof binding.literalString === 'string') return binding.literalString;
  if (typeof binding.valueString === 'string') return binding.valueString;
  if (binding.literal != null) return extractSpecCandidate(binding.literal);

  return null;
}

function parseSpec(raw: string | DiagramSpec | null): DiagramSpec | null {
  if (!raw) return null;
  if (isDiagramSpec(raw)) return raw;

  try {
    const parsed = JSON.parse(raw) as unknown;
    return isDiagramSpec(parsed) ? parsed : null;
  } catch (error) {
    console.warn('[FlowDiagram] Failed to parse spec payload:', error, raw);
    return null;
  }
}

export const FlowDiagram = memo(function FlowDiagram({
  node,
  surfaceId,
}: A2UIComponentProps<any>) {
  const {getValue} = useA2UIComponent(node, surfaceId);
  const canvasRef = useRef<HTMLDivElement | null>(null);
  const [canvasWidth, setCanvasWidth] = useState(0);
  const props = node.properties as FlowDiagramNodeProps;
  const rawSpecValue =
    props.spec && typeof props.spec === 'object' && 'path' in props.spec && props.spec.path
      ? getValue(props.spec.path)
      : props.spec;
  const specSource = extractSpecCandidate(rawSpecValue);
  const spec = parseSpec(specSource);

  useEffect(() => {
    const element = canvasRef.current;
    if (!element) return;

    const updateWidth = () => setCanvasWidth(element.clientWidth);
    updateWidth();

    const observer = new ResizeObserver(() => updateWidth());
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  const layout = useMemo(() => {
    if (!spec) return null;
    const maxColumn = Math.max(...spec.nodes.map((item) => item.column), 0);
    const maxLane = Math.max(...spec.nodes.map((item) => item.lane), 0);
    const columnCount = maxColumn + 1;
    const laneCount = maxLane + 1;
    const paddingX = 20;
    const paddingY = 20;
    const columnGap = columnCount >= 6 ? 12 : columnCount >= 4 ? 18 : 26;
    const rowGap = 32;
    const fallbackStageWidth = 980;
    const maxAutoStageWidth = 980;
    const minNodeWidth = 120;
    const preferredNodeWidth = 156;
    const availableStageWidth =
      canvasWidth > 0 ? Math.min(Math.max(canvasWidth - 24, 0), maxAutoStageWidth) : fallbackStageWidth;
    const fittedNodeWidth =
      (availableStageWidth - paddingX * 2 - Math.max(0, columnCount - 1) * columnGap) / columnCount;
    const canFitWithoutScroll = fittedNodeWidth >= minNodeWidth;
    const nodeWidth = canFitWithoutScroll ? Math.min(176, fittedNodeWidth) : preferredNodeWidth;
    const nodeHeight = 96;
    const width = paddingX * 2 + nodeWidth * columnCount + Math.max(0, columnCount - 1) * columnGap;
    const height = paddingY * 2 + nodeHeight * laneCount + Math.max(0, laneCount - 1) * rowGap;
    const positions = new Map<string, {x: number; y: number}>();

    spec.nodes.forEach((item) => {
      positions.set(item.id, {
        x: paddingX + item.column * (nodeWidth + columnGap) + nodeWidth / 2,
        y: paddingY + item.lane * (nodeHeight + rowGap) + nodeHeight / 2,
      });
    });

    return {
      width,
      height,
      nodeWidth,
      nodeHeight,
      positions,
    };
  }, [canvasWidth, spec]);

  if (!spec || !layout) {
    return <div className="rounded-2xl border border-slate-200 bg-slate-50/90 p-5 text-sm text-slate-500">流程图数据暂不可用。</div>;
  }

  return (
    <div className="flow-diagram flex flex-col gap-4">
      <div>
        <p className="mb-1 text-[11px] font-semibold tracking-[0.08em] uppercase text-blue-600">Flow Diagram</p>
        <h3 className="text-base font-semibold text-slate-800">{spec.title}</h3>
      </div>
      <div ref={canvasRef} className="relative overflow-auto rounded-xl border border-slate-200 bg-slate-50/85 p-3">
        <div className="relative" style={{width: layout.width, height: layout.height}}>
          <svg className="pointer-events-none absolute inset-0 z-[1] block overflow-visible" viewBox={`0 0 ${layout.width} ${layout.height}`} width={layout.width} height={layout.height}>
            <defs>
              <marker id={`flow-diagram-arrow-${node.id}`} markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
              </marker>
            </defs>
            {spec.edges.map((edge) => {
              const from = layout.positions.get(edge.from_id);
              const to = layout.positions.get(edge.to_id);
              if (!from || !to) return null;
              const midX = (from.x + to.x) / 2;
              const path = `M ${from.x} ${from.y} C ${midX} ${from.y}, ${midX} ${to.y}, ${to.x} ${to.y}`;
              return (
                <g key={`${edge.from_id}-${edge.to_id}-${edge.label ?? ''}`}>
                  <path d={path} className="fill-none stroke-blue-500 stroke-[2.5] [stroke-linecap:round] [stroke-linejoin:round]" markerEnd={`url(#flow-diagram-arrow-${node.id})`} />
                </g>
              );
            })}
          </svg>

          {spec.edges.map((edge) => {
            if (!edge.label) return null;
            const from = layout.positions.get(edge.from_id);
            const to = layout.positions.get(edge.to_id);
            if (!from || !to) return null;
            return (
              <div
                key={`label-${edge.from_id}-${edge.to_id}-${edge.label}`}
                className="absolute z-[2] -translate-x-1/2 -translate-y-1/2 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-[11px] font-semibold leading-4 text-slate-500"
                style={{
                  left: (from.x + to.x) / 2,
                  top: (from.y + to.y) / 2 - 12,
                  minWidth: Math.max(42, edge.label.length * 16),
                }}
              >
                {edge.label}
              </div>
            );
          })}

          {spec.nodes.map((item) => (
            <div
              key={item.id}
              className={cn(
                'absolute z-[3] flex min-h-24 flex-col justify-center gap-2 rounded-xl border p-3.5 shadow-sm',
                nodeTone[item.kind]
              )}
              style={{
                left: layout.positions.get(item.id)!.x - layout.nodeWidth / 2,
                top: layout.positions.get(item.id)!.y - layout.nodeHeight / 2,
                width: layout.nodeWidth,
              }}
            >
              <span className="w-fit rounded-full bg-blue-100 px-2.5 py-1 text-[10px] font-semibold tracking-[0.06em] uppercase text-blue-700">{item.kind}</span>
              <strong className="text-sm leading-5 text-slate-800">{item.label}</strong>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});
