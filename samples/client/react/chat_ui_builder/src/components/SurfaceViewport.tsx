import {PropsWithChildren} from 'react';
import {cn} from '../lib/cn';
import {panelVariants, surfaceVariants} from '../lib/viewStyles';

interface SurfaceViewportProps extends PropsWithChildren {
  title: string;
  description: string;
  onPing: () => void;
}

export function SurfaceViewport({title, description, onPing, children}: SurfaceViewportProps) {
  return (
    <section className={cn(panelVariants.primary, surfaceVariants.card)}>
      <header className={cn(panelVariants.secondary, 'mb-6 flex flex-col justify-between gap-4 p-4 xl:flex-row xl:items-start')}>
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-blue-600">实时预览</p>
          <h2 className="text-2xl font-semibold text-slate-900">{title}</h2>
          <p className="mt-2 text-sm text-slate-500">{description}</p>
        </div>
        <button
          type="button"
          className="rounded-full bg-slate-200/90 px-4 py-3 text-sm font-semibold text-slate-900 shadow-sm transition hover:-translate-y-px"
          onClick={onPing}
        >
          测试动作回调
        </button>
      </header>
      <div className={surfaceVariants.shell}>{children}</div>
    </section>
  );
}
