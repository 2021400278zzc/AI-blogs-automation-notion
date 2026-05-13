import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Sparkles,
  FileText,
  Send,
  AlertTriangle,
  ArrowRight,
  Inbox,
  TrendingUp,
  PenTool,
  Zap,
} from 'lucide-react'
import PageHeader from '../components/PageHeader'
import { getStats, listArticles, type StatsData, type ArticleSummary } from '../api'
import StatusBadge from '../components/StatusBadge'

export default function HomePage() {
  const navigate = useNavigate()
  const [stats, setStats] = useState<StatsData | null>(null)
  const [recent, setRecent] = useState<ArticleSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getStats(), listArticles()])
      .then(([s, a]) => {
        setStats(s)
        setRecent(a.articles.slice(0, 5))
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <PageHeader
        title="工作台"
        subtitle="AI 驱动的自动化博客内容生产系统"
        action={
          <button onClick={() => navigate('/generate')} className="btn-primary">
            <Sparkles className="h-4 w-4" />
            生成文章
          </button>
        }
      />

      {stats && !stats.config_ok && (
        <div className="flex items-start gap-3.5 rounded-xl border border-warning/20 bg-warning/5 p-4">
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-warning/10">
            <AlertTriangle className="h-4 w-4 text-warning" />
          </div>
          <div>
            <p className="text-[13px] font-semibold text-warning">配置不完整</p>
            <p className="mt-1 text-xs text-text-3">
              {stats.config_errors.join('、')}，请前往{' '}
              <button onClick={() => navigate('/settings')} className="text-brand-light hover:underline">
                系统配置
              </button>{' '}
              完成设置
            </p>
          </div>
        </div>
      )}

      {stats && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard
            icon={<FileText className="h-5 w-5" />}
            label="文章总数"
            value={stats.total_articles}
            iconColor="text-brand-light"
            iconBg="bg-gradient-to-br from-brand/15 to-cyan/8"
            gradient="from-brand/8 via-transparent to-cyan/5"
          />
          <StatCard
            icon={<Send className="h-5 w-5" />}
            label="已发布"
            value={stats.published}
            iconColor="text-success"
            iconBg="bg-gradient-to-br from-success/15 to-success/5"
            gradient="from-success/8 via-transparent to-success/3"
          />
          <StatCard
            icon={<PenTool className="h-5 w-5" />}
            label="草稿"
            value={stats.drafts}
            iconColor="text-warning"
            iconBg="bg-gradient-to-br from-warning/15 to-warning/5"
            gradient="from-warning/8 via-transparent to-warning/3"
          />
          <StatCard
            icon={<TrendingUp className="h-5 w-5" />}
            label="总字数"
            value={stats.total_words > 1000 ? `${(stats.total_words / 1000).toFixed(1)}k` : stats.total_words}
            iconColor="text-info"
            iconBg="bg-gradient-to-br from-info/15 to-cyan/8"
            gradient="from-info/8 via-transparent to-cyan/5"
          />
        </div>
      )}

      <div className="grid gap-5 sm:grid-cols-2">
        <QuickAction
          icon={<Zap className="h-6 w-6" />}
          title="自动生成文章"
          desc="AI 自动选题、搜索、写作，一键生成完整博文并配图"
          onClick={() => navigate('/generate')}
          gradient="from-brand via-brand-dark to-cyan"
        />
        <QuickAction
          icon={<PenTool className="h-6 w-6" />}
          title="指定主题生成"
          desc="输入你想要的主题，AI 围绕主题撰写深度文章"
          onClick={() => navigate('/generate?mode=topic')}
          gradient="from-cyan via-info-2 to-brand"
        />
      </div>

      {recent.length > 0 && (
        <div className="card card-glow overflow-hidden">
          <div className="flex items-center justify-between border-b border-border px-6 py-4">
            <h3 className="text-[13px] font-semibold text-text-2">最近文章</h3>
            <button
              onClick={() => navigate('/articles')}
              className="flex items-center gap-1.5 text-xs text-brand-light transition-colors hover:text-brand"
            >
              查看全部 <ArrowRight className="h-3 w-3" />
            </button>
          </div>
          <div className="divide-y divide-border/60">
            {recent.map(a => (
              <div
                key={a.id}
                onClick={() => navigate(`/article/${a.id}`)}
                className="flex cursor-pointer items-center gap-4 px-6 py-3.5 transition-colors hover:bg-surface-3/60"
              >
                {a.cover_url ? (
                  <img src={a.cover_url} alt="" className="h-11 w-[72px] flex-shrink-0 rounded-lg object-cover shadow-sm" />
                ) : (
                  <div className="flex h-11 w-[72px] flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-surface-4 to-surface-3">
                    <FileText className="h-4 w-4 text-text-4" />
                  </div>
                )}
                <div className="min-w-0 flex-1">
                  <p className="truncate text-[13px] font-medium text-text">{a.title}</p>
                  <p className="mt-0.5 truncate text-xs text-text-4">
                    {a.category} · {a.word_count} 字
                  </p>
                </div>
                <StatusBadge status={a.status} />
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && recent.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-20">
          <Inbox className="mb-4 h-12 w-12 text-text-4" />
          <p className="text-sm text-text-3">还没有文章</p>
          <p className="mt-1 text-xs text-text-4">点击上方按钮开始生成</p>
        </div>
      )}
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
  iconColor,
  iconBg,
  gradient,
}: {
  icon: React.ReactNode
  label: string
  value: number | string
  iconColor: string
  iconBg: string
  gradient: string
}) {
  return (
    <div className="card card-hover card-glow p-5 relative overflow-hidden">
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 transition-opacity duration-300 group-hover:opacity-100`} />
      <div className="relative z-10">
        <div className={`mb-3 flex h-10 w-10 items-center justify-center rounded-xl ${iconBg} ${iconColor}`}>
          {icon}
        </div>
        <p className="text-3xl font-bold tracking-tight text-text">{value}</p>
        <p className="mt-1 text-xs text-text-4">{label}</p>
      </div>
    </div>
  )
}

function QuickAction({
  icon,
  title,
  desc,
  onClick,
  gradient,
}: {
  icon: React.ReactNode
  title: string
  desc: string
  onClick: () => void
  gradient: string
}) {
  return (
    <button
      onClick={onClick}
      className="group card card-hover card-glow flex items-start gap-5 p-6 text-left relative overflow-hidden"
    >
      <div className="absolute -inset-1 bg-gradient-to-br from-brand/5 via-transparent to-cyan/5 opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
      <div className="relative z-10 flex items-start gap-5 w-full">
        <div className={`flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${gradient} text-white shadow-lg shadow-brand-glow transition-transform duration-300 group-hover:scale-110`}>
          {icon}
        </div>
        <div>
          <p className="text-[15px] font-semibold text-text">{title}</p>
          <p className="mt-1.5 text-xs leading-relaxed text-text-3">{desc}</p>
        </div>
      </div>
    </button>
  )
}
