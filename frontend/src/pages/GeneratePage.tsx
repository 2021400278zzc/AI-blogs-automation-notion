import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Sparkles, Loader2, Zap, PenTool, Info } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import ProgressBar from '../components/ProgressBar'
import { generateArticle } from '../api'
import { useTaskPolling } from '../hooks/useTaskPolling'

export default function GeneratePage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [topic, setTopic] = useState('')
  const [taskId, setTaskId] = useState<string | null>(null)
  const { status } = useTaskPolling(taskId)

  useEffect(() => {
    const mode = searchParams.get('mode')
    if (mode === 'topic') {
      const input = document.getElementById('topic-input')
      input?.focus()
    }
  }, [searchParams])

  useEffect(() => {
    if (status?.status === 'completed' && status.article_id) {
      const timer = setTimeout(() => {
        navigate(`/article/${status.article_id}`)
      }, 800)
      return () => clearTimeout(timer)
    }
  }, [status, navigate])

  const handleGenerate = async (withTopic: boolean) => {
    try {
      const result = await generateArticle(withTopic ? topic : undefined)
      setTaskId(result.task_id)
    } catch (err) {
      console.error('Generate failed:', err)
    }
  }

  const isRunning = status?.status === 'running' || status?.status === 'pending'

  return (
    <div className="mx-auto max-w-2xl space-y-7">
      <PageHeader title="生成文章" subtitle="AI 自动选题或指定主题生成博文" />

      <div className="card p-7">
        {!isRunning ? (
          <div className="space-y-6">
            <div>
              <label className="mb-2 block text-[13px] font-medium text-text-2">
                指定主题（可选）
              </label>
              <input
                id="topic-input"
                type="text"
                value={topic}
                onChange={e => setTopic(e.target.value)}
                placeholder="留空则由 AI 自动选题"
                className="input-field"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => handleGenerate(false)}
                className="btn-primary flex-1 justify-center py-3"
              >
                <Zap className="h-4 w-4" />
                AI 自动选题
              </button>
              <button
                onClick={() => handleGenerate(true)}
                disabled={!topic.trim()}
                className="btn-ghost flex-1 justify-center py-3 disabled:opacity-40"
              >
                <PenTool className="h-4 w-4" />
                按主题生成
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-5 py-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand/10">
                <Loader2 className="h-5 w-5 animate-spin text-brand-light" />
              </div>
              <div>
                <p className="text-[13px] font-semibold text-text-2">
                  {status?.step || '准备中...'}
                </p>
                <p className="text-xs text-text-4">生成过程通常需要 1-3 分钟</p>
              </div>
            </div>
            <ProgressBar
              current={status?.progress || 0}
              label={status?.step || '初始化'}
            />
          </div>
        )}

        {status?.status === 'failed' && (
          <div className="mt-5 rounded-xl border border-danger/20 bg-danger/5 p-5">
            <p className="text-[13px] font-semibold text-danger">生成失败</p>
            <p className="mt-1.5 text-xs text-text-3">{status.error}</p>
            <button
              onClick={() => setTaskId(null)}
              className="mt-3 text-xs font-medium text-brand-light hover:underline"
            >
              重新尝试
            </button>
          </div>
        )}
      </div>

      <div className="card p-6">
        <div className="mb-4 flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-surface-4">
            <Info className="h-3.5 w-3.5 text-text-3" />
          </div>
          <h3 className="text-[13px] font-semibold text-text-2">生成流程说明</h3>
        </div>
        <div className="space-y-3">
          {[
            'AI 自动选题（或使用你指定的主题）',
            '搜索最新相关资料与行业动态',
            'AI 生成完整文章（Markdown 格式，2000+ 字）',
            'AI 生成封面图片并上传图床',
            '生成完成后可预览、编辑、再发布到 Notion',
          ].map((step, i) => (
            <div key={i} className="flex items-center gap-3.5">
              <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-lg bg-brand/8 text-[11px] font-bold text-brand-light">
                {i + 1}
              </span>
              <span className="text-xs text-text-3">{step}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
