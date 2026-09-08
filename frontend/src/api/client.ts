const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
const TOKEN_KEY = 'noteslab_token'

export type User = {
  id: number
  username: string
  email: string
  role: string
  created_at: string
}

export type Note = {
  id: number
  title: string
  content: string
  owner_id: number
  created_at: string
  updated_at: string
}

export type NoteInput = {
  title: string
  content: string
}

export type AuthResponse = {
  access_token: string
  token_type: string
  user: User
}

export type SearchResult = {
  title: string
  link: string
  snippet: string
}

export type ResearchResponse = {
  session_id: string
  query: string
  plan: string[]
  answer: string
  sources: SearchResult[]
  remembered_facts: string[]
  memory_used: string[]
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setStoredToken(token: string | null) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

async function request<T>(path: string, init?: RequestInit, auth = true): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init?.headers as Record<string, string> | undefined),
  }

  if (auth) {
    const token = getStoredToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  })

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = (await response.json()) as { detail?: string | Array<{ msg?: string }> }
      if (typeof body.detail === 'string') {
        detail = body.detail
      } else if (Array.isArray(body.detail) && body.detail[0]?.msg) {
        detail = body.detail[0].msg
      }
    } catch {
      // keep default message
    }
    throw new Error(detail)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export function register(username: string, email: string, password: string) {
  return request<AuthResponse>(
    '/api/auth/register',
    {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    },
    false,
  )
}

export function login(username: string, password: string) {
  return request<AuthResponse>(
    '/api/auth/login',
    {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    },
    false,
  )
}

export function fetchMe() {
  return request<User>('/api/auth/me')
}

export function listNotes() {
  return request<Note[]>('/api/notes')
}

export function createNote(payload: NoteInput) {
  return request<Note>('/api/notes', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function deleteNote(id: number) {
  return request<void>(`/api/notes/${id}`, { method: 'DELETE' })
}

export function runResearch(query: string, sessionId: string) {
  return request<ResearchResponse>('/api/agent/research', {
    method: 'POST',
    body: JSON.stringify({ query, session_id: sessionId }),
  })
}

export function getAgentMemory(sessionId: string) {
  return request<{ session_id: string; facts: string[] }>(`/api/agent/memory/${sessionId}`)
}

export function rememberFact(sessionId: string, fact: string) {
  return request<{ session_id: string; facts: string[] }>('/api/agent/memory', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, fact }),
  })
}

export type TraceEvent = {
  id: string
  timestamp: string
  agent: string
  tool: string
  phase: string
  arguments: Record<string, unknown>
  result_preview?: string | null
  error?: string | null
  duration_ms?: number | null
}

export type SupervisorResponse = {
  query: string
  route: string[]
  answer: string
  handoffs: Array<{ worker: string; summary: string; details: Record<string, unknown> }>
  traces: TraceEvent[]
}

export type MultiHopResponse = {
  question: string
  steps: string[]
  answer: string
  session_id: string
  traces: TraceEvent[]
}

export function runSupervisor(query: string, sessionId: string, filePath?: string) {
  return request<SupervisorResponse>('/api/orchestration/supervise', {
    method: 'POST',
    body: JSON.stringify({
      query,
      session_id: sessionId,
      file_path: filePath ?? null,
    }),
  })
}

export function runMultiHop(question: string, sessionId: string) {
  return request<MultiHopResponse>('/api/orchestration/multi-hop', {
    method: 'POST',
    body: JSON.stringify({ question, session_id: sessionId }),
  })
}

export function listTraces() {
  return request<{ events: TraceEvent[] }>('/api/orchestration/traces')
}
