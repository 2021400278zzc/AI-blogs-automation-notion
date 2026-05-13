interface Props {
  status: string
}

const statusMap: Record<string, { label: string; cls: string; dot: string }> = {
  draft: { label: '草稿', cls: 'bg-warning/10 text-warning border-warning/20', dot: 'bg-warning' },
  published: { label: '已发布', cls: 'bg-success/10 text-success border-success/20', dot: 'bg-success' },
  generating: { label: '生成中', cls: 'bg-gradient-to-r from-brand/10 to-cyan/8 text-info border-brand/20', dot: 'bg-gradient-to-r from-brand to-cyan animate-pulse' },
  failed: { label: '失败', cls: 'bg-danger/10 text-danger border-danger/20', dot: 'bg-danger' },
  ready: { label: '就绪', cls: 'bg-success/10 text-success border-success/20', dot: 'bg-success' },
}

export default function StatusBadge({ status }: Props) {
  const s = statusMap[status] || statusMap.draft
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold ${s.cls}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  )
}
