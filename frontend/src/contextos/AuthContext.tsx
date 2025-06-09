/**
 * AUTH CONTEXT - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Context global para manejo de estado de autenticación
 */

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import { toast } from 'react-hot-toast'
import api from '../servicios/api'
import type { 
  Usuario, 
  LoginCredentials, 
  LoginResponse, 
  CambiarPasswordData 
} from '../types'

// =============================================================================
// TIPOS DEL CONTEXT
// =============================================================================

/** Estados de autenticación */
type EstadoAuth = 'inicial' | 'cargando' | 'autenticado' | 'no_autenticado' | 'error'

/** Estado del AuthContext */
interface AuthState {
  usuario: Usuario | null
  estado: EstadoAuth
  token: string | null
  sesionId: string | null
  cargandoInicializacion: boolean
  error: string | null
  requiereCambioPassword: boolean
}

/** Acciones del AuthContext */
type AuthAction =
  | { type: 'INICIALIZANDO' }
  | { type: 'LOGIN_INICIANDO' }
  | { type: 'LOGIN_EXITOSO'; payload: { usuario: Usuario; token: string; sesionId: string; requiereCambioPassword: boolean } }
  | { type: 'LOGIN_FALLIDO'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'PERFIL_ACTUALIZADO'; payload: Usuario }
  | { type: 'PASSWORD_CAMBIADO' }
  | { type: 'ERROR'; payload: string }
  | { type: 'LIMPIAR_ERROR' }
  | { type: 'TOKEN_RENOVADO'; payload: string }

/** Props del contexto */
interface AuthContextType {
  // Estado
  usuario: Usuario | null
  estado: EstadoAuth
  cargandoInicializacion: boolean
  error: string | null
  requiereCambioPassword: boolean
  estaAutenticado: boolean
  
  // Funciones de autenticación
  iniciarSesion: (credenciales: LoginCredentials) => Promise<boolean>
  cerrarSesion: () => Promise<void>
  cambiarPassword: (datos: CambiarPasswordData) => Promise<boolean>
  actualizarPerfil: (datos: Partial<Usuario>) => Promise<boolean>
  verificarToken: () => Promise<boolean>
  limpiarError: () => void
  
  // Funciones de utilidad
  tienePermiso: (permiso: string) => boolean
  tieneRol: (rol: string) => boolean
  obtenerPermisos: () => string[]
  obtenerRoles: () => string[]
}

// =============================================================================
// ESTADO INICIAL
// =============================================================================
const estadoInicial: AuthState = {
  usuario: null,
  estado: 'inicial',
  token: null,
  sesionId: null,
  cargandoInicializacion: true,
  error: null,
  requiereCambioPassword: false
}

// =============================================================================
// REDUCER
// =============================================================================
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'INICIALIZANDO':
      return {
        ...state,
        cargandoInicializacion: true,
        error: null
      }

    case 'LOGIN_INICIANDO':
      return {
        ...state,
        estado: 'cargando',
        error: null
      }

    case 'LOGIN_EXITOSO':
      return {
        ...state,
        usuario: action.payload.usuario,
        token: action.payload.token,
        sesionId: action.payload.sesionId,
        estado: 'autenticado',
        requiereCambioPassword: action.payload.requiereCambioPassword,
        cargandoInicializacion: false,
        error: null
      }

    case 'LOGIN_FALLIDO':
      return {
        ...state,
        usuario: null,
        token: null,
        sesionId: null,
        estado: 'no_autenticado',
        cargandoInicializacion: false,
        error: action.payload,
        requiereCambioPassword: false
      }

    case 'LOGOUT':
      return {
        ...estadoInicial,
        cargandoInicializacion: false,
        estado: 'no_autenticado'
      }

    case 'PERFIL_ACTUALIZADO':
      return {
        ...state,
        usuario: action.payload
      }

    case 'PASSWORD_CAMBIADO':
      return {
        ...state,
        requiereCambioPassword: false
      }

    case 'ERROR':
      return {
        ...state,
        error: action.payload,
        estado: 'error'
      }

    case 'LIMPIAR_ERROR':
      return {
        ...state,
        error: null
      }

    case 'TOKEN_RENOVADO':
      return {
        ...state,
        token: action.payload
      }

    default:
      return state
  }
}

// =============================================================================
// CONTEXT
// =============================================================================
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// =============================================================================
// PROVIDER
// =============================================================================
interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, estadoInicial)

  // =============================================================================
  // FUNCIONES DE AUTENTICACIÓN
  // =============================================================================

  /**
   * Inicializar autenticación al cargar la app
   */
  const inicializarAuth = async (): Promise<void> => {
    try {
      dispatch({ type: 'INICIALIZANDO' })

      // Verificar si hay token guardado
      const tokenGuardado = api.getAccessToken()
      
      if (!tokenGuardado) {
        dispatch({ type: 'LOGIN_FALLIDO', payload: 'No hay sesión activa' })
        return
      }

      // Verificar si el token es válido
      const esValido = await verificarToken()
      
      if (!esValido) {
        // Token inválido, limpiar y redirigir a login
        api.clearTokens()
        dispatch({ type: 'LOGIN_FALLIDO', payload: 'Sesión expirada' })
        return
      }

      // Si llegamos aquí, el usuario está autenticado
      // El verificarToken ya actualizó el estado
      
    } catch (error) {
      console.error('Error al inicializar autenticación:', error)
      api.clearTokens()
      dispatch({ type: 'LOGIN_FALLIDO', payload: 'Error al verificar sesión' })
    }
  }

  /**
   * Iniciar sesión
   */
  const iniciarSesion = async (credenciales: LoginCredentials): Promise<boolean> => {
    try {
      dispatch({ type: 'LOGIN_INICIANDO' })

      const respuesta: LoginResponse = await api.auth.login(credenciales)

      dispatch({
        type: 'LOGIN_EXITOSO',
        payload: {
          usuario: respuesta.user,
          token: respuesta.access,
          sesionId: respuesta.session_id,
          requiereCambioPassword: respuesta.requires_password_change
        }
      })

      // Mostrar mensaje de bienvenida
      toast.success(`¡Bienvenido, ${respuesta.user.nombres}!`)

      return true

    } catch (error: any) {
      const mensajeError = error.response?.data?.error || 'Error al iniciar sesión'
      
      dispatch({
        type: 'LOGIN_FALLIDO',
        payload: mensajeError
      })

      toast.error(mensajeError)
      return false
    }
  }

  /**
   * Cerrar sesión
   */
  const cerrarSesion = async (): Promise<void> => {
    try {
      // Llamar al backend para invalidar el token
      await api.auth.logout()
      
    } catch (error) {
      console.error('Error al cerrar sesión en el backend:', error)
      // Continuar con el logout local aunque falle el backend
    } finally {
      // Limpiar estado local
      dispatch({ type: 'LOGOUT' })
      
      // Limpiar tokens del localStorage
      api.clearTokens()
      
      toast.success('Sesión cerrada correctamente')
    }
  }

  /**
   * Cambiar contraseña
   */
  const cambiarPassword = async (datos: CambiarPasswordData): Promise<boolean> => {
    try {
      await api.auth.changePassword(datos)
      
      dispatch({ type: 'PASSWORD_CAMBIADO' })
      toast.success('Contraseña cambiada correctamente')
      
      return true
      
    } catch (error: any) {
      const mensajeError = error.response?.data?.error || 'Error al cambiar contraseña'
      
      dispatch({ type: 'ERROR', payload: mensajeError })
      toast.error(mensajeError)
      
      return false
    }
  }

  /**
   * Actualizar perfil del usuario
   */
  const actualizarPerfil = async (datos: Partial<Usuario>): Promise<boolean> => {
    try {
      const usuarioActualizado = await api.auth.updateProfile(datos)
      
      dispatch({ type: 'PERFIL_ACTUALIZADO', payload: usuarioActualizado })
      toast.success('Perfil actualizado correctamente')
      
      return true
      
    } catch (error: any) {
      const mensajeError = error.response?.data?.error || 'Error al actualizar perfil'
      
      dispatch({ type: 'ERROR', payload: mensajeError })
      toast.error(mensajeError)
      
      return false
    }
  }

  /**
   * Verificar si el token es válido
   */
  const verificarToken = async (): Promise<boolean> => {
    try {
      const respuesta = await api.auth.validateToken()
      
      if (respuesta.valid && respuesta.user) {
        dispatch({
          type: 'LOGIN_EXITOSO',
          payload: {
            usuario: respuesta.user,
            token: api.getAccessToken() || '',
            sesionId: '', // TODO: Obtener de la respuesta si está disponible
            requiereCambioPassword: respuesta.user.requiere_cambio_password
          }
        })
        
        return true
      }
      
      return false
      
    } catch (error) {
      console.error('Error al verificar token:', error)
      return false
    }
  }

  /**
   * Limpiar error
   */
  const limpiarError = (): void => {
    dispatch({ type: 'LIMPIAR_ERROR' })
  }

  // =============================================================================
  // FUNCIONES DE UTILIDAD
  // =============================================================================

  /**
   * Verificar si el usuario tiene un permiso específico
   */
  const tienePermiso = (permiso: string): boolean => {
    if (!state.usuario) return false
    
    // Los superusuarios tienen todos los permisos
    if (state.usuario.is_superuser) return true
    
    // Verificar en la lista de permisos del usuario
    return state.usuario.permisos?.includes(permiso) || false
  }

  /**
   * Verificar si el usuario tiene un rol específico
   */
  const tieneRol = (rol: string): boolean => {
    if (!state.usuario) return false
    
    // Verificar en la lista de roles del usuario
    return state.usuario.roles?.some(r => r.nombre === rol) || false
  }

  /**
   * Obtener lista de permisos del usuario
   */
  const obtenerPermisos = (): string[] => {
    return state.usuario?.permisos || []
  }

  /**
   * Obtener lista de roles del usuario
   */
  const obtenerRoles = (): string[] => {
    return state.usuario?.roles?.map(r => r.nombre) || []
  }

  // =============================================================================
  // EFFECTS
  // =============================================================================

  /**
   * Inicializar autenticación al montar el componente
   */
  useEffect(() => {
    inicializarAuth()
  }, [])

  /**
   * Configurar interceptor para tokens expirados
   */
  useEffect(() => {
    // Escuchar eventos de token expirado
    const manejarTokenExpirado = () => {
      dispatch({ type: 'LOGOUT' })
      toast.error('Sesión expirada. Por favor, inicia sesión nuevamente.')
    }

    // Este interceptor ya está configurado en api.ts
    // Solo agregamos el listener para eventos personalizados si fuera necesario
    window.addEventListener('auth:token-expired', manejarTokenExpirado)

    return () => {
      window.removeEventListener('auth:token-expired', manejarTokenExpirado)
    }
  }, [])

  // =============================================================================
  // VALOR DEL CONTEXT
  // =============================================================================
  const contextValue: AuthContextType = {
    // Estado
    usuario: state.usuario,
    estado: state.estado,
    cargandoInicializacion: state.cargandoInicializacion,
    error: state.error,
    requiereCambioPassword: state.requiereCambioPassword,
    estaAutenticado: state.estado === 'autenticado' && !!state.usuario,

    // Funciones de autenticación
    iniciarSesion,
    cerrarSesion,
    cambiarPassword,
    actualizarPerfil,
    verificarToken,
    limpiarError,

    // Funciones de utilidad
    tienePermiso,
    tieneRol,
    obtenerPermisos,
    obtenerRoles
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

// =============================================================================
// HOOK PARA USAR EL CONTEXT
// =============================================================================
export const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext)
  
  if (context === undefined) {
    throw new Error('useAuthContext debe ser usado dentro de un AuthProvider')
  }
  
  return context
}

// =============================================================================
// HOOK PARA VERIFICAR AUTENTICACIÓN
// =============================================================================
export const useRequireAuth = () => {
  const { estaAutenticado, cargandoInicializacion } = useAuthContext()
  
  return {
    estaAutenticado,
    cargandoInicializacion,
    requiereAuth: !estaAutenticado && !cargandoInicializacion
  }
}

// =============================================================================
// HOOK PARA VERIFICAR PERMISOS
// =============================================================================
export const usePermisos = () => {
  const { tienePermiso, tieneRol, obtenerPermisos, obtenerRoles } = useAuthContext()
  
  return {
    tienePermiso,
    tieneRol,
    obtenerPermisos,
    obtenerRoles
  }
}

export default AuthContext