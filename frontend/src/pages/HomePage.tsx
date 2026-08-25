import { Link } from 'react-router-dom'
import { useNotes } from '../context/NotesContext'

export function HomePage() {
  const { notes, users, loading, error } = useNotes()

  return (
    <section className="hero-panel">
      <p className="eyebrow">Week 1 · Frontend Fundamentals</p>
      <h1>A small notes SPA wired to a real API.</h1>
      <p className="lede">
        Three routes, shared layout, client-side validation, and fetch-based API calls — built for
        the Arbisoft AI-Focused Internship Program 2026.
      </p>
      <div className="cta-row">
        <Link className="button primary" to="/notes">
          Browse notes
        </Link>
        <Link className="button ghost" to="/notes/new">
          Create a note
        </Link>
      </div>
      <dl className="stat-row">
        <div>
          <dt>Notes loaded</dt>
          <dd>{loading ? '…' : notes.length}</dd>
        </div>
        <div>
          <dt>Users</dt>
          <dd>{loading ? '…' : users.length}</dd>
        </div>
        <div>
          <dt>API</dt>
          <dd>{error ? 'offline' : 'ready'}</dd>
        </div>
      </dl>
      {error ? <p className="banner error">{error}</p> : null}
    </section>
  )
}
