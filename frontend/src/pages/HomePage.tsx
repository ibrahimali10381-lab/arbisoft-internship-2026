import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useNotes } from '../context/NotesContext'

export function HomePage() {
  const { user } = useAuth()
  const { notes, loading, error } = useNotes()

  return (
    <section className="hero-panel">
      <p className="eyebrow">Weeks 1–4 · NotesLab</p>
      <h1>Full-stack notes with JWT auth and a SerpAPI research agent.</h1>
      <p className="lede">
        Week 3 adds login, RBAC, and API/integration tests. Week 4 adds a research agent with web
        search + session memory.
      </p>
      <div className="cta-row">
        {user ? (
          <>
            <Link className="button primary" to="/notes">
              Browse notes
            </Link>
            <Link className="button ghost" to="/research">
              Open research agent
            </Link>
          </>
        ) : (
          <Link className="button primary" to="/login">
            Log in to continue
          </Link>
        )}
      </div>
      <dl className="stat-row">
        <div>
          <dt>Signed in</dt>
          <dd>{user ? user.username : 'no'}</dd>
        </div>
        <div>
          <dt>Notes</dt>
          <dd>{user ? (loading ? '…' : notes.length) : '—'}</dd>
        </div>
        <div>
          <dt>Role</dt>
          <dd>{user?.role ?? 'guest'}</dd>
        </div>
      </dl>
      {error ? <p className="banner error">{error}</p> : null}
    </section>
  )
}
