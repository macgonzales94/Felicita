import React, { createContext, useContext, useState, useEffect } from 'react'
import { authService } from '../servicios/auth'
import type { Usuario } from '../types/auth'

interface AuthContextType {
  usuario: Usuario | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      authService.getCurrentUser()
        .then(setUsuario)
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (username: string, password: string) => {
    const { usuario, access } = await authService.login(username, password)
    localStorage.setItem('token', access)
    setUsuario(usuario)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUsuario(null)
  }

  const value = {
    usuario,
    isLoading,
    login,
    logout,
    isAuthenticated: !!usuario,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
