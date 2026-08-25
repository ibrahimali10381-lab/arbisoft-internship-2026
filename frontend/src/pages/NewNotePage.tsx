import { useNavigate } from 'react-router-dom'
import { NoteForm } from '../components/NoteForm'
import { useNotes } from '../context/NotesContext'

export function NewNotePage() {
  const navigate = useNavigate()
  const { users, addNote, error } = useNotes()

  return (
    <section className="narrow">
      <p className="eyebrow">Create</p>
      <h1>New note</h1>
      <p className="lede">
        Client-side validation runs before the request hits the API. Invalid fields never leave the
        browser.
      </p>
      {error ? <p className="banner error">{error}</p> : null}
      <NoteForm
        users={users}
        onSubmit={async (values) => {
          await addNote(values)
          navigate('/notes')
        }}
      />
    </section>
  )
}
