import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">N</span>
          <div>
            <p className="brand-name">NotesLab</p>
            <p className="brand-sub">Arbisoft Internship 2026</p>
          </div>
        </div>
        <nav className="nav">
          <NavLink to="/" end>
            Home
          </NavLink>
          {user ? (
            <>
              <NavLink to="/notes">Notes</NavLink>
              <NavLink to="/notes/new">New Note</NavLink>
              <NavLink to="/research">Research</NavLink>
              <button type="button" className="button ghost nav-button" onClick={logout}>
                Log out ({user.username})
              </button>
            </>
          ) : (
            <NavLink to="/login">Log in</NavLink>
          )}
        </nav>
      </header>
      <main className="page">
        <Outlet />
      </main>
    </div>
  )
}
