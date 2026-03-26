import {FormEvent, type Dispatch, type SetStateAction, useCallback, useMemo, useRef, useState} from 'react';
import {A2UIProvider, A2UIRenderer, ComponentRegistry, useA2UIActions} from '@a2ui/react';
import type {Types} from '@a2ui/react';
import {FlowDiagram} from './components/FlowDiagram';
import {SurfaceViewport} from './components/SurfaceViewport';
import {cn} from './lib/cn';
import {buttonVariants, fieldVariants, panelVariants, surfaceVariants} from './lib/viewStyles';

const DEFAULT_API_BASE = 'http://localhost:8010';
const MAX_LOG_ENTRIES = 40;

const EXAMPLES = [
  '请生成一个客户概览卡片，包含姓名 Alice、客户等级 VIP、最近两笔订单，并提供一个“跟进客户”按钮。',
  '请生成一个缺陷分诊面板，包含标题“生产故障”、严重级别“高”、负责人“平台团队”，并添加“立即升级”和“记录备注”两个动作。',
  '请生成一个会议准备表单，包含参会人姓名、会议时间、议程、是否需要录屏，以及一个“提交准备信息”按钮。',
  '请生成一个请假审批流程图，包含提交申请、主管审批、通过、驳回修改四个节点，并在下方放一个“发起审批”按钮。',
];

const registry = ComponentRegistry.getInstance();
if (!registry.has('FlowDiagram')) {
  registry.register('FlowDiagram', {component: FlowDiagram});
}

interface ShellProps {
  onAction: (message: Types.A2UIClientEventMessage) => void;
}

function formatJson(value: unknown) {
  return JSON.stringify(value, null, 2);
}

function pushEntry(setter: Dispatch<SetStateAction<string[]>>, entry: string) {
  setter((prev) => [...prev, entry].slice(-MAX_LOG_ENTRIES));
}

function Shell({onAction}: ShellProps) {
  const {processMessages, clearSurfaces} = useA2UIActions();
  const [input, setInput] = useState(EXAMPLES[0]);
  const [status, setStatus] = useState<'idle' | 'streaming' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [apiBase, setApiBase] = useState(DEFAULT_API_BASE);
  const [history, setHistory] = useState<string[]>([]);
  const [actions, setActions] = useState<string[]>([]);
  const [frames, setFrames] = useState<string[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  const submit = useCallback(
    async (message: string) => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;
      clearSurfaces();
      setFrames([]);
      setStatus('streaming');
      setError(null);
      pushEntry(setHistory, `用户输入：${message}`);
      pushEntry(setHistory, `请求地址：${apiBase}/api/chat/stream`);

      try {
        const response = await fetch(`${apiBase}/api/chat/stream`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({message}),
          signal: controller.signal,
        });

        if (!response.ok || !response.body) {
          throw new Error(`请求失败，状态码 ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const {done, value} = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, {stream: true});
          let newlineIndex = buffer.indexOf('\n');
          while (newlineIndex !== -1) {
            const line = buffer.slice(0, newlineIndex).trim();
            buffer = buffer.slice(newlineIndex + 1);
            if (line) {
              const frame = JSON.parse(line) as Types.ServerToClientMessage;
              pushEntry(setFrames, formatJson(frame));
              processMessages([frame]);
            }
            newlineIndex = buffer.indexOf('\n');
          }
        }

        const tail = buffer.trim();
        if (tail) {
          const frame = JSON.parse(tail) as Types.ServerToClientMessage;
          pushEntry(setFrames, formatJson(frame));
          processMessages([frame]);
        }

        pushEntry(setHistory, '渲染完成：已接收并处理 A2UI 数据帧。');
        setStatus('idle');
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          setStatus('idle');
          pushEntry(setHistory, '上一次请求已取消。');
          return;
        }
        const messageText = err instanceof Error ? err.message : '流式请求失败';
        setStatus('error');
        setError(messageText);
        pushEntry(setHistory, `错误：${messageText}`);
      }
    },
    [apiBase, clearSurfaces, processMessages]
  );

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const trimmed = input.trim();
      if (!trimmed) return;
      await submit(trimmed);
    },
    [input, submit]
  );

  const exampleButtons = useMemo(
    () =>
      EXAMPLES.map((example) => (
        <button key={example} type="button" className={cn(buttonVariants.ghost)} onClick={() => setInput(example)}>
          {example}
        </button>
      )),
    []
  );

  const handleAction = useCallback(
    (message: Types.A2UIClientEventMessage) => {
      onAction(message);
      const action = message.userAction;
      const actionName = action?.name ?? 'unknown';
      const context = action?.context ? formatJson(action.context) : '{}';
      pushEntry(setActions, `动作：${actionName} ${context}`);
      pushEntry(setHistory, `点击动作：${actionName}`);
    },
    [onAction]
  );

  return (
    <div className="grid min-h-screen grid-cols-1 gap-6 p-4 xl:grid-cols-[minmax(360px,460px)_1fr] xl:p-6">
      <aside className={cn(panelVariants.primary, 'flex flex-col gap-5 p-6')}>
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-blue-600">演示</p>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900">聊天式 A2UI 生成器</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            左侧输入中文需求，前端通过 <code>fetch + ReadableStream</code> 接收后端返回的 NDJSON A2UI
            帧，并调用 <code>@a2ui/react</code> 的渲染能力实时更新右侧界面。
          </p>
        </div>

        <div className={cn(panelVariants.info, 'p-4')}>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-slate-700">前端实现说明</p>
          <ul className={fieldVariants.list}>
            <li>
              使用 <code>@a2ui/react</code> 提供的 <code>A2UIProvider</code>、<code>A2UIRenderer</code> 与{' '}
              <code>useA2UIActions</code>。
            </li>
            <li>
              通过 <code>response.body.getReader()</code> 逐行解析 <code>application/x-ndjson</code>。
            </li>
            <li>
              每收到一帧就调用 <code>processMessages([frame])</code>，因此界面会增量更新而不是一次性刷新。
            </li>
          </ul>
        </div>

        <label className={fieldVariants.label}>
          <span>后端地址</span>
          <input className={fieldVariants.input} value={apiBase} onChange={(e) => setApiBase(e.target.value)} />
        </label>

        <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
          <label className={fieldVariants.label}>
            <span>需求描述</span>
            <textarea className={cn(fieldVariants.input, 'min-h-48 resize-y')} value={input} onChange={(e) => setInput(e.target.value)} rows={10} />
          </label>
          <div className="flex flex-wrap gap-3">
            <button type="submit" disabled={status === 'streaming'} className={cn(buttonVariants.primary)}>
              {status === 'streaming' ? '生成中…' : '生成界面'}
            </button>
            <button
              type="button"
              className={buttonVariants.secondary}
              onClick={() => {
                abortRef.current?.abort();
                clearSurfaces();
                setFrames([]);
                pushEntry(setHistory, '已清空画布。');
              }}
            >
              清空画布
            </button>
          </div>
        </form>

        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-slate-700">示例需求</p>
          <div className="flex flex-wrap gap-2">{exampleButtons}</div>
        </div>

        <div className={cn(panelVariants.status, 'flex flex-col gap-2 p-4')}>
          <p className="text-xs font-bold uppercase tracking-[0.08em] text-slate-700">当前状态</p>
          <p
            className={cn(
              'inline-flex w-fit items-center justify-center rounded-full px-3 py-1 text-xs font-bold uppercase tracking-[0.08em]',
              status === 'error' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
            )}
          >
            {status === 'idle' ? '空闲' : status === 'streaming' ? '流式生成中' : '出错'}
          </p>
          {error ? <p className="m-0 text-sm text-red-700">{error}</p> : null}
        </div>

        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-slate-700">交互日志</p>
          <ul className={fieldVariants.list}>
            {history.length === 0 ? <li>还没有请求记录。</li> : null}
            {history.slice().reverse().map((entry, index) => (
              <li key={`${entry}-${index}`}>{entry}</li>
            ))}
          </ul>
        </div>

        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-slate-700">A2UI 动作回调</p>
          <ul className={fieldVariants.list}>
            {actions.length === 0 ? <li>还没有触发动作按钮。</li> : null}
            {actions.slice().reverse().map((entry, index) => (
              <li key={`${entry}-${index}`}>{entry}</li>
            ))}
          </ul>
        </div>

        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-slate-700">已接收 A2UI 数据帧</p>
          <div className="flex max-h-96 flex-col gap-3 overflow-auto">
            {frames.length === 0 ? <p className="m-0 text-sm text-slate-500">等待后端返回数据帧…</p> : null}
            {frames.slice().reverse().map((entry, index) => (
              <pre key={`${index}-${entry}`} className="m-0 whitespace-pre-wrap break-words rounded-2xl bg-slate-900 p-3 text-xs text-slate-200">
                {entry}
              </pre>
            ))}
          </div>
        </div>
      </aside>

      <main className="min-w-0">
        <SurfaceViewport
          title="由 A2UI 帧驱动的界面"
          description="如果模型返回了卡片、按钮、表单等组件，这里会直接按 A2UI 组件树渲染。"
          onPing={() =>
            handleAction({
              userAction: {
                name: 'frontend_ping',
                surfaceId: 'main',
                sourceComponentId: 'preview-header',
                timestamp: new Date().toISOString(),
                context: {source: 'preview-header'},
              },
            } as Types.A2UIClientEventMessage)
          }
        >
          <A2UIRenderer surfaceId="main" registry={registry} />
        </SurfaceViewport>
      </main>
    </div>
  );
}

export function App() {
  const [lastAction, setLastAction] = useState<Types.A2UIClientEventMessage | null>(null);

  const handleAction = useCallback((message: Types.A2UIClientEventMessage) => {
    setLastAction(message);
    console.info('A2UI action received:', message);
  }, []);

  return (
    <A2UIProvider onAction={handleAction}>
      <Shell onAction={handleAction} />
      {lastAction ? (
        <div className={cn(panelVariants.primary, 'fixed right-6 bottom-6 px-5 py-3 text-sm font-semibold text-slate-800')}>
          最近动作：{lastAction.userAction?.name ?? 'unknown'}
        </div>
      ) : null}
    </A2UIProvider>
  );
}
