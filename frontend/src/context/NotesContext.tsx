import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import {
  createNote as apiCreateNote,
  deleteNote as apiDeleteNote,
  listNotes,
  listUsers,
  type Note,
  type NoteInput,
  type User,
} from '../api/notes'

type NotesContextValue = {
  notes: Note[]
  users: User[]
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  addNote: (input: NoteInput) => Promise<Note>
  removeNote: (id: number) => Promise<void>
}

const NotesContext = createContext<NotesContextValue | null>(null)

export function NotesProvider({ children }: { children: ReactNode }) {
  const [notes, setNotes] = useState<Note[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [nextNotes, nextUsers] = await Promise.all([listNotes(), listUsers()])
      setNotes(nextNotes)
      setUsers(nextUsers)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }, [])

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
      users,
      loading,
      error,
      refresh,
      addNote,
      removeNote,
    }),
    [notes, users, loading, error, refresh, addNote, removeNote],
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
