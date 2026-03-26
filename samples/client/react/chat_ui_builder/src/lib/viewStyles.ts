export const buttonVariants = {
  primary:
    'rounded-full px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:-translate-y-px disabled:cursor-progress disabled:opacity-70 bg-gradient-to-r from-blue-600 to-blue-700',
  secondary:
    'rounded-full px-4 py-3 text-sm font-semibold text-slate-900 shadow-sm transition hover:-translate-y-px bg-slate-200/90',
  ghost: 'rounded-xl border border-slate-200 bg-slate-100/90 px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-200/90',
} as const;

export const panelVariants = {
  primary: 'rounded-3xl border border-slate-300/40 bg-white/90 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur-xl',
  info: 'rounded-2xl border border-sky-200/90 bg-sky-50/80 shadow-sm',
  status: 'rounded-2xl border border-cyan-300/40 bg-gradient-to-b from-blue-50/90 to-slate-50/95',
  secondary: 'rounded-2xl border border-slate-200/80 bg-white/85 shadow-sm',
} as const;

export const fieldVariants = {
  input:
    'w-full rounded-xl border border-slate-300/60 bg-white/90 px-3 py-2.5 text-sm text-slate-800 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
  list: 'flex list-disc flex-col gap-2 pl-5 text-sm text-slate-700',
  label: 'flex flex-col gap-2 text-sm font-semibold text-slate-800',
} as const;

export const surfaceVariants = {
  shell: 'render-surface a2ui-content-theme min-h-[520px]',
  card: 'min-h-[50vh] overflow-auto bg-white/85 p-7 xl:min-h-[calc(100vh-48px)]',
} as const;
