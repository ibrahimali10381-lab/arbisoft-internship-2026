import { useState, type FormEvent } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function LoginPage() {
  const { user, login, register, loading } = useAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState('demo')
  const [email, setEmail] = useState('demo@example.com')
  const [password, setPassword] = useState('demopass')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (!loading && user) {
    return <Navigate to="/notes" replace />
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      if (mode === 'login') {
        await login(username, password)
      } else {
        await register(username, email, password)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="narrow">
      <p className="eyebrow">Week 3 · Auth</p>
      <h1>{mode === 'login' ? 'Log in' : 'Create account'}</h1>
      <p className="lede">
        JWT-backed login for end-to-end notes CRUD. Seeded users: <code>demo/demopass</code> and{' '}
        <code>admin/adminpass</code>.
      </p>

      <form className="note-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Username</span>
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        {mode === 'register' ? (
          <label className="field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
        ) : null}
        <label className="field">
          <span>Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
        </label>
        {error ? (
          <p className="form-error" role="alert">
            {error}
          </p>
        ) : null}
        <button type="submit" disabled={submitting}>
          {submitting ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Register'}
        </button>
      </form>

      <p className="lede">
        {mode === 'login' ? (
          <>
            Need an account?{' '}
            <button type="button" className="linkish" onClick={() => setMode('register')}>
              Register
            </button>
          </>
        ) : (
          <>
            Already registered?{' '}
            <button type="button" className="linkish" onClick={() => setMode('login')}>
              Log in
            </button>
          </>
        )}{' '}
        · <Link to="/">Back home</Link>
      </p>
    </section>
  )
}
