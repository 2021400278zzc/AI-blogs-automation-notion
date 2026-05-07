import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Save,
  Eye,
  Loader2,
} from 'lucide-react'
import { getArticle, updateArticle, type ArticleDetail } from '../api'

export default function EditorPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [article, setArticle] = useState<ArticleDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [title, setTitle] = useState('')
  const [summary, setSummary] = useState('')
  const [category, setCategory] = useState('')
  const [tags, setTags] = useState('')
  const [content, setContent] = useState('')

  useEffect(() => {
    if (!id) return
    setLoading(true)
    getArticle(id)
      .then(a => {
        setArticle(a)
        setTitle(a.title)
        setSummary(a.summary)
        setCategory(a.category)
        setTags(a.tags?.join(', ') || '')
        setContent(a.content_markdown)
      })
      .finally(() => setLoading(false))
  }, [id])

  const handleSave = async () => {
    if (!id) return
    setSaving(true)
    try {
      const updated = await updateArticle(id, {
        title,
        summary,
        category,
        tags: tags.split(',').map(t => t.trim()).filter(Boolean),
        content_markdown: content,
      })
      setArticle(updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch {}
    setSaving(false)
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

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(`/article/${id}`)} className="btn-ghost !p-2.5 !rounded-xl">
            <ArrowLeft className="h-4.5 w-4.5" />
          </button>
          <h2 className="text-xl font-bold tracking-tight text-text">编辑文章</h2>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => navigate(`/article/${id}`)} className="btn-ghost">
            <Eye className="h-3.5 w-3.5" />
            预览
          </button>
          <button onClick={handleSave} disabled={saving} className="btn-primary">
            {saving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
            {saving ? '保存中...' : saved ? '已保存' : '保存'}
          </button>
        </div>
      </div>

      <div className="card p-6 space-y-5">
        <div>
          <label className="mb-2 block text-[13px] font-medium text-text-2">标题</label>
          <input type="text" value={title} onChange={e => setTitle(e.target.value)} className="input-field text-base font-semibold" />
        </div>

        <div>
          <label className="mb-2 block text-[13px] font-medium text-text-2">摘要</label>
          <textarea
            value={summary}
            onChange={e => setSummary(e.target.value)}
            rows={2}
            className="input-field resize-none"
          />
        </div>

        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-[13px] font-medium text-text-2">分类</label>
            <input type="text" value={category} onChange={e => setCategory(e.target.value)} className="input-field" />
          </div>
          <div>
            <label className="mb-2 block text-[13px] font-medium text-text-2">标签</label>
            <input
              type="text"
              value={tags}
              onChange={e => setTags(e.target.value)}
              placeholder="逗号分隔，如：AI, 技术, 编程"
              className="input-field"
            />
          </div>
        </div>
      </div>

      <div className="card p-6">
        <div className="mb-3 flex items-center justify-between">
          <label className="text-[13px] font-medium text-text-2">文章内容</label>
          <span className="text-xs font-mono text-text-4 tabular-nums">{content.length} 字</span>
        </div>
        <textarea
          value={content}
          onChange={e => setContent(e.target.value)}
          rows={28}
          className="input-field resize-y font-mono text-[13px] leading-relaxed"
          style={{ minHeight: 480 }}
        />
      </div>
    </div>
  )
}
