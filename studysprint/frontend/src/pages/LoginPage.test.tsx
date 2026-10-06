import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../context/AuthContext'
import { LoginPage } from './LoginPage'

function renderLogin() {
  render(
    <AuthProvider>
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<p>Courses home</p>} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>,
  )
}

afterEach(() => {
  vi.restoreAllMocks()
  localStorage.clear()
})

describe('LoginPage', () => {
  it('logs in, stores the token and redirects', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          access_token: 'tok',
          user: { id: 1, username: 'demo', email: 'd@x.dev' },
        }),
        { status: 200 },
      ),
    )
    renderLogin()
    await userEvent.type(screen.getByLabelText('Username'), 'demo')
    await userEvent.type(screen.getByLabelText('Password'), 'demopass123')
    await userEvent.click(screen.getByRole('button', { name: 'Log in' }))
    expect(await screen.findByText('Courses home')).toBeInTheDocument()
    expect(localStorage.getItem('studysprint_token')).toBe('tok')
  })

  it('validates password length on sign up', async () => {
    renderLogin()
    await userEvent.click(screen.getByRole('button', { name: /Create an account/ }))
    await userEvent.type(screen.getByLabelText('Username'), 'newbie')
    await userEvent.type(screen.getByLabelText('Email'), 'n@x.dev')
    await userEvent.type(screen.getByLabelText('Password'), 'short')
    await userEvent.click(screen.getByRole('button', { name: 'Sign up' }))
    expect(screen.getByRole('alert')).toHaveTextContent('at least 8 characters')
  })
})
