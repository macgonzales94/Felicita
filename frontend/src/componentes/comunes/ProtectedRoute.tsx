/**
 * FELICITA - ProtectedRoute Mejorado
 * Sistema de Facturación Electrónica para Perú
 * 
 * Componente para proteger rutas con verificación de autenticación, roles y permisos
 */

import React, { useState, useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { ShieldAlert, Lock, AlertTriangle, Loader } from 'lucide-react'
import { useAuth } from '../contextos/AuthContext'
import type { UsuarioRol } from '../types/auth'

// ===========================================
// INTERFACES
// ===========================================

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRoles?: UsuarioRol[]
  requiredPermissions?: string[]
  requireAllPermissions?: boolean
  fallbackPath?: string
  showUnauthorized?: boolean
}

interface UnauthorizedProps {
  type: 'not-authenticated' | 'insufficient-role' | 'insufficient-permissions'
  requiredRoles?: UsuarioRol[]
  requiredPermissions?: string[]
  userRole?: UsuarioRol
}

// ===========================================
// COMPONENTE DE CARGA
// ===========================================

function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="flex flex-col items-center space-y-4">
        <div className="relative">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <Loader className="h-6 w-6 text-blue-600" />
          </div>
        </div>
        <p className="text-gray-600 font-medium">Verificando permisos...</p>
      </div>
    </div>
  )
}

// ===========================================
// COMPONENTE NO AUTORIZADO
// ===========================================

function UnauthorizedAccess({ type, requiredRoles, requiredPermissions, userRole }: UnauthorizedProps) {
  const getContent = () => {
    switch (type) {
      case 'not-authenticated':
        return {
          icon: Lock,
          title: 'Acceso Restringido',
          message: 'Necesitas iniciar sesión para acceder a esta página.',
          action: 'Ir al Login',
          actionPath: '/login'
        }
      
      case 'insufficient-role':
        return {
          icon: ShieldAlert,
          title: 'Permisos Insuficientes',
          message: `Tu rol actual (${userRole}) no tiene acceso a esta sección.`,
          details: requiredRoles?.length ? `Roles requeridos: ${requiredRoles.join(', ')}` : undefined,
          action: 'Volver al Dashboard',
          actionPath: '/dashboard'
        }
      
      case 'insufficient-permissions':
        return {
          icon: AlertTriangle,
          title: 'Sin Autorización',
          message: 'No tienes los permisos necesarios para acceder a esta página.',
          details: requiredPermissions?.length ? `Permisos requeridos: ${requiredPermissions.join(', ')}` : undefined,
          action: 'Volver al Dashboard',
          actionPath: '/dashboard'
        }
      
      default:
        return {
          icon: AlertTriangle,
          title: 'Acceso Denegado',
          message: 'No tienes autorización para acceder a esta página.',
          action: 'Volver al Dashboard',
          actionPath: '/dashboard'
        }
    }
  }

  const content = getContent()
  const IconComponent = content.icon

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full text-center">
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Icono */}
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
            <IconComponent className="h-8 w-8 text-red-600" />
          </div>
          
          {/* Título */}
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            {content.title}
          </h1>
          
          {/* Mensaje principal */}
          <p className="text-gray-600 mb-4">
            {content.message}
          </p>
          
          {/* Detalles adicionales */}
          {content.details && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-700">
                {content.details}
              </p>
            </div>
          )}
          
          {/* Acciones */}
          <div className="space-y-3">
            <a
              href={content.actionPath}
              className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              {content.action}
            </a>
            
            <button
              onClick={() => window.history.back()}
              className="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Volver Atrás
            </button>
          </div>
        </div>
        
        {/* Footer */}
        <p className="mt-6 text-sm text-gray-500">
          Si crees que esto es un error, contacta al administrador del sistema.
        </p>
      </div>
    </div>
  )
}

// ===========================================
// COMPONENTE PRINCIPAL
// ===========================================

export default function ProtectedRoute({
  children,
  requiredRoles = [],
  requiredPermissions = [],
  requireAllPermissions = false,
  fallbackPath = '/login',
  showUnauthorized = true
}: ProtectedRouteProps) {
  const { usuario, isLoading, isAuthenticated, hasPermission, hasRole, checkPermissions } = useAuth()
  const [permissionsChecked, setPermissionsChecked] = useState(false)
  const [hasRequiredPermissions, setHasRequiredPermissions] = useState(false)
  const location = useLocation()

  // ===========================================
  // VERIFICACIÓN DE PERMISOS ASÍNCRONA
  // ===========================================

  useEffect(() => {
    async function verifyPermissions() {
      if (!isAuthenticated || !usuario || requiredPermissions.length === 0) {
        setPermissionsChecked(true)
        setHasRequiredPermissions(requiredPermissions.length === 0)
        return
      }

      try {
        const permissionsResult = await checkPermissions(requiredPermissions)
        
        if (requireAllPermissions) {
          // Debe tener TODOS los permisos
          setHasRequiredPermissions(
            requiredPermissions.every(permission => permissionsResult[permission])
          )
        } else {
          // Debe tener AL MENOS UNO de los permisos
          setHasRequiredPermissions(
            requiredPermissions.some(permission => permissionsResult[permission])
          )
        }
      } catch (error) {
        console.error('Error verificando permisos:', error)
        setHasRequiredPermissions(false)
      } finally {
        setPermissionsChecked(true)
      }
    }

    verifyPermissions()
  }, [isAuthenticated, usuario, requiredPermissions, requireAllPermissions, checkPermissions])

  // ===========================================
  // LOADING STATE
  // ===========================================

  if (isLoading || (requiredPermissions.length > 0 && !permissionsChecked)) {
    return <LoadingScreen />
  }

  // ===========================================
  // VERIFICACIONES DE ACCESO
  // ===========================================

  // 1. Verificar autenticación
  if (!isAuthenticated || !usuario) {
    if (showUnauthorized) {
      return <UnauthorizedAccess type="not-authenticated" />
    }
    return <Navigate to={fallbackPath} state={{ from: location }} replace />
  }

  // 2. Verificar roles requeridos
  if (requiredRoles.length > 0 && !hasRole(requiredRoles)) {
    if (showUnauthorized) {
      return (
        <UnauthorizedAccess 
          type="insufficient-role" 
          requiredRoles={requiredRoles}
          userRole={usuario.rol}
        />
      )
    }
    return <Navigate to="/dashboard" replace />
  }

  // 3. Verificar permisos requeridos
  if (requiredPermissions.length > 0 && !hasRequiredPermissions) {
    if (showUnauthorized) {
      return (
        <UnauthorizedAccess 
          type="insufficient-permissions" 
          requiredPermissions={requiredPermissions}
          userRole={usuario.rol}
        />
      )
    }
    return <Navigate to="/dashboard" replace />
  }

  // ===========================================
  // ACCESO AUTORIZADO
  // ===========================================

  return <>{children}</>
}

// ===========================================
// HOOKS ADICIONALES
// ===========================================

/**
 * Hook para verificar acceso a una ruta específica
 */
export function useRouteAccess(
  requiredRoles: UsuarioRol[] = [],
  requiredPermissions: string[] = [],
  requireAllPermissions: boolean = false
) {
  const { usuario, isAuthenticated, hasRole, hasPermission } = useAuth()
  const [canAccess, setCanAccess] = useState(false)
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    setIsChecking(true)

    // Verificar autenticación
    if (!isAuthenticated || !usuario) {
      setCanAccess(false)
      setIsChecking(false)
      return
    }

    // Verificar roles
    if (requiredRoles.length > 0 && !hasRole(requiredRoles)) {
      setCanAccess(false)
      setIsChecking(false)
      return
    }

    // Verificar permisos
    if (requiredPermissions.length > 0) {
      if (requireAllPermissions) {
        // Debe tener TODOS los permisos
        const hasAll = requiredPermissions.every(permission => hasPermission(permission))
        setCanAccess(hasAll)
      } else {
        // Debe tener AL MENOS UNO de los permisos
        const hasAny = requiredPermissions.some(permission => hasPermission(permission))
        setCanAccess(hasAny)
      }
    } else {
      setCanAccess(true)
    }

    setIsChecking(false)
  }, [isAuthenticated, usuario, requiredRoles, requiredPermissions, requireAllPermissions, hasRole, hasPermission])

  return { canAccess, isChecking }
}

// ===========================================
// COMPONENTES ESPECÍFICOS
// ===========================================

/**
 * Ruta protegida solo para administradores
 */
export function AdminRoute({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute requiredRoles={['administrador']}>
      {children}
    </ProtectedRoute>
  )
}

/**
 * Ruta protegida para administradores y contadores
 */
export function AdminOrAccountantRoute({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute requiredRoles={['administrador', 'contador']}>
      {children}
    </ProtectedRoute>
  )
}

/**
 * Ruta protegida para roles operativos (excluye clientes)
 */
export function OperationalRoute({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute requiredRoles={['administrador', 'contador', 'vendedor', 'supervisor']}>
      {children}
    </ProtectedRoute>
  )
}

/**
 * Ruta protegida por permisos específicos
 */
export function PermissionRoute({ 
  children, 
  permissions, 
  requireAll = false 
}: { 
  children: React.ReactNode
  permissions: string[]
  requireAll?: boolean 
}) {
  return (
    <ProtectedRoute 
      requiredPermissions={permissions} 
      requireAllPermissions={requireAll}
    >
      {children}
    </ProtectedRoute>
  )
}

// ===========================================
// EXPORTACIONES
// ===========================================

export { 
  ProtectedRoute, 
  AdminRoute, 
  AdminOrAccountantRoute, 
  OperationalRoute, 
  PermissionRoute,
  useRouteAccess 
}