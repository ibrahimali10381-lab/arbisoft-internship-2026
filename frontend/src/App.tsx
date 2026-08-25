import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { NotesProvider } from './context/NotesContext'
import { HomePage } from './pages/HomePage'
import { NewNotePage } from './pages/NewNotePage'
import { NotesPage } from './pages/NotesPage'
import './App.css'

function App() {
  return (
    <NotesProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/notes" element={<NotesPage />} />
            <Route path="/notes/new" element={<NewNotePage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </NotesProvider>
  )
}

export default App
