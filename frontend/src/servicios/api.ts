/**
 * FELICITA - Configuración Base API
 * Sistema de Facturación Electrónica para Perú
 * 
 * Configuración de Axios con interceptores para JWT
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { toast } from 'react-hot-toast'

// ===========================================
// CONFIGURACIÓN BASE
// ===========================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Crear instancia de Axios
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// ===========================================
// UTILIDADES DE TOKEN
// ===========================================

interface TokenData {
  access: string
  refresh: string
}

class TokenManager {
  private static readonly ACCESS_TOKEN_KEY = 'felicita_access_token'
  private static readonly REFRESH_TOKEN_KEY = 'felicita_refresh_token'

  static getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY)
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY)
  }

  static setTokens(tokens: TokenData): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, tokens.access)
    localStorage.setItem(this.REFRESH_TOKEN_KEY, tokens.refresh)
  }

  static clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY)
    localStorage.removeItem(this.REFRESH_TOKEN_KEY)
  }

  static isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.exp * 1000 < Date.now()
    } catch {
      return true
    }
  }
}

// ===========================================
// INTERCEPTORES
// ===========================================

// Variable para evitar múltiples refrescos simultáneos
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: any) => void
  reject: (error: any) => void
}> = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  
  failedQueue = []
}

// Interceptor de request - agregar token
api.interceptors.request.use(
  (config) => {
    const token = TokenManager.getAccessToken()
    
    if (token && !TokenManager.isTokenExpired(token)) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Log de peticiones en desarrollo
    if (import.meta.env.DEV) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor de response - manejar errores y refrescar token
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log de respuestas exitosas en desarrollo
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    }
    
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any
    
    // Log de errores en desarrollo
    if (import.meta.env.DEV) {
      console.error(`❌ API Error: ${error.response?.status} ${originalRequest?.url}`)
    }
    
    // Si es error 401 y no es una petición de login/refresh
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/login/') &&
      !originalRequest.url?.includes('/auth/token/refresh/')
    ) {
      // Evitar múltiples refrescos simultáneos
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = TokenManager.getRefreshToken()
      
      if (refreshToken && !TokenManager.isTokenExpired(refreshToken)) {
        try {
          const response = await axios.post(`${API_BASE_URL}/usuarios/auth/token/refresh/`, {
            refresh: refreshToken
          })
          
          const newAccessToken = response.data.access
          TokenManager.setTokens({
            access: newAccessToken,
            refresh: response.data.refresh || refreshToken
          })
          
          processQueue(null, newAccessToken)
          
          // Reintentar petición original
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return api(originalRequest)
          
        } catch (refreshError) {
          processQueue(refreshError, null)
          TokenManager.clearTokens()
          
          // Redirigir a login
          window.location.href = '/login'
          
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      } else {
        // No hay refresh token válido
        TokenManager.clearTokens()
        window.location.href = '/login'
        return Promise.reject(error)
      }
    }
    
    // Manejar otros errores
    if (error.response?.status === 403) {
      toast.error('No tienes permisos para realizar esta acción')
    } else if (error.response?.status === 404) {
      toast.error('Recurso no encontrado')
    } else if (error.response?.status === 422) {
      toast.error('Datos inválidos')
    } else if (error.response?.status === 429) {
      toast.error('Demasiadas peticiones. Intenta más tarde.')
    } else if (error.response?.status >= 500) {
      toast.error('Error interno del servidor')
    }
    
    return Promise.reject(error)
  }
)

// ===========================================
// FUNCIONES UTILITARIAS
// ===========================================

export const handleApiError = (error: any) => {
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }
  
  if (error.response?.data) {
    // Manejar errores de validación del formulario
    const errors = error.response.data
    if (typeof errors === 'object') {
      const firstError = Object.values(errors)[0]
      if (Array.isArray(firstError)) {
        return firstError[0]
      }
      return firstError
    }
  }
  
  return error.message || 'Error desconocido'
}

export const createFormData = (data: Record<string, any>): FormData => {
  const formData = new FormData()
  
  Object.keys(data).forEach(key => {
    const value = data[key]
    if (value !== null && value !== undefined) {
      if (value instanceof File) {
        formData.append(key, value)
      } else if (Array.isArray(value)) {
        value.forEach(item => formData.append(key, item))
      } else {
        formData.append(key, String(value))
      }
    }
  })
  
  return formData
}

// ===========================================
// EXPORTACIONES
// ===========================================

export default api
export { TokenManager }
export type { TokenData }