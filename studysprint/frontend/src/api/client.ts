export const TOKEN_KEY = 'studysprint_token'

export interface User {
  id: number
  username: string
  email: string
}

export interface Topic {
  id: number
  name: string
  summary: string
  source_page: number
  mastery: number
  attempts: number
  last_practiced_at: string | null
  question_count: number
}

export interface DocumentInfo {
  id: number
  filename: string
  page_count: number
  created_at: string
}

export interface Course {
  id: number
  title: string
  exam_date: string | null
  created_at: string
  document_count: number
  topic_count: number
  average_mastery: number
}

export interface CourseDetail extends Course {
  documents: DocumentInfo[]
  topics: Topic[]
}

export interface Question {
  id: number
  topic_id: number
  prompt: string
  source_page: number
  model: string
}

export interface QuestionWithAnswer extends Question {
  reference_answer: string
  key_points: string[]
}

export interface SessionQuestion extends Question {
  topic_name: string
  topic_mastery: number
}

export interface AttemptResult {
  id: number
  question_id: number
  score: number
  feedback: string
  missing_points: string[]
  model: string
  reference_answer: string
  source_page: number
  topic_mastery: number
}

export interface PlanDay {
  date: string
  focus: 'learn' | 'practice' | 'review'
  topics: { id: number; name: string; mastery: number }[]
}

export interface AskResult {
  answer: string
  citations: { page: number; document: string; excerpt: string }[]
  model: string
  cached: boolean
}

export interface ModelInfo {
  id: string
  label: string
  kind: 'llm' | 'local'
  available: boolean
}

export interface CompareRow {
  model: string
  ok: boolean
  latency_ms: number
  output: Record<string, unknown> | null
  error: string | null
}

export interface AgentRun {
  run_id: string
  intent: string
  steps: { worker: string; tool: string; summary: string }[]
  output: Record<string, unknown>
}

export interface TraceEvent {
  id: string
  run_id: string | null
  kind: string
  name: string
  status: string
  duration_ms: number
  started_at: string
  detail: Record<string, unknown>
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

function errorMessage(body: unknown, fallback: string): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && detail[0]?.msg) return String(detail[0].msg)
  }
  return fallback
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (init.body && !(init.body instanceof FormData)) headers.set('Content-Type', 'application/json')

  let response: Response
  try {
    response = await fetch(`/api${path}`, { ...init, headers })
  } catch {
    throw new ApiError(0, 'Cannot reach the StudySprint API. Is the backend running?')
  }
  if (response.status === 204) return undefined as T
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(response.status, errorMessage(body, `Request failed (${response.status})`))
  }
  return body as T
}

const json = (data: unknown) => JSON.stringify(data)

export const api = {
  login: (username: string, password: string) =>
    request<{ access_token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: json({ username, password }),
    }),
  register: (username: string, email: string, password: string) =>
    request<{ access_token: string; user: User }>('/auth/register', {
      method: 'POST',
      body: json({ username, email, password }),
    }),
  me: () => request<User>('/auth/me'),

  listCourses: () => request<Course[]>('/courses'),
  createCourse: (title: string, exam_date: string | null) =>
    request<CourseDetail>('/courses', { method: 'POST', body: json({ title, exam_date }) }),
  getCourse: (id: number) => request<CourseDetail>(`/courses/${id}`),
  updateCourse: (id: number, data: { title?: string; exam_date?: string | null }) =>
    request<CourseDetail>(`/courses/${id}`, { method: 'PATCH', body: json(data) }),
  deleteCourse: (id: number) => request<void>(`/courses/${id}`, { method: 'DELETE' }),
  uploadDocument: (id: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return request<{ document: DocumentInfo; topics_created: number; model: string }>(
      `/courses/${id}/documents`,
      { method: 'POST', body: form },
    )
  },

  generateQuestions: (topicId: number, count = 3) =>
    request<QuestionWithAnswer[]>(`/topics/${topicId}/questions`, {
      method: 'POST',
      body: json({ count }),
    }),
  listQuestions: (topicId: number) => request<QuestionWithAnswer[]>(`/topics/${topicId}/questions`),
  getSession: (courseId: number, size = 5) =>
    request<{ course_id: number; questions: SessionQuestion[] }>(
      `/courses/${courseId}/session?size=${size}`,
    ),
  submitAttempt: (questionId: number, answer: string) =>
    request<AttemptResult>(`/questions/${questionId}/attempts`, {
      method: 'POST',
      body: json({ answer }),
    }),
  getPlan: (courseId: number) =>
    request<{ course_id: number; exam_date: string | null; days: PlanDay[] }>(
      `/courses/${courseId}/plan`,
    ),

  ask: (courseId: number, question: string) =>
    request<AskResult>(`/courses/${courseId}/ask`, { method: 'POST', body: json({ question }) }),
  listModels: () => request<ModelInfo[]>('/ai/models'),
  compare: (data: {
    task: 'ask' | 'grade'
    course_id: number
    question?: string
    question_id?: number
    answer?: string
    models?: string[]
  }) =>
    request<{ task: string; rows: CompareRow[] }>('/ai/compare', {
      method: 'POST',
      body: json(data),
    }),
  runAgent: (course_id: number, goal: string) =>
    request<AgentRun>('/agent/run', { method: 'POST', body: json({ course_id, goal }) }),
  listTraces: (runId?: string) =>
    request<TraceEvent[]>(`/traces?limit=200${runId ? `&run_id=${runId}` : ''}`),
  clearTraces: () => request<void>('/traces', { method: 'DELETE' }),
}
