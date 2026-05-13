interface Props {
  current: number
  label: string
}

export default function ProgressBar({ current, label }: Props) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-[13px] font-medium text-text-2">{label}</span>
        <span className="text-xs font-mono text-text-4 tabular-nums">{current}%</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-surface-4">
        <div
          className="h-full rounded-full bg-gradient-to-r from-brand via-brand-light to-cyan transition-all duration-700 ease-out relative"
          style={{ width: `${current}%` }}
        >
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
        </div>
      </div>
    </div>
  )
}
