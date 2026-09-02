import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import { NotesProvider } from './context/NotesContext'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { NewNotePage } from './pages/NewNotePage'
import { NotesPage } from './pages/NotesPage'
import { ResearchPage } from './pages/ResearchPage'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <NotesProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route element={<ProtectedRoute />}>
                <Route path="/notes" element={<NotesPage />} />
                <Route path="/notes/new" element={<NewNotePage />} />
                <Route path="/research" element={<ResearchPage />} />
              </Route>
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </NotesProvider>
    </AuthProvider>
  )
}

export default App
