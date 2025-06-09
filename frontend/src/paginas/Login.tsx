/**
 * PÁGINA LOGIN - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Página de inicio de sesión con React Hook Form y validaciones
 */

import React, { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Link, Navigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../hooks/useAuth'
import { Button } from '../componentes/ui/button'
import { Input } from '../componentes/ui/input'
import { Card } from '../componentes/ui/card'
import LoadingSpinner from '../componentes/ui/LoadingSpinner'
import type { LoginCredentials } from '../types'

// =============================================================================
// TIPOS DEL COMPONENTE
// =============================================================================

/** Datos del formulario de login */
interface LoginFormData {
  email: string
  password: string
  recordarme: boolean
}

/** Props del componente Login */
interface LoginPageProps {
  // Props opcionales para personalización
  mostrarRegistro?: boolean
  mostrarRecordarPassword?: boolean
  redireccionarA?: string
}

// =============================================================================
// CONSTANTES
// =============================================================================

/** Credenciales de demostración para desarrollo */
const CREDENCIALES_DEMO = [
  {
    email: 'admin@felicita.pe',
    password: 'admin123',
    rol: 'Administrador',
    descripcion: 'Acceso completo al sistema'
  },
  {
    email: 'contador@felicita.pe',
    password: 'contador123',
    rol: 'Contador',
    descripcion: 'Facturación y reportes contables'
  },
  {
    email: 'vendedor@felicita.pe',
    password: 'vendedor123',
    rol: 'Vendedor',
    descripcion: 'Punto de venta e inventario'
  }
]

// =============================================================================
// COMPONENTE PRINCIPAL
// =============================================================================
const LoginPage: React.FC<LoginPageProps> = ({
  mostrarRegistro = false,
  mostrarRecordarPassword = true,
  redireccionarA
}) => {
  // Hooks de autenticación
  const { 
    login, 
    estaAutenticado, 
    cargandoAuth, 
    cargandoAccion, 
    error, 
    limpiarError 
  } = useAuth()

  // Estado local
  const [mostrarPassword, setMostrarPassword] = useState(false)
  const [mostrarCredencialesDemo, setMostrarCredencialesDemo] = useState(false)

  // React Hook Form
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    setValue,
    watch
  } = useForm<LoginFormData>({
    mode: 'onChange',
    defaultValues: {
      email: '',
      password: '',
      recordarme: false
    }
  })

  // =============================================================================
  // EFFECTS
  // =============================================================================

  /**
   * Limpiar errores cuando se monta el componente
   */
  useEffect(() => {
    limpiarError()
  }, [limpiarError])

  /**
   * Limpiar errores cuando el usuario empieza a escribir
   */
  useEffect(() => {
    const subscription = watch(() => {
      if (error) {
        limpiarError()
      }
    })
    
    return () => subscription.unsubscribe()
  }, [watch, error, limpiarError])

  // =============================================================================
  // HANDLERS
  // =============================================================================

  /**
   * Manejar envío del formulario
   */
  const onSubmit = async (data: LoginFormData): Promise<void> => {
    try {
      const credenciales: LoginCredentials = {
        email: data.email.trim().toLowerCase(),
        password: data.password
      }

      const exitoso = await login(credenciales, {
        ruta: redireccionarA,
        preservarHistorial: false
      })

      if (exitoso) {
        // Manejar "recordarme" si está habilitado
        if (data.recordarme) {
          localStorage.setItem('felicita_recordar_email', credenciales.email)
        } else {
          localStorage.removeItem('felicita_recordar_email')
        }
      }

    } catch (error) {
      console.error('Error en onSubmit:', error)
      toast.error('Error inesperado al iniciar sesión')
    }
  }

  /**
   * Usar credenciales de demostración
   */
  const usarCredencialesDemo = (credenciales: typeof CREDENCIALES_DEMO[0]): void => {
    setValue('email', credenciales.email)
    setValue('password', credenciales.password)
    setMostrarCredencialesDemo(false)
    toast.info(`Credenciales cargadas para ${credenciales.rol}`)
  }

  /**
   * Alternar visibilidad de contraseña
   */
  const toggleMostrarPassword = (): void => {
    setMostrarPassword(prev => !prev)
  }

  // =============================================================================
  // REDIRECCIÓN SI YA ESTÁ AUTENTICADO
  // =============================================================================
  if (estaAutenticado) {
    return <Navigate to={redireccionarA || '/dashboard'} replace />
  }

  // =============================================================================
  // RENDER
  // =============================================================================
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-blue-600 rounded-xl flex items-center justify-center mb-6">
            <span className="text-2xl font-bold text-white">F</span>
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Bienvenido a FELICITA
          </h1>
          
          <p className="text-gray-600">
            Sistema de Facturación Electrónica para Perú
          </p>
          
          {import.meta.env.DEV && (
            <p className="text-sm text-amber-600 mt-2 font-medium">
              🚧 Modo Desarrollo - SUNAT Demo
            </p>
          )}
        </div>

        {/* Formulario de Login */}
        <Card className="p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            
            {/* Campo Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Correo Electrónico
              </label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="usuario@empresa.com"
                error={errors.email?.message}
                {...register('email', {
                  required: 'El correo electrónico es requerido',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Formato de correo electrónico inválido'
                  }
                })}
                className={errors.email ? 'border-red-300' : ''}
              />
            </div>

            {/* Campo Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Contraseña
              </label>
              <div className="relative">
                <Input
                  id="password"
                  type={mostrarPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  placeholder="Ingresa tu contraseña"
                  error={errors.password?.message}
                  {...register('password', {
                    required: 'La contraseña es requerida',
                    minLength: {
                      value: 6,
                      message: 'La contraseña debe tener al menos 6 caracteres'
                    }
                  })}
                  className={`pr-10 ${errors.password ? 'border-red-300' : ''}`}
                />
                
                <button
                  type="button"
                  onClick={toggleMostrarPassword}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {mostrarPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Opciones adicionales */}
            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  {...register('recordarme')}
                />
                <span className="ml-2 block text-sm text-gray-700">
                  Recordar mi sesión
                </span>
              </label>

              {mostrarRecordarPassword && (
                <Link
                  to="/forgot-password"
                  className="text-sm text-blue-600 hover:text-blue-500 font-medium"
                >
                  ¿Olvidaste tu contraseña?
                </Link>
              )}
            </div>

            {/* Mensaje de error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Botón de envío */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              disabled={!isValid || cargandoAccion}
              loading={cargandoAccion}
            >
              {cargandoAccion ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </Button>

            {/* Enlace de registro */}
            {mostrarRegistro && (
              <div className="text-center">
                <p className="text-sm text-gray-600">
                  ¿No tienes una cuenta?{' '}
                  <Link
                    to="/register"
                    className="text-blue-600 hover:text-blue-500 font-medium"
                  >
                    Regístrate aquí
                  </Link>
                </p>
              </div>
            )}
          </form>
        </Card>

        {/* Credenciales de Demostración (Solo en desarrollo) */}
        {import.meta.env.DEV && (
          <Card className="p-6 bg-amber-50 border-amber-200">
            <div className="text-center mb-4">
              <h3 className="text-lg font-semibold text-amber-800 mb-2">
                🧪 Credenciales de Desarrollo
              </h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setMostrarCredencialesDemo(!mostrarCredencialesDemo)}
                className="text-amber-700 border-amber-300 hover:bg-amber-100"
              >
                {mostrarCredencialesDemo ? 'Ocultar' : 'Mostrar'} Credenciales Demo
              </Button>
            </div>

            {mostrarCredencialesDemo && (
              <div className="space-y-3">
                {CREDENCIALES_DEMO.map((cred, index) => (
                  <div
                    key={index}
                    className="bg-white border border-amber-200 rounded-lg p-3 cursor-pointer hover:bg-amber-25 transition-colors"
                    onClick={() => usarCredencialesDemo(cred)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-amber-800">{cred.rol}</p>
                        <p className="text-sm text-amber-600">{cred.email}</p>
                        <p className="text-xs text-amber-500">{cred.descripcion}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-amber-600 hover:text-amber-800"
                      >
                        Usar
                      </Button>
                    </div>
                  </div>
                ))}
                
                <p className="text-xs text-amber-600 text-center mt-4">
                  Click en cualquier credencial para cargarla automáticamente
                </p>
              </div>
            )}
          </Card>
        )}

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>
            © 2024 FELICITA - Sistema de Facturación Electrónica
          </p>
          <p className="mt-1">
            Cumple con normativas SUNAT del Perú
          </p>
        </div>

        {/* Loading overlay */}
        {cargandoAuth && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
              <LoadingSpinner size="md" />
              <span className="text-gray-700">Verificando sesión...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default LoginPage