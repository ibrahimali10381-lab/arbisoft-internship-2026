import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function Layout() {
  const { user, logout } = useAuth()
  return (
    <div className="shell">
      <header className="topbar">
        <NavLink to="/" className="brand">
          StudySprint
        </NavLink>
        {user && (
          <nav>
            <NavLink to="/" end>
              Courses
            </NavLink>
            <NavLink to="/compare">Compare models</NavLink>
            <NavLink to="/traces">Traces</NavLink>
            <span className="muted">{user.username}</span>
            <button type="button" className="link" onClick={logout}>
              Log out
            </button>
          </nav>
        )}
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
