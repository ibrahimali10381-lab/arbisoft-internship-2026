import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import {
  fetchMe,
  getStoredToken,
  login as apiLogin,
  register as apiRegister,
  setStoredToken,
  type User,
} from '../api/client'

type AuthContextValue = {
  user: User | null
  token: string | null
  loading: boolean
  error: string | null
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(getStoredToken())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function bootstrap() {
      if (!token) {
        setLoading(false)
        return
      }
      try {
        const me = await fetchMe()
        setUser(me)
      } catch {
        setStoredToken(null)
        setToken(null)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }
    void bootstrap()
  }, [token])

  const login = useCallback(async (username: string, password: string) => {
    setError(null)
    const result = await apiLogin(username, password)
    setStoredToken(result.access_token)
    setToken(result.access_token)
    setUser(result.user)
  }, [])

  const register = useCallback(async (username: string, email: string, password: string) => {
    setError(null)
    const result = await apiRegister(username, email, password)
    setStoredToken(result.access_token)
    setToken(result.access_token)
    setUser(result.user)
  }, [])

  const logout = useCallback(() => {
    setStoredToken(null)
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, token, loading, error, login, register, logout }),
    [user, token, loading, error, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
