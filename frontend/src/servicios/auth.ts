import api from './api'
import type { LoginRequest, LoginResponse, Usuario } from '../types/auth'

class AuthService {
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login/', {
      username,
      password,
    })
    return response.data
  }

  async getCurrentUser(): Promise<Usuario> {
    const response = await api.get<Usuario>('/auth/usuarios/perfil/')
    return response.data
  }

  async logout(): Promise<void> {
    localStorage.removeItem('token')
  }
}

export const authService = new AuthService()