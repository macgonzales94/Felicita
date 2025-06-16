/**
 * FELICITA - AuthContext Completo
 * Sistema de Facturación Electrónica para Perú
 * 
 * Contexto de autenticación con estado global y funcionalidades completas
 */

import React, { createContext, useContext, useState, useEffect, useReducer, useCallback } from 'react'
import { toast } from 'react-hot-toast'
import authService from '../servicios/auth'
import { TokenManager } from '../servicios/api'
import type { 
  Usuario, 
  LoginRequest, 
  LoginResponse, 
  AuthContextValue, 
  AuthState, 
  AuthAction,
  UsuarioRol,
  CambiarPasswordRequest,
  ActualizarPerfilRequest,
  SesionUsuario
} from '../types/auth'

// ===========================================
// REDUCER DE AUTENTICACIÓN
// ===========================================

const initialState: AuthState = {
  usuario: null,
  isLoading: true,
  isAuthenticated: false,
  error: null
}

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload
      }
    
    case 'SET_USER':
      return {
        ...state,
        usuario: action.payload,
        isAuthenticated: !!action.payload,
        isLoading: false,
        error: null
      }
    
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        usuario: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null
      }
    
    case 'LOGOUT':
      return {
        ...state,
        usuario: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      }
    
    case 'UPDATE_USER':
      return {
        ...state,
        usuario: state.usuario ? { ...state.usuario, ...action.payload } : null,
        error: null
      }
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false
      }
    
    default:
      return state
  }
}

// ===========================================
// CONTEXTO
// ===========================================

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

// ===========================================
// PROVIDER COMPONENT
// ===========================================

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // ===========================================
  // INICIALIZACIÓN
  // ===========================================

  useEffect(() => {
    initializeAuth()
  }, [])

  const initializeAuth = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      
      // Verificar si hay token válido
      const token = TokenManager.getAccessToken()
      
      if (token && !TokenManager.isTokenExpired(token)) {
        // Obtener información del usuario
        const usuario = await authService.getCurrentUser()
        dispatch({ type: 'SET_USER', payload: usuario })
      } else {
        // Limpiar tokens inválidos
        TokenManager.clearTokens()
        dispatch({ type: 'SET_USER', payload: null })
      }
    } catch (error) {
      console.error('Error inicializando auth:', error)
      TokenManager.clearTokens()
      dispatch({ type: 'SET_USER', payload: null })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  // ===========================================
  // FUNCIONES DE AUTENTICACIÓN
  // ===========================================

  const login = useCallback(async (credentials: LoginRequest): Promise<LoginResponse> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      dispatch({ type: 'SET_ERROR', payload: null })
      
      const response = await authService.login(credentials)
      
      dispatch({ type: 'LOGIN_SUCCESS', payload: response.usuario })
      
      toast.success(`¡Bienvenido, ${response.usuario.nombre_completo}!`)
      
      return response
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error de autenticación'
      dispatch({ type: 'SET_ERROR', payload: errorMessage })
      toast.error(errorMessage)
      throw error
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }, [])

  const logout = useCallback(async (): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      
      await authService.logout()
      
      dispatch({ type: 'LOGOUT' })
      
      toast.success('Sesión cerrada correctamente')
    } catch (error) {
      console.error('Error en logout:', error)
      // Aunque falle, limpiar estado local
      dispatch({ type: 'LOGOUT' })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }, [])

  const refreshUser = useCallback(async (): Promise<Usuario> => {
    try {
      const usuario = await authService.getCurrentUser()
      dispatch({ type: 'SET_USER', payload: usuario })
      return usuario
    } catch (error) {
      console.error('Error refrescando usuario:', error)
      TokenManager.clearTokens()
      dispatch({ type: 'LOGOUT' })
      throw error
    }
  }, [])

  // ===========================================
  // GESTIÓN DE PERFIL
  // ===========================================

  const updateProfile = useCallback(async (data: ActualizarPerfilRequest): Promise<Usuario> => {
    try {
      const usuarioActualizado = await authService.updateProfile(data)
      dispatch({ type: 'UPDATE_USER', payload: usuarioActualizado })
      toast.success('Perfil actualizado correctamente')
      return usuarioActualizado
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error actualizando perfil'
      toast.error(errorMessage)
      throw error
    }
  }, [])

  const changePassword = useCallback(async (data: CambiarPasswordRequest): Promise<void> => {
    try {
      await authService.cambiarPassword(data)
      
      // Limpiar estado porque se invalidaron las sesiones
      dispatch({ type: 'LOGOUT' })
      
      toast.success('Contraseña cambiada correctamente. Inicie sesión nuevamente.')
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error cambiando contraseña'
      toast.error(errorMessage)
      throw error
    }
  }, [])

  // ===========================================
  // GESTIÓN DE SESIONES
  // ===========================================

  const getSessions = useCallback(async (): Promise<SesionUsuario[]> => {
    try {
      return await authService.getSesionesActivas()
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error obteniendo sesiones'
      toast.error(errorMessage)
      throw error
    }
  }, [])

  const closeSessions = useCallback(async (tokenJti?: string): Promise<void> => {
    try {
      if (tokenJti) {
        await authService.cerrarSesion(tokenJti)
        toast.success('Sesión cerrada correctamente')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error cerrando sesión'
      toast.error(errorMessage)
      throw error
    }
  }, [])

  const closeAllSessions = useCallback(async (): Promise<void> => {
    try {
      await authService.cerrarTodasSesiones()
      
      // Limpiar estado local
      dispatch({ type: 'LOGOUT' })
      
      toast.success('Todas las sesiones han sido cerradas')
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error cerrando sesiones'
      toast.error(errorMessage)
      throw error
    }
  }, [])

  // ===========================================
  // VERIFICACIÓN DE PERMISOS
  // ===========================================

  const hasPermission = useCallback((permission: string): boolean => {
    if (!state.usuario) return false
    
    // Superusuario tiene todos los permisos
    if (state.usuario.rol === 'administrador') return true
    
    // Verificar permiso exacto
    if (state.usuario.permisos.includes(permission)) return true
    
    // Verificar wildcard completo
    if (state.usuario.permisos.includes('*')) return true
    
    // Verificar wildcard de módulo (ej: 'core.*')
    const modulo = permission.split('.')[0]
    if (state.usuario.permisos.includes(`${modulo}.*`)) return true
    
    return false
  }, [state.usuario])

  const hasRole = useCallback((roles: UsuarioRol[]): boolean => {
    if (!state.usuario) return false
    return roles.includes(state.usuario.rol)
  }, [state.usuario])

  const checkPermissions = useCallback(async (permissions: string[]): Promise<Record<string, boolean>> => {
    try {
      const result = await authService.verificarPermisos(permissions)
      return result.permisos
    } catch (error) {
      console.error('Error verificando permisos:', error)
      // Retornar todos como false en caso de error
      return permissions.reduce((acc, permission) => {
        acc[permission] = false
        return acc
      }, {} as Record<string, boolean>)
    }
  }, [])

  // ===========================================
  // VALOR DEL CONTEXTO
  // ===========================================

  const contextValue: AuthContextValue = {
    // Estado
    usuario: state.usuario,
    isLoading: state.isLoading,
    isAuthenticated: state.isAuthenticated,
    
    // Acciones principales
    login,
    logout,
    refreshUser,
    
    // Gestión de perfil
    updateProfile,
    changePassword,
    
    // Gestión de sesiones
    getSessions,
    closeSessions,
    closeAllSessions,
    
    // Permisos
    hasPermission,
    hasRole,
    checkPermissions
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

// ===========================================
// HOOK PERSONALIZADO
// ===========================================

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider')
  }
  
  return context
}

// ===========================================
// HOOKS ADICIONALES
// ===========================================

/**
 * Hook para verificar permisos específicos
 */
export function usePermissions(permissions: string[]) {
  const { hasPermission, checkPermissions } = useAuth()
  const [permissionsMap, setPermissionsMap] = useState<Record<string, boolean>>({})
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (permissions.length > 0) {
      setIsLoading(true)
      checkPermissions(permissions)
        .then(setPermissionsMap)
        .finally(() => setIsLoading(false))
    }
  }, [permissions, checkPermissions])

  return {
    permissions: permissionsMap,
    isLoading,
    hasPermission: (permission: string) => hasPermission(permission),
    hasAnyPermission: (perms: string[]) => perms.some(p => hasPermission(p)),
    hasAllPermissions: (perms: string[]) => perms.every(p => hasPermission(p))
  }
}

/**
 * Hook para verificar roles específicos
 */
export function useRoles(roles: UsuarioRol[]) {
  const { usuario, hasRole } = useAuth()

  return {
    hasRole: (role: UsuarioRol) => hasRole([role]),
    hasAnyRole: () => hasRole(roles),
    currentRole: usuario?.rol,
    isAdmin: hasRole(['administrador']),
    isContador: hasRole(['contador']),
    isVendedor: hasRole(['vendedor']),
    isSupervisor: hasRole(['supervisor']),
    isCliente: hasRole(['cliente'])
  }
}

/**
 * Hook para gestión de sesiones
 */
export function useSessions() {
  const { getSessions, closeSessions, closeAllSessions } = useAuth()
  const [sessions, setSessions] = useState<SesionUsuario[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const loadSessions = useCallback(async () => {
    try {
      setIsLoading(true)
      const sessionsData = await getSessions()
      setSessions(sessionsData)
    } catch (error) {
      console.error('Error cargando sesiones:', error)
    } finally {
      setIsLoading(false)
    }
  }, [getSessions])

  const closeSession = useCallback(async (tokenJti: string) => {
    try {
      await closeSessions(tokenJti)
      await loadSessions() // Recargar sesiones
    } catch (error) {
      console.error('Error cerrando sesión:', error)
    }
  }, [closeSessions, loadSessions])

  const closeAll = useCallback(async () => {
    try {
      await closeAllSessions()
      setSessions([]) // Limpiar sesiones localmente
    } catch (error) {
      console.error('Error cerrando todas las sesiones:', error)
    }
  }, [closeAllSessions])

  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  return {
    sessions,
    isLoading,
    loadSessions,
    closeSession,
    closeAll
  }
}

// ===========================================
// EXPORTACIONES
// ===========================================

export default AuthContext
export { AuthProvider, useAuth, usePermissions, useRoles, useSessions }