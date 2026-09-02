import { useNavigate } from 'react-router-dom'
import { NoteForm } from '../components/NoteForm'
import { useNotes } from '../context/NotesContext'

export function NewNotePage() {
  const navigate = useNavigate()
  const { addNote, error } = useNotes()

  return (
    <section className="narrow">
      <p className="eyebrow">Create</p>
      <h1>New note</h1>
      <p className="lede">
        Ownership comes from your JWT — no owner picker needed. Client-side validation still runs
        first.
      </p>
      {error ? <p className="banner error">{error}</p> : null}
      <NoteForm
        onSubmit={async (values) => {
          await addNote(values)
          navigate('/notes')
        }}
      />
    </section>
  )
}
