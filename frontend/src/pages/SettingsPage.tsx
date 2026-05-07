import { useEffect, useState } from 'react'
import { Save, Loader2, CheckCircle2, AlertTriangle, Cpu, Image, Database, FileText } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import { getConfig, updateConfig, type ConfigData } from '../api'

type TabKey = 'llm' | 'image' | 'notion' | 'article'

const tabs: { key: TabKey; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: 'llm', label: 'AI 模型', icon: Cpu },
  { key: 'image', label: '图片生成', icon: Image },
  { key: 'notion', label: 'Notion', icon: Database },
  { key: 'article', label: '文章设置', icon: FileText },
]

export default function SettingsPage() {
  const [config, setConfig] = useState<ConfigData | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<TabKey>('llm')
  const [form, setForm] = useState<Record<string, string>>({})

  useEffect(() => {
    getConfig()
      .then(c => {
        setConfig(c)
        const flat: Record<string, string> = {}
        flat.llm_provider = c.llm.provider
        flat.llm_api_url = c.llm.api_url
        flat.llm_api_key = c.llm.api_key
        flat.llm_model = c.llm.model
        flat.llm_temperature = String(c.llm.temperature)
        flat.llm_max_tokens = String(c.llm.max_tokens)
        flat.llm_top_p = String(c.llm.top_p)
        flat.claude_api_url = c.llm.claude_api_url
        flat.claude_api_key = c.llm.claude_api_key
        flat.claude_model = c.llm.claude_model
        flat.claude_max_tokens = String(c.llm.claude_max_tokens)
        flat.claude_temperature = String(c.llm.claude_temperature)
        flat.image_provider = c.image.provider
        flat.image_api_url = c.image.api_url
        flat.image_api_key = c.image.api_key
        flat.image_model = c.image.model
        flat.image_size = c.image.size
        flat.image_quality = c.image.quality
        flat.notion_token = c.notion.token
        flat.notion_database_id = c.notion.database_id
        flat.cover_image_style = c.article.cover_image_style
        flat.article_min_length = String(c.article.min_length)
        setForm(flat)
      })
      .finally(() => setLoading(false))
  }, [])

  const handleChange = (key: string, value: string) => {
    setForm(prev => ({ ...prev, [key]: value }))
    setSaved(false)
  }

  const handleSave = async () => {
    setSaving(true)
    setError('')
    try {
      await updateConfig(form)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '保存失败')
    }
    setSaving(false)
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl space-y-7">
      <PageHeader
        title="系统配置"
        subtitle="配置 AI 模型、图片生成、Notion 等参数"
        action={
          <button onClick={handleSave} disabled={saving} className="btn-primary">
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : saved ? <CheckCircle2 className="h-4 w-4" /> : <Save className="h-4 w-4" />}
            {saving ? '保存中...' : saved ? '已保存' : '保存配置'}
          </button>
        }
      />

      {error && (
        <div className="flex items-center gap-2.5 rounded-xl border border-danger/20 bg-danger/5 p-4 text-sm text-danger">
          <AlertTriangle className="h-4 w-4" />
          {error}
        </div>
      )}

      <div className="flex gap-1.5 rounded-xl border border-border bg-surface-2 p-1.5">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2.5 text-[12px] font-semibold transition-all duration-200 ${
              activeTab === tab.key
                ? 'bg-brand/12 text-brand-light shadow-sm shadow-brand-glow'
                : 'text-text-4 hover:text-text-2'
            }`}
          >
            <tab.icon className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">{tab.label}</span>
          </button>
        ))}
      </div>

      {activeTab === 'llm' && (
        <div className="card p-6 space-y-5">
          <FormField
            label="LLM 提供商"
            value={form.llm_provider || ''}
            onChange={v => handleChange('llm_provider', v)}
            select
            options={[
              { value: 'openai', label: 'OpenAI 兼容格式' },
              { value: 'claude', label: 'Anthropic Claude' },
            ]}
          />
          <p className="text-xs text-text-4 rounded-lg bg-surface-3 p-3 border border-border">
            OpenAI 格式适用于：OpenAI、DeepSeek、Groq、Grok2API、Ollama 等
          </p>

          {form.llm_provider === 'openai' ? (
            <>
              <FormField label="API 地址" value={form.llm_api_url || ''} onChange={v => handleChange('llm_api_url', v)} />
              <FormField label="API Key" value={form.llm_api_key || ''} onChange={v => handleChange('llm_api_key', v)} type="password" />
              <FormField label="模型" value={form.llm_model || ''} onChange={v => handleChange('llm_model', v)} />
              <div className="grid gap-4 sm:grid-cols-3">
                <FormField label="Temperature" value={form.llm_temperature || ''} onChange={v => handleChange('llm_temperature', v)} type="number" />
                <FormField label="Max Tokens" value={form.llm_max_tokens || ''} onChange={v => handleChange('llm_max_tokens', v)} type="number" />
                <FormField label="Top P" value={form.llm_top_p || ''} onChange={v => handleChange('llm_top_p', v)} type="number" />
              </div>
            </>
          ) : (
            <>
              <FormField label="Claude API 地址" value={form.claude_api_url || ''} onChange={v => handleChange('claude_api_url', v)} />
              <FormField label="Claude API Key" value={form.claude_api_key || ''} onChange={v => handleChange('claude_api_key', v)} type="password" />
              <FormField label="Claude 模型" value={form.claude_model || ''} onChange={v => handleChange('claude_model', v)} />
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField label="Max Tokens" value={form.claude_max_tokens || ''} onChange={v => handleChange('claude_max_tokens', v)} type="number" />
                <FormField label="Temperature" value={form.claude_temperature || ''} onChange={v => handleChange('claude_temperature', v)} type="number" />
              </div>
            </>
          )}
        </div>
      )}

      {activeTab === 'image' && (
        <div className="card p-6 space-y-5">
          <FormField
            label="图片生成提供商"
            value={form.image_provider || ''}
            onChange={v => handleChange('image_provider', v)}
            select
            options={[
              { value: 'pollinations', label: 'Pollinations.ai (免费)' },
              { value: 'openai', label: 'OpenAI DALL-E' },
              { value: 'stability', label: 'Stability AI' },
              { value: 'replicate', label: 'Replicate' },
              { value: 'custom', label: '自定义 API' },
            ]}
          />

          {form.image_provider === 'openai' && (
            <>
              <FormField label="API 地址" value={form.image_api_url || ''} onChange={v => handleChange('image_api_url', v)} />
              <FormField label="API Key" value={form.image_api_key || ''} onChange={v => handleChange('image_api_key', v)} type="password" />
              <FormField label="模型" value={form.image_model || ''} onChange={v => handleChange('image_model', v)} />
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField
                  label="尺寸"
                  value={form.image_size || ''}
                  onChange={v => handleChange('image_size', v)}
                  select
                  options={[
                    { value: '1024x1024', label: '1024x1024' },
                    { value: '1024x1792', label: '1024x1792' },
                    { value: '1792x1024', label: '1792x1024' },
                  ]}
                />
                <FormField
                  label="质量"
                  value={form.image_quality || ''}
                  onChange={v => handleChange('image_quality', v)}
                  select
                  options={[
                    { value: 'standard', label: 'Standard' },
                    { value: 'hd', label: 'HD' },
                  ]}
                />
              </div>
            </>
          )}

          {form.image_provider === 'pollinations' && (
            <div className="rounded-xl border border-info/15 bg-info/5 p-4">
              <p className="text-xs text-info">
                Pollinations.ai 是免费服务，无需 API Key，开箱即用。
              </p>
            </div>
          )}

          {(form.image_provider === 'stability' || form.image_provider === 'replicate' || form.image_provider === 'custom') && (
            <div className="rounded-xl border border-border bg-surface-3 p-4">
              <p className="text-xs text-text-4">请通过 .env 文件配置 {form.image_provider === 'stability' ? 'Stability AI' : form.image_provider === 'replicate' ? 'Replicate' : '自定义图片生成 API'} 参数</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'notion' && (
        <div className="card p-6 space-y-5">
          <FormField label="Notion Token" value={form.notion_token || ''} onChange={v => handleChange('notion_token', v)} type="password" />
          <FormField label="Database ID" value={form.notion_database_id || ''} onChange={v => handleChange('notion_database_id', v)} />
          <div className="rounded-xl border border-info/15 bg-info/5 p-4 space-y-1.5">
            <p className="text-xs text-info">
              获取 Token：前往 notion.so/my-integrations 创建 Integration
            </p>
            <p className="text-xs text-info">
              获取 Database ID：打开 Notion 数据库页面，URL 中最后一串字符即为 ID
            </p>
          </div>
        </div>
      )}

      {activeTab === 'article' && (
        <div className="card p-6 space-y-5">
          <FormField label="文章最小字数" value={form.article_min_length || ''} onChange={v => handleChange('article_min_length', v)} type="number" />
          <div>
            <label className="mb-2 block text-[13px] font-medium text-text-2">封面图片风格描述</label>
            <textarea
              value={form.cover_image_style || ''}
              onChange={e => handleChange('cover_image_style', e.target.value)}
              rows={3}
              className="input-field resize-none"
            />
            <p className="mt-2 text-xs text-text-4">用于 AI 生成封面图片时的风格提示词</p>
          </div>
        </div>
      )}

      <div className="rounded-xl border border-border bg-surface-2 p-5">
        <p className="text-xs leading-relaxed text-text-4">
          前端修改的配置会保存到 .env 文件，并立即生效（服务单例会自动重新初始化）。
          开发者也可以直接编辑 .env 文件，后端默认读取 .env 配置。
        </p>
      </div>
    </div>
  )
}

function FormField({
  label,
  value,
  onChange,
  type = 'text',
  select = false,
  options,
}: {
  label: string
  value: string
  onChange: (v: string) => void
  type?: string
  select?: boolean
  options?: { value: string; label: string }[]
}) {
  return (
    <div>
      <label className="mb-2 block text-[13px] font-medium text-text-2">{label}</label>
      {select ? (
        <select
          value={value}
          onChange={e => onChange(e.target.value)}
          className="input-field appearance-none"
        >
          {options?.map(o => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          type={type}
          value={value}
          onChange={e => onChange(e.target.value)}
          className="input-field"
        />
      )}
    </div>
  )
}
