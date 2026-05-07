import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export interface ConfigData {
  llm: {
    provider: string
    api_url: string
    api_key: string
    model: string
    temperature: number
    max_tokens: number
    top_p: number
    claude_api_url: string
    claude_api_key: string
    claude_model: string
    claude_max_tokens: number
    claude_temperature: number
  }
  image: {
    provider: string
    pollinations_api_url: string
    pollinations_width: number
    pollinations_height: number
    api_url: string
    api_key: string
    model: string
    size: string
    quality: string
    stability_api_url: string
    stability_api_key: string
    stability_model: string
    replicate_api_url: string
    replicate_api_key: string
    replicate_model: string
    custom_api_url: string
    custom_api_key: string
    custom_model: string
  }
  notion: {
    token: string
    database_id: string
  }
  upload: {
    url: string
    auth_code: string
  }
  article: {
    min_length: number
    cover_image_style: string
  }
}

export interface ArticleSummary {
  id: string
  title: string
  summary: string
  category: string
  tags: string[]
  status: string
  cover_url: string | null
  notion_page_url: string | null
  updated_at: string
  word_count: number
}

export interface ArticleDetail {
  id: string
  title: string
  summary: string
  category: string
  tags: string[]
  content_markdown: string
  status: string
  cover_url: string | null
  notion_page_url: string | null
  notion_page_id: string | null
  updated_at: string
}

export interface TaskStatus {
  status: 'pending' | 'running' | 'completed' | 'failed'
  step: string
  progress: number
  article_id?: string
  image_url?: string
  page_url?: string
  error?: string
}

export interface StatsData {
  total_articles: number
  published: number
  drafts: number
  total_words: number
  config_ok: boolean
  config_errors: string[]
}

export const getConfig = () => api.get<ConfigData>('/config').then(r => r.data)

export const updateConfig = (data: Record<string, unknown>) =>
  api.put('/config', data).then(r => r.data)

export const getStats = () => api.get<StatsData>('/stats').then(r => r.data)

export const listArticles = () =>
  api.get<{ articles: ArticleSummary[]; total: number }>('/articles').then(r => r.data)

export const getArticle = (id: string) =>
  api.get<ArticleDetail>(`/articles/${id}`).then(r => r.data)

export const updateArticle = (id: string, data: Partial<ArticleDetail>) =>
  api.put<ArticleDetail>(`/articles/${id}`, data).then(r => r.data)

export const deleteArticle = (id: string) =>
  api.delete(`/articles/${id}`).then(r => r.data)

export const generateArticle = (topic?: string) =>
  api.post<{ task_id: string; message: string }>('/articles/generate', { topic }).then(r => r.data)

export const publishArticle = (id: string) =>
  api.post<{ task_id: string; message: string }>(`/articles/${id}/publish`).then(r => r.data)

export const regenerateImage = (id: string, imageType: string, prompt?: string) =>
  api.post<{ task_id: string; message: string }>(`/articles/${id}/generate-image`, {
    article_id: id,
    image_type: imageType,
    prompt,
  }).then(r => r.data)

export const getTaskStatus = (taskId: string) =>
  api.get<TaskStatus>(`/tasks/${taskId}`).then(r => r.data)
