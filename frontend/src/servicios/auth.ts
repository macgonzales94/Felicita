/**
 * FELICITA - Servicio de Autenticación
 * Sistema de Facturación Electrónica para Perú
 * 
 * Servicio completo para manejo de autenticación JWT
 */

import api, { TokenManager, handleApiError } from './api'
import type { Usuario, LoginRequest, LoginResponse, CambiarPasswordRequest, RegistroRequest } from '../types/auth'

// ===========================================
// INTERFACES ESPECÍFICAS
// ===========================================

interface SesionActiva {
  id: number
  token_jti: string
  ip_address: string
  user_agent: string
  dispositivo_info: {
    navegador: string
    sistema: string
    dispositivo: string
  }
  ubicacion?: string
  fecha_inicio: string
  ultima_actividad: string
  fecha_expiracion: string
}

interface VerificarPermisosRequest {
  permisos: string[]
}

interface VerificarPermisosResponse {
  usuario: string
  rol: string
  permisos: Record<string, boolean>
}

interface EstadisticasUsuarios {
  total_usuarios: number
  usuarios_activos: number
  usuarios_inactivos: number
  por_rol: Record<string, number>
  sesiones_activas: number
}

// ===========================================
// CLASE SERVICIO AUTENTICACIÓN
// ===========================================

class AuthService {
  /**
   * Iniciar sesión con credenciales
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>('/usuarios/auth/login/', credentials)
      
      // Guardar tokens
      TokenManager.setTokens({
        access: response.data.access,
        refresh: response.data.refresh
      })
      
      // Log en desarrollo
      if (import.meta.env.DEV) {
        console.log('🔐 Login exitoso:', response.data.usuario.username)
      }
      
      return response.data
    } catch (error) {
      console.error('❌ Error en login:', error)
      throw new Error(handleApiError(error))
    }
  }

  /**
   * Cerrar sesión
   */
  async logout(): Promise<void> {
    try {
      const refreshToken = TokenManager.getRefreshToken()
      
      if (refreshToken) {
        await api.post('/usuarios/auth/logout/', {
          refresh_token: refreshToken
        })
      }
      
      // Limpiar tokens localmente
      TokenManager.clearTokens()
      
      if (import.meta.env.DEV) {
        console.log('👋 Logout exitoso')
      }
    } catch (error) {
      // Aunque falle el logout en el servidor, limpiar tokens localmente
      TokenManager.clearTokens()
      console.error('⚠️ Error en logout:', error)
    }
  }

  /**
   * Registrar nuevo usuario
   */
  async registro(data: RegistroRequest): Promise<{ message: string; usuario_id: number }> {
    try {
      const response = await api.post('/usuarios/auth/registro/', data)
      return response.data
    } catch (error) {
      throw new Error(handleApiError(error))
    }
  }

  /**
   * Obtener perfil del usuario autenticado
   */
  async getCurrentUser(): Promise<Usuario> {
    try {
      const response = await api.get<Usuario>('/usuarios/usuarios/perfil/')
      return response.data
    } catch (error) {
      throw new Error(handleApiError(error))
    }
  }

  /**
   * Actualizar perfil del usuario
   */
  async updateProfile(data: Partial<Usuario>): Promise<Usuario> {
    try {
      const response = await api.patch<Usuario>('/usuarios/usuarios/perfil/', data)
      return response.data
    } catch (error) {
      throw new Error(handleApiError(error))
    }
  }

  /**
   * Cambiar contraseña
   */
  async cambiarPassword(data: CambiarPasswordRequest): Promise<{ message: string }> {
    try {
      const response = await api.post('/usuarios/usuarios/cambiar_password/', data)
      
      // Limpiar tokens porque se invalidaron las sesiones
      TokenManager.clearTokens()
      
      return response.data
    } catch (error) {
      throw new Error(handleApiError(error))
    }
  }

  /**
   * Obtener sesiones activas
   */
  async getSesionesActivas(): Promise<SesionActiva[]> {
    try {
      const response = await api.get<SesionActiva[]>('/usuarios/usuarios/sesiones_activas/')
      return response.data
    } catch (error) {
      throw new Error(handleApiError(error))
    }
  }

  /**
   * Cerrar sesión específica
   */
  async cerrarSesion(tokenJti: string): Promise<{ message: string }> {
    try {
      const response = await api.post('/usuarios/usuarios/cerrar_sesion/', {
        token_jti: tokenJti
      })
      return response.data
    } catch (error) {
      throw new Error(handleApiError(error))
    }
  }

  /**
   * Cerrar todas las sesiones
   */
  async cerrarTodasSesiones(): Promise<{ message: string }> {
    try {
      const response = await api.post('/usuarios/usuarios/cerrar_todas_sesiones/')
      
      // Limpiar tokens locales
      TokenManager.clearTokens()
      
      return response.data
    } catch (error) {
      throw new Error(handleApiError(error))
    }
  }

  /**
   * Verificar permisos específicos
   */
  async verificarPermisos(permisos: string[]): Promise<VerificarPermisosResponse> {
    try {
      const response = await api.post<VerificarPermisosResponse>('/usuarios/auth/verificar-permisos/', {
        permisos
      })
      return response.data
    } catch (error) {
      throw new Error(handleApiError(error))
    }
  }

  /**
   * Refrescar token de acceso
   */
  async refreshToken(): Promise<string> {
    try {
      const refreshToken = TokenManager.getRefreshToken()
      
      if (!refreshToken) {
        throw new Error('No hay refresh token disponible')
      }
      
      const response = await api.post('/usuarios/auth/token/refresh/', {
        refresh: refreshToken
      })
      
      const newTokens = {
        access: response.data.access,
        refresh: response.data.refresh || refreshToken
      }
      
      TokenManager.setTokens(newTokens)
      
      return newTokens.access
    } catch (error) {
      TokenManager.clearTokens()
      throw new Error(handleApiError(error))
    }
  }

  /**
   * Verificar si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    const token = TokenManager.getAccessToken()
    return token !== null && !TokenManager.isTokenExpired(token)
  }

  /**
   * Obtener información del token actual
   */
  getTokenInfo(): { user_id: number; username: string; exp: number } | null {
    const token = TokenManager.getAccessToken()
    
    if (!token) return null
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return {
        user_id: payload.user_id,
        username: payload.username,
        exp: payload.exp
      }
    } catch {
      return null
    }
  }

  /**
   * Obtener estadísticas de usuarios (solo admin/contador)
   */
  async getEstadisticasUsuarios(): Promise<EstadisticasUsuarios> {
    try {
      const response = await api.get<EstadisticasUsuarios>('/usuarios/usuarios/estadisticas/')
      return response.data
    } catch (error) {
      throw new Error(handleApiError(error))
    }
  }
}

// ===========================================
// INSTANCIA SINGLETON
// ===========================================

const authService = new AuthService()

// ===========================================
// UTILIDADES ADICIONALES
// ===========================================

/**
 * Hook para verificar permisos
 */
export const usePermissions = () => {
  const verificarPermiso = async (permiso: string): Promise<boolean> => {
    try {
      const result = await authService.verificarPermisos([permiso])
      return result.permisos[permiso] || false
    } catch {
      return false
    }
  }

  const verificarPermisos = async (permisos: string[]): Promise<Record<string, boolean>> => {
    try {
      const result = await authService.verificarPermisos(permisos)
      return result.permisos
    } catch {
      return permisos.reduce((acc, permiso) => {
        acc[permiso] = false
        return acc
      }, {} as Record<string, boolean>)
    }
  }

  return { verificarPermiso, verificarPermisos }
}

/**
 * Utilidad para verificar rol
 */
export const hasRole = (usuario: Usuario | null, roles: string[]): boolean => {
  if (!usuario) return false
  return roles.includes(usuario.rol)
}

/**
 * Utilidad para verificar permiso específico
 */
export const hasPermission = (usuario: Usuario | null, permiso: string): boolean => {
  if (!usuario) return false
  return usuario.permisos.includes(permiso) || usuario.permisos.includes('*')
}

// ===========================================
// EXPORTACIONES
// ===========================================

export default authService
export { AuthService }
export type { 
  SesionActiva, 
  VerificarPermisosRequest, 
  VerificarPermisosResponse, 
  EstadisticasUsuarios 
}