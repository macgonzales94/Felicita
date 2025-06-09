/**
 * HOOK useAuth - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Hook personalizado para manejo de autenticación
 */

import { useState, useCallback, useMemo } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { useAuthContext } from '../contextos/AuthContext'
import type { 
  Usuario, 
  LoginCredentials, 
  CambiarPasswordData 
} from '../types'

// =============================================================================
// TIPOS DEL HOOK
// =============================================================================

/** Configuración de redirección después del login */
interface RedirectConfig {
  ruta?: string
  preservarHistorial?: boolean
}

/** Resultado del hook useAuth */
interface UseAuthResult {
  // Estado de autenticación
  usuario: Usuario | null
  estaAutenticado: boolean
  cargandoAuth: boolean
  cargandoAccion: boolean
  error: string | null
  requiereCambioPassword: boolean
  
  // Información del usuario
  nombreCompleto: string
  iniciales: string
  empresa: string
  rolesUsuario: string[]
  permisosUsuario: string[]
  
  // Funciones de autenticación
  login: (credenciales: LoginCredentials, config?: RedirectConfig) => Promise<boolean>
  logout: (mostrarMensaje?: boolean) => Promise<void>
  cambiarPassword: (datos: CambiarPasswordData) => Promise<boolean>
  actualizarPerfil: (datos: Partial<Usuario>) => Promise<boolean>
  
  // Funciones de utilidad
  tienePermiso: (permiso: string) => boolean
  tieneRol: (rol: string) => boolean
  tieneAlgunRol: (roles: string[]) => boolean
  tieneAlgunPermiso: (permisos: string[]) => boolean
  esAdministrador: boolean
  esContador: boolean
  esVendedor: boolean
  puedeAprobarFacturas: boolean
  
  // Funciones de navegación
  irALogin: (preservarRutaActual?: boolean) => void
  irADashboard: () => void
  irAPerfil: () => void
  
  // Funciones de estado
  limpiarError: () => void
  refrescarAuth: () => Promise<void>
}

// =============================================================================
// HOOK PRINCIPAL
// =============================================================================
export const useAuth = (): UseAuthResult => {
  // Hooks del contexto y navegación
  const {
    usuario,
    estado,
    cargandoInicializacion,
    error,
    requiereCambioPassword,
    estaAutenticado,
    iniciarSesion,
    cerrarSesion,
    cambiarPassword: cambiarPasswordContext,
    actualizarPerfil: actualizarPerfilContext,
    verificarToken,
    limpiarError: limpiarErrorContext,
    tienePermiso: tienePermisoContext,
    tieneRol: tieneRolContext,
    obtenerPermisos,
    obtenerRoles
  } = useAuthContext()
  
  const navigate = useNavigate()
  const location = useLocation()
  
  // Estado local para acciones específicas
  const [cargandoAccion, setCargandoAccion] = useState(false)

  // =============================================================================
  // COMPUTED VALUES
  // =============================================================================
  
  /** Información básica del usuario */
  const informacionUsuario = useMemo(() => {
    if (!usuario) {
      return {
        nombreCompleto: '',
        iniciales: '',
        empresa: '',
        rolesUsuario: [],
        permisosUsuario: []
      }
    }

    const nombreCompleto = `${usuario.nombres} ${usuario.apellido_paterno} ${usuario.apellido_materno}`.trim()
    const iniciales = `${usuario.nombres.charAt(0)}${usuario.apellido_paterno.charAt(0)}`.toUpperCase()
    const empresa = usuario.empresa?.razon_social || ''
    const rolesUsuario = obtenerRoles()
    const permisosUsuario = obtenerPermisos()

    return {
      nombreCompleto,
      iniciales,
      empresa,
      rolesUsuario,
      permisosUsuario
    }
  }, [usuario, obtenerRoles, obtenerPermisos])

  /** Verificación de roles específicos */
  const rolesEspecificos = useMemo(() => {
    const esAdministrador = tieneRolContext('Administrador') || usuario?.is_superuser || false
    const esContador = tieneRolContext('Contador')
    const esVendedor = tieneRolContext('Vendedor')
    const puedeAprobarFacturas = usuario?.puede_aprobar_facturas || esAdministrador

    return {
      esAdministrador,
      esContador,
      esVendedor,
      puedeAprobarFacturas
    }
  }, [usuario, tieneRolContext])

  // =============================================================================
  // FUNCIONES DE AUTENTICACIÓN
  // =============================================================================

  /**
   * Iniciar sesión con redirección personalizada
   */
  const login = useCallback(async (
    credenciales: LoginCredentials, 
    config: RedirectConfig = {}
  ): Promise<boolean> => {
    setCargandoAccion(true)
    
    try {
      const exitoso = await iniciarSesion(credenciales)
      
      if (exitoso) {
        // Determinar ruta de redirección
        const rutaDestino = config.ruta || 
                           (location.state as any)?.from?.pathname || 
                           '/dashboard'
        
        // Redireccionar
        if (config.preservarHistorial) {
          navigate(rutaDestino)
        } else {
          navigate(rutaDestino, { replace: true })
        }
      }
      
      return exitoso
      
    } catch (error) {
      console.error('Error en login:', error)
      return false
    } finally {
      setCargandoAccion(false)
    }
  }, [iniciarSesion, navigate, location.state])

  /**
   * Cerrar sesión con opciones de mensaje
   */
  const logout = useCallback(async (mostrarMensaje = true): Promise<void> => {
    setCargandoAccion(true)
    
    try {
      await cerrarSesion()
      
      // Redireccionar al login
      navigate('/login', { replace: true })
      
      if (mostrarMensaje) {
        toast.success('Sesión cerrada correctamente')
      }
      
    } catch (error) {
      console.error('Error en logout:', error)
      // Forzar redirección aunque falle
      navigate('/login', { replace: true })
    } finally {
      setCargandoAccion(false)
    }
  }, [cerrarSesion, navigate])

  /**
   * Cambiar contraseña con validaciones adicionales
   */
  const cambiarPassword = useCallback(async (datos: CambiarPasswordData): Promise<boolean> => {
    setCargandoAccion(true)
    
    try {
      // Validaciones adicionales
      if (datos.password_nueva.length < 8) {
        toast.error('La nueva contraseña debe tener al menos 8 caracteres')
        return false
      }
      
      if (datos.password_nueva !== datos.confirmar_password) {
        toast.error('Las contraseñas nuevas no coinciden')
        return false
      }
      
      const exitoso = await cambiarPasswordContext(datos)
      
      if (exitoso) {
        toast.success('Contraseña cambiada correctamente. Tu sesión permanece activa.')
      }
      
      return exitoso
      
    } catch (error) {
      console.error('Error al cambiar contraseña:', error)
      return false
    } finally {
      setCargandoAccion(false)
    }
  }, [cambiarPasswordContext])

  /**
   * Actualizar perfil del usuario
   */
  const actualizarPerfil = useCallback(async (datos: Partial<Usuario>): Promise<boolean> => {
    setCargandoAccion(true)
    
    try {
      const exitoso = await actualizarPerfilContext(datos)
      
      if (exitoso) {
        toast.success('Perfil actualizado correctamente')
      }
      
      return exitoso
      
    } catch (error) {
      console.error('Error al actualizar perfil:', error)
      return false
    } finally {
      setCargandoAccion(false)
    }
  }, [actualizarPerfilContext])

  // =============================================================================
  // FUNCIONES DE PERMISOS Y ROLES
  // =============================================================================

  /**
   * Verificar si el usuario tiene alguno de los roles especificados
   */
  const tieneAlgunRol = useCallback((roles: string[]): boolean => {
    return roles.some(rol => tieneRolContext(rol))
  }, [tieneRolContext])

  /**
   * Verificar si el usuario tiene alguno de los permisos especificados
   */
  const tieneAlgunPermiso = useCallback((permisos: string[]): boolean => {
    return permisos.some(permiso => tienePermisoContext(permiso))
  }, [tienePermisoContext])

  // =============================================================================
  // FUNCIONES DE NAVEGACIÓN
  // =============================================================================

  /**
   * Ir a la página de login
   */
  const irALogin = useCallback((preservarRutaActual = true): void => {
    const estadoNavegacion = preservarRutaActual ? { from: location } : undefined
    navigate('/login', { state: estadoNavegacion, replace: true })
  }, [navigate, location])

  /**
   * Ir al dashboard
   */
  const irADashboard = useCallback((): void => {
    navigate('/dashboard')
  }, [navigate])

  /**
   * Ir al perfil del usuario
   */
  const irAPerfil = useCallback((): void => {
    navigate('/perfil')
  }, [navigate])

  // =============================================================================
  // FUNCIONES DE ESTADO
  // =============================================================================

  /**
   * Limpiar error del estado
   */
  const limpiarError = useCallback((): void => {
    limpiarErrorContext()
  }, [limpiarErrorContext])

  /**
   * Refrescar autenticación
   */
  const refrescarAuth = useCallback(async (): Promise<void> => {
    setCargandoAccion(true)
    
    try {
      await verificarToken()
    } catch (error) {
      console.error('Error al refrescar autenticación:', error)
      toast.error('Error al verificar la sesión')
    } finally {
      setCargandoAccion(false)
    }
  }, [verificarToken])

  // =============================================================================
  // RETURN DEL HOOK
  // =============================================================================
  return {
    // Estado de autenticación
    usuario,
    estaAutenticado,
    cargandoAuth: cargandoInicializacion || estado === 'cargando',
    cargandoAccion,
    error,
    requiereCambioPassword,
    
    // Información del usuario
    ...informacionUsuario,
    
    // Funciones de autenticación
    login,
    logout,
    cambiarPassword,
    actualizarPerfil,
    
    // Funciones de utilidad
    tienePermiso: tienePermisoContext,
    tieneRol: tieneRolContext,
    tieneAlgunRol,
    tieneAlgunPermiso,
    ...rolesEspecificos,
    
    // Funciones de navegación
    irALogin,
    irADashboard,
    irAPerfil,
    
    // Funciones de estado
    limpiarError,
    refrescarAuth
  }
}

// =============================================================================
// HOOKS ESPECIALIZADOS
// =============================================================================

/**
 * Hook para proteger rutas que requieren autenticación
 */
export const useRequireAuth = () => {
  const { estaAutenticado, cargandoAuth, irALogin } = useAuth()
  
  // Auto-redireccionar si no está autenticado
  if (!cargandoAuth && !estaAutenticado) {
    irALogin()
  }
  
  return {
    estaAutenticado,
    cargandoAuth,
    requiereAutenticacion: !estaAutenticado && !cargandoAuth
  }
}

/**
 * Hook para verificar permisos específicos
 */
export const usePermisos = (permisosRequeridos: string[]) => {
  const { tienePermiso, tieneAlgunPermiso, permisosUsuario } = useAuth()
  
  const tienePermisosRequeridos = useMemo(() => {
    return permisosRequeridos.every(permiso => tienePermiso(permiso))
  }, [permisosRequeridos, tienePermiso])
  
  const tieneAlgunoDePermisos = useMemo(() => {
    return tieneAlgunPermiso(permisosRequeridos)
  }, [permisosRequeridos, tieneAlgunPermiso])
  
  return {
    tienePermisosRequeridos,
    tieneAlgunoDePermisos,
    permisosUsuario,
    permisosFaltantes: permisosRequeridos.filter(p => !tienePermiso(p))
  }
}

/**
 * Hook para verificar roles específicos
 */
export const useRoles = (rolesRequeridos: string[]) => {
  const { tieneRol, tieneAlgunRol, rolesUsuario } = useAuth()
  
  const tieneRolesRequeridos = useMemo(() => {
    return rolesRequeridos.every(rol => tieneRol(rol))
  }, [rolesRequeridos, tieneRol])
  
  const tieneAlgunoDeRoles = useMemo(() => {
    return tieneAlgunRol(rolesRequeridos)
  }, [rolesRequeridos, tieneAlgunRol])
  
  return {
    tieneRolesRequeridos,
    tieneAlgunoDeRoles,
    rolesUsuario,
    rolesFaltantes: rolesRequeridos.filter(r => !tieneRol(r))
  }
}

/**
 * Hook para manejar el estado de carga durante operaciones de auth
 */
export const useAuthLoading = () => {
  const { cargandoAuth, cargandoAccion } = useAuth()
  
  return {
    cargandoAuth,
    cargandoAccion,
    cargandoGeneral: cargandoAuth || cargandoAccion
  }
}

export default useAuth