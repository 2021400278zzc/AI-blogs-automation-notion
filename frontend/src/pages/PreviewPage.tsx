import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  ArrowLeft,
  Pencil,
  Send,
  ImagePlus,
  Loader2,
  ExternalLink,
  RefreshCw,
  Tag,
} from 'lucide-react'
import PageHeader from '../components/PageHeader'
import ProgressBar from '../components/ProgressBar'
import StatusBadge from '../components/StatusBadge'
import {
  getArticle,
  publishArticle,
  regenerateImage,
  type ArticleDetail,
} from '../api'
import { useTaskPolling } from '../hooks/useTaskPolling'

export default function PreviewPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [article, setArticle] = useState<ArticleDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [publishTaskId, setPublishTaskId] = useState<string | null>(null)
  const [imageTaskId, setImageTaskId] = useState<string | null>(null)
  const { status: publishStatus } = useTaskPolling(publishTaskId)
  const { status: imageStatus } = useTaskPolling(imageTaskId)

  const fetchArticle = () => {
    if (!id) return
    setLoading(true)
    getArticle(id)
      .then(setArticle)
      .finally(() => setLoading(false))
  }

  useEffect(fetchArticle, [id])

  useEffect(() => { if (publishStatus?.status === 'completed') fetchArticle() }, [publishStatus?.status])
  useEffect(() => { if (imageStatus?.status === 'completed') fetchArticle() }, [imageStatus?.status])

  const handlePublish = async () => {
    if (!id || !confirm('确定发布到 Notion？发布后将自动同步到博客。')) return
    try {
      const result = await publishArticle(id)
      setPublishTaskId(result.task_id)
    } catch {}
  }

  const handleRegenerateImage = async () => {
    if (!id) return
    try {
      const result = await regenerateImage(id, 'cover')
      setImageTaskId(result.task_id)
    } catch {}
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand border-t-transparent" />
      </div>
    )
  }

  if (!article) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-sm text-text-3">文章不存在</p>
        <button onClick={() => navigate('/articles')} className="mt-3 text-sm text-brand-light hover:underline">
          返回列表
        </button>
      </div>
    )
  }

  const isPublishing = publishStatus?.status === 'running' || publishStatus?.status === 'pending'
  const isGeneratingImage = imageStatus?.status === 'running' || imageStatus?.status === 'pending'

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/articles')} className="btn-ghost !p-2.5 !rounded-xl">
            <ArrowLeft className="h-4.5 w-4.5" />
          </button>
          <div>
            <h2 className="text-xl font-bold tracking-tight text-text">{article.title}</h2>
            <div className="mt-1.5 flex items-center gap-2.5">
              <StatusBadge status={article.status} />
              <span className="text-xs text-text-4">
                {article.category} · {article.content_markdown?.length || 0} 字
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => navigate(`/article/${id}/edit`)} className="btn-ghost">
            <Pencil className="h-3.5 w-3.5" />
            编辑
          </button>
          {article.status !== 'published' && (
            <button onClick={handlePublish} disabled={isPublishing} className="btn-primary">
              {isPublishing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
              {isPublishing ? '发布中...' : '发布到 Notion'}
            </button>
          )}
          {article.notion_page_url && (
            <a href={article.notion_page_url} target="_blank" rel="noreferrer" className="btn-ghost">
              <ExternalLink className="h-3.5 w-3.5" />
              Notion
            </a>
          )}
        </div>
      </div>

      {isPublishing && publishStatus && (
        <div className="card p-5">
          <ProgressBar current={publishStatus.progress} label={publishStatus.step} />
        </div>
      )}

      {publishStatus?.status === 'failed' && (
        <div className="rounded-xl border border-danger/20 bg-danger/5 p-4 text-sm text-danger">
          发布失败：{publishStatus.error}
        </div>
      )}

      <div className="card card-glow overflow-hidden">
        <div className="flex items-center justify-between border-b border-border px-6 py-3">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-text-4">封面图片</span>
          <button
            onClick={handleRegenerateImage}
            disabled={isGeneratingImage}
            className="flex items-center gap-1.5 text-xs font-medium text-brand-light transition-colors hover:text-brand disabled:opacity-50"
          >
            {isGeneratingImage ? <Loader2 className="h-3 w-3 animate-spin" /> : <RefreshCw className="h-3 w-3" />}
            {isGeneratingImage ? '生成中...' : '重新生成'}
          </button>
        </div>
        {article.cover_url ? (
          <img src={article.cover_url} alt="cover" className="w-full object-cover" style={{ maxHeight: 380 }} />
        ) : isGeneratingImage ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader2 className="mx-auto h-8 w-8 animate-spin text-brand-light" />
              <p className="mt-4 text-xs text-text-4">图片生成中...</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20">
            <ImagePlus className="mb-3 h-10 w-10 text-text-4" />
            <p className="text-xs text-text-4">暂无封面图</p>
            <button onClick={handleRegenerateImage} className="mt-3 text-xs font-medium text-brand-light hover:underline">
              生成封面
            </button>
          </div>
        )}
      </div>

      {isGeneratingImage && imageStatus && (
        <div className="card p-5">
          <ProgressBar current={imageStatus.progress} label={imageStatus.step} />
        </div>
      )}

      {article.tags?.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          <Tag className="h-3.5 w-3.5 text-text-4" />
          {article.tags.map((tag, i) => (
            <span key={i} className="rounded-full bg-gradient-to-r from-brand/8 to-cyan/6 border border-brand/15 px-3 py-1 text-[11px] font-medium text-brand-light">
              {tag}
            </span>
          ))}
        </div>
      )}

      {article.summary && (
        <div className="card card-glow p-6">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-text-4 mb-2">摘要</p>
          <p className="text-sm leading-relaxed text-text-2">{article.summary}</p>
        </div>
      )}

      <div className="card card-glow p-8">
        <div className="markdown-body">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {article.content_markdown || ''}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  )
}
