export type Note = {
  id: number
  title: string
  content: string
  owner_id: number
  created_at: string
  updated_at: string
}

export type User = {
  id: number
  username: string
  email: string
  created_at: string
}

export type NoteInput = {
  title: string
  content: string
  owner_id: number
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = (await response.json()) as { detail?: string }
      if (typeof body.detail === 'string') {
        detail = body.detail
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

export function listNotes(): Promise<Note[]> {
  return request<Note[]>('/api/notes')
}

export function createNote(payload: NoteInput): Promise<Note> {
  return request<Note>('/api/notes', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function deleteNote(id: number): Promise<void> {
  return request<void>(`/api/notes/${id}`, { method: 'DELETE' })
}

export function listUsers(): Promise<User[]> {
  return request<User[]>('/api/users')
}
