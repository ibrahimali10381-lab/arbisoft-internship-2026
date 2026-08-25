import { Link } from 'react-router-dom'
import { useNotes } from '../context/NotesContext'

export function NotesPage() {
  const { notes, users, loading, error, removeNote, refresh } = useNotes()

  return (
    <section>
      <div className="section-head">
        <div>
          <p className="eyebrow">Notes</p>
          <h1>Your notes</h1>
          <p className="lede">Fetched from the FastAPI CRUD backend.</p>
        </div>
        <div className="cta-row">
          <button type="button" className="button ghost" onClick={() => void refresh()}>
            Refresh
          </button>
          <Link className="button primary" to="/notes/new">
            New note
          </Link>
        </div>
      </div>

      {loading ? <p>Loading notes…</p> : null}
      {error ? <p className="banner error">{error}</p> : null}

      {!loading && !error && notes.length === 0 ? (
        <p className="empty">No notes yet. Create one to get started.</p>
      ) : null}

      <ul className="note-list">
        {notes.map((note) => {
          const owner = users.find((user) => user.id === note.owner_id)
          return (
            <li key={note.id} className="note-card">
              <div>
                <h2>{note.title}</h2>
                <p>{note.content}</p>
                <p className="meta">
                  Owner: {owner?.username ?? `user #${note.owner_id}`} · Updated{' '}
                  {new Date(note.updated_at).toLocaleString()}
                </p>
              </div>
              <button
                type="button"
                className="button danger"
                onClick={() => void removeNote(note.id)}
              >
                Delete
              </button>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
