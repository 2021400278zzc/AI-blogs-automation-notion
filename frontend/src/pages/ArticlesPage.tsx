import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, Trash2, ExternalLink, Pencil, Inbox } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'
import { listArticles, deleteArticle, type ArticleSummary } from '../api'

export default function ArticlesPage() {
  const navigate = useNavigate()
  const [articles, setArticles] = useState<ArticleSummary[]>([])
  const [loading, setLoading] = useState(true)

  const fetchArticles = () => {
    setLoading(true)
    listArticles()
      .then(data => setArticles(data.articles))
      .finally(() => setLoading(false))
  }

  useEffect(fetchArticles, [])

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('确定删除此文章？')) return
    try {
      await deleteArticle(id)
      fetchArticles()
    } catch {}
  }

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
        title="文章管理"
        subtitle={`共 ${articles.length} 篇文章`}
        action={
          <button onClick={() => navigate('/generate')} className="btn-primary">
            <FileText className="h-4 w-4" />
            新建文章
          </button>
        }
      />

      {articles.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-20">
          <Inbox className="mb-4 h-12 w-12 text-text-4" />
          <p className="text-sm text-text-3">暂无文章</p>
          <p className="mt-1 text-xs text-text-4">点击上方按钮开始生成</p>
        </div>
      ) : (
        <>
          <div className="card card-glow overflow-hidden hidden sm:block">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border text-left text-[11px] font-semibold uppercase tracking-wider text-text-4">
                  <th className="px-6 py-4">标题</th>
                  <th className="px-6 py-4">分类</th>
                  <th className="px-6 py-4">字数</th>
                  <th className="px-6 py-4">状态</th>
                  <th className="px-6 py-4">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {articles.map(a => (
                  <tr
                    key={a.id}
                    onClick={() => navigate(`/article/${a.id}`)}
                    className="cursor-pointer transition-colors hover:bg-surface-3/50"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3.5">
                        {a.cover_url ? (
                          <img src={a.cover_url} alt="" className="h-10 w-16 rounded-lg object-cover shadow-sm" />
                        ) : (
                          <div className="flex h-10 w-16 items-center justify-center rounded-lg bg-gradient-to-br from-surface-4 to-surface-3">
                            <FileText className="h-4 w-4 text-text-4" />
                          </div>
                        )}
                        <span className="max-w-[240px] truncate text-[13px] font-medium text-text">
                          {a.title}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-text-3">{a.category || '-'}</td>
                    <td className="px-6 py-4 text-xs font-mono text-text-4 tabular-nums">{a.word_count}</td>
                    <td className="px-6 py-4">
                      <StatusBadge status={a.status} />
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-0.5">
                        <button
                          onClick={e => { e.stopPropagation(); navigate(`/article/${a.id}/edit`) }}
                          className="rounded-lg p-2 text-text-4 transition-colors hover:bg-surface-4 hover:text-text-2"
                          title="编辑"
                        >
                          <Pencil className="h-3.5 w-3.5" />
                        </button>
                        {a.notion_page_url && (
                          <a
                            href={a.notion_page_url}
                            target="_blank"
                            rel="noreferrer"
                            onClick={e => e.stopPropagation()}
                            className="rounded-lg p-2 text-text-4 transition-colors hover:bg-surface-4 hover:text-info"
                            title="Notion"
                          >
                            <ExternalLink className="h-3.5 w-3.5" />
                          </a>
                        )}
                        <button
                          onClick={e => handleDelete(a.id, e)}
                          className="rounded-lg p-2 text-text-4 transition-colors hover:bg-surface-4 hover:text-danger"
                          title="删除"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="space-y-3 sm:hidden">
            {articles.map(a => (
              <div
                key={a.id}
                onClick={() => navigate(`/article/${a.id}`)}
                className="card card-hover card-glow flex items-center gap-3.5 p-4 cursor-pointer"
              >
                {a.cover_url ? (
                  <img src={a.cover_url} alt="" className="h-11 w-[72px] rounded-lg object-cover shadow-sm" />
                ) : (
                  <div className="flex h-11 w-[72px] items-center justify-center rounded-lg bg-gradient-to-br from-surface-4 to-surface-3">
                    <FileText className="h-4 w-4 text-text-4" />
                  </div>
                )}
                <div className="min-w-0 flex-1">
                  <p className="truncate text-[13px] font-medium text-text">{a.title}</p>
                  <div className="mt-1.5 flex items-center gap-2">
                    <StatusBadge status={a.status} />
                    <span className="text-xs font-mono text-text-4 tabular-nums">{a.word_count}字</span>
                  </div>
                </div>
                <button onClick={e => handleDelete(a.id, e)} className="rounded-lg p-2 text-text-4">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
