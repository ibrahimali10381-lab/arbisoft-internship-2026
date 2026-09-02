import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import {
  createNote as apiCreateNote,
  deleteNote as apiDeleteNote,
  listNotes,
  type Note,
  type NoteInput,
} from '../api/client'
import { useAuth } from './AuthContext'

type NotesContextValue = {
  notes: Note[]
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  addNote: (input: NoteInput) => Promise<Note>
  removeNote: (id: number) => Promise<void>
}

const NotesContext = createContext<NotesContextValue | null>(null)

export function NotesProvider({ children }: { children: ReactNode }) {
  const { token } = useAuth()
  const [notes, setNotes] = useState<Note[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    if (!token) {
      setNotes([])
      setError(null)
      return
    }
    setLoading(true)
    setError(null)
    try {
      setNotes(await listNotes())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load notes')
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const addNote = useCallback(async (input: NoteInput) => {
    const note = await apiCreateNote(input)
    setNotes((current) => [note, ...current])
    return note
  }, [])

  const removeNote = useCallback(async (id: number) => {
    await apiDeleteNote(id)
    setNotes((current) => current.filter((note) => note.id !== id))
  }, [])

  const value = useMemo(
    () => ({
      notes,
      loading,
      error,
      refresh,
      addNote,
      removeNote,
    }),
    [notes, loading, error, refresh, addNote, removeNote],
  )

  return <NotesContext.Provider value={value}>{children}</NotesContext.Provider>
}

export function useNotes() {
  const context = useContext(NotesContext)
  if (!context) {
    throw new Error('useNotes must be used within NotesProvider')
  }
  return context
}
