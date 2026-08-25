import { NavLink, Outlet } from 'react-router-dom'

export function Layout() {
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
          <NavLink to="/notes">Notes</NavLink>
          <NavLink to="/notes/new">New Note</NavLink>
        </nav>
      </header>
      <main className="page">
        <Outlet />
      </main>
    </div>
  )
}
