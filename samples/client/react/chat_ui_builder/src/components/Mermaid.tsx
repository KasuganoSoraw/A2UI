import {memo, useEffect, useMemo, useRef, useState} from 'react';
import {useA2UIComponent} from '@a2ui/react';
import type {A2UIComponentProps} from '@a2ui/react';
import mermaid from 'mermaid';

type MermaidDiagramType = 'flowchart' | 'sequenceDiagram' | 'stateDiagram-v2' | 'erDiagram' | 'classDiagram';

interface MermaidSpec {
  title?: string;
  diagramType: MermaidDiagramType;
  definition: string;
}

interface SpecBinding {
  path?: string;
  literal?: unknown;
  literalString?: string;
  valueString?: string;
}

interface MermaidNodeProps {
  spec?: string | MermaidSpec | SpecBinding;
}

let initialized = false;
let renderCounter = 0;

function isMermaidSpec(value: unknown): value is MermaidSpec {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<MermaidSpec>;
  return typeof candidate.diagramType === 'string' && typeof candidate.definition === 'string';
}

function extractSpecCandidate(value: unknown): string | MermaidSpec | null {
  if (value == null) return null;
  if (typeof value === 'string') return value;
  if (isMermaidSpec(value)) return value;
  if (typeof value !== 'object') return String(value);

  const binding = value as SpecBinding;
  if (typeof binding.literalString === 'string') return binding.literalString;
  if (typeof binding.valueString === 'string') return binding.valueString;
  if (binding.literal != null) return extractSpecCandidate(binding.literal);

  return null;
}

function parseSpec(raw: string | MermaidSpec | null): MermaidSpec | null {
  if (!raw) return null;
  if (isMermaidSpec(raw)) return raw;

  try {
    const parsed = JSON.parse(raw) as unknown;
    return isMermaidSpec(parsed) ? parsed : null;
  } catch (error) {
    console.warn('[Mermaid] Failed to parse spec payload:', error, raw);
    return null;
  }
}

function buildMermaidSource(spec: MermaidSpec): string {
  const definition = spec.definition.trim();
  if (!definition) return '';
  if (definition.startsWith(spec.diagramType)) return definition;
  return `${spec.diagramType}\n${definition}`;
}

export const Mermaid = memo(function Mermaid({node, surfaceId}: A2UIComponentProps<any>) {
  const {getValue} = useA2UIComponent(node, surfaceId);
  const props = node.properties as MermaidNodeProps;
  const canvasRef = useRef<HTMLDivElement | null>(null);
  const [renderError, setRenderError] = useState(false);

  const rawSpecValue =
    props.spec && typeof props.spec === 'object' && 'path' in props.spec && props.spec.path
      ? getValue(props.spec.path)
      : props.spec;

  const specSource = extractSpecCandidate(rawSpecValue);
  const spec = parseSpec(specSource);

  const source = useMemo(() => (spec ? buildMermaidSource(spec) : ''), [spec]);

  useEffect(() => {
    if (!spec || !source || !canvasRef.current) {
      if (canvasRef.current) canvasRef.current.innerHTML = '';
      setRenderError(false);
      return;
    }

    if (!initialized) {
      mermaid.initialize({startOnLoad: false, securityLevel: 'loose'});
      initialized = true;
    }

    let disposed = false;
    setRenderError(false);
    const target = canvasRef.current;
    const renderId = `a2ui-mermaid-${renderCounter++}`;

    mermaid
      .render(renderId, source)
      .then((result) => {
        if (disposed || !target) return;
        target.innerHTML = result.svg;
      })
      .catch((error) => {
        console.warn('[Mermaid] Failed to render diagram:', error, source);
        if (!disposed) setRenderError(true);
      });

    return () => {
      disposed = true;
      if (target) target.innerHTML = '';
    };
  }, [source, spec]);

  if (!spec) {
    return (
      <div className="a2ui-mermaid">
        <div className="a2ui-mermaid-empty">图表数据暂不可用</div>
      </div>
    );
  }

  if (!source) {
    return (
      <div className="a2ui-mermaid">
        <div className="a2ui-mermaid-empty">暂无图形定义</div>
      </div>
    );
  }

  return (
    <div className="a2ui-mermaid">
      <div className="a2ui-mermaid-card">
        {spec.title ? <div className="a2ui-mermaid-title">{spec.title}</div> : null}
        {renderError ? (
          <div className="a2ui-mermaid-empty">Mermaid 图渲染失败</div>
        ) : (
          <div className="a2ui-mermaid-canvas" ref={canvasRef} />
        )}
      </div>
    </div>
  );
});
