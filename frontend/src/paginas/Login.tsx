/**
 * FELICITA - Componente Login
 * Sistema de Facturación Electrónica para Perú
 * 
 * Página de login completa con validaciones y diseño profesional
 */

import React, { useState, useEffect } from 'react'
import { Navigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'react-hot-toast'
import { Eye, EyeOff, LogIn, Shield, Building2, Users, BarChart3, Zap } from 'lucide-react'
import { useAuth } from '../contextos/AuthContext'
import type { LoginFormData } from '../types/auth'

// ===========================================
// VALIDACIÓN SCHEMA
// ===========================================

const loginSchema = z.object({
  username: z
    .string()
    .min(1, 'Usuario requerido')
    .max(150, 'Usuario muy largo'),
  password: z
    .string()
    .min(1, 'Contraseña requerida')
    .max(128, 'Contraseña muy larga'),
  remember_me: z.boolean().optional()
})

// ===========================================
// COMPONENTE PRINCIPAL
// ===========================================

export default function Login() {
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { login, isAuthenticated, isLoading } = useAuth()

  const {
    register,
    handleSubmit,
    formState: { errors },
    setFocus
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      remember_me: false
    }
  })

  // ===========================================
  // EFECTOS
  // ===========================================

  useEffect(() => {
    // Focus en el campo username al cargar
    setFocus('username')
  }, [setFocus])

  // Redirigir si ya está autenticado
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  // ===========================================
  // HANDLERS
  // ===========================================

  const onSubmit = async (data: LoginFormData) => {
    setIsSubmitting(true)
    
    try {
      await login({
        username: data.username,
        password: data.password
      })
      
      // El redirect se maneja automáticamente por el AuthProvider
    } catch (error) {
      // El error se maneja en el AuthProvider con toast
      console.error('Error en login:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  // ===========================================
  // RENDER LOADING
  // ===========================================

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="text-gray-600">Cargando...</p>
        </div>
      </div>
    )
  }

  // ===========================================
  // RENDER PRINCIPAL
  // ===========================================

  return (
    <div className="min-h-screen flex">
      {/* Panel Izquierdo - Información */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-indigo-700 text-white">
        <div className="flex flex-col justify-center px-12">
          {/* Logo y Título */}
          <div className="mb-12">
            <div className="flex items-center space-x-3 mb-6">
              <div className="bg-white rounded-xl p-3">
                <Building2 className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">FELICITA</h1>
                <p className="text-blue-100">Sistema de Facturación Electrónica</p>
              </div>
            </div>
            
            <h2 className="text-4xl font-bold mb-4">
              Gestiona tu negocio con confianza
            </h2>
            <p className="text-xl text-blue-100 leading-relaxed">
              Sistema completo de facturación electrónica que cumple con todos los 
              requisitos de SUNAT para empresas peruanas.
            </p>
          </div>

          {/* Características */}
          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <div className="bg-white/20 rounded-lg p-2">
                <Shield className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">100% Compatible con SUNAT</h3>
                <p className="text-blue-100">
                  Cumple con todas las normativas de facturación electrónica
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="bg-white/20 rounded-lg p-2">
                <Users className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Gestión de Usuarios</h3>
                <p className="text-blue-100">
                  Control de acceso por roles y permisos granulares
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="bg-white/20 rounded-lg p-2">
                <BarChart3 className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Reportes en Tiempo Real</h3>
                <p className="text-blue-100">
                  Análisis y reportes detallados de tu negocio
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="bg-white/20 rounded-lg p-2">
                <Zap className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Rápido y Eficiente</h3>
                <p className="text-blue-100">
                  Interfaz moderna y optimizada para tu productividad
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Panel Derecho - Formulario de Login */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md">
          {/* Header Mobile */}
          <div className="lg:hidden text-center mb-8">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="bg-blue-600 rounded-xl p-3">
                <Building2 className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">FELICITA</h1>
                <p className="text-gray-600">Facturación Electrónica</p>
              </div>
            </div>
          </div>

          {/* Título del Formulario */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Iniciar Sesión
            </h2>
            <p className="text-gray-600">
              Ingrese sus credenciales para acceder al sistema
            </p>
          </div>

          {/* Formulario */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Campo Usuario */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Usuario
              </label>
              <input
                {...register('username')}
                type="text"
                id="username"
                autoComplete="username"
                className={`
                  w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
                  transition-colors duration-200
                  ${errors.username ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}
                `}
                placeholder="Ingrese su usuario"
                disabled={isSubmitting}
              />
              {errors.username && (
                <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
              )}
            </div>

            {/* Campo Contraseña */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Contraseña
              </label>
              <div className="relative">
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  autoComplete="current-password"
                  className={`
                    w-full px-4 py-3 pr-12 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
                    transition-colors duration-200
                    ${errors.password ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'}
                  `}
                  placeholder="Ingrese su contraseña"
                  disabled={isSubmitting}
                />
                <button
                  type="button"
                  onClick={togglePasswordVisibility}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  disabled={isSubmitting}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            {/* Recordarme */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  {...register('remember_me')}
                  id="remember_me"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  disabled={isSubmitting}
                />
                <label htmlFor="remember_me" className="ml-2 text-sm text-gray-700">
                  Recordarme
                </label>
              </div>
              
              <Link
                to="/forgot-password"
                className="text-sm text-blue-600 hover:text-blue-500 transition-colors"
              >
                ¿Olvidaste tu contraseña?
              </Link>
            </div>

            {/* Botón Submit */}
            <button
              type="submit"
              disabled={isSubmitting}
              className={`
                w-full flex items-center justify-center px-4 py-3 border border-transparent 
                rounded-lg shadow-sm text-white font-medium transition-all duration-200
                ${isSubmitting 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                }
              `}
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Iniciando sesión...
                </>
              ) : (
                <>
                  <LogIn className="h-5 w-5 mr-2" />
                  Iniciar Sesión
                </>
              )}
            </button>
          </form>

          {/* Enlaces adicionales */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-600">
              ¿No tienes una cuenta?{' '}
              <Link
                to="/registro"
                className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
              >
                Regístrate aquí
              </Link>
            </p>
          </div>

          {/* Usuarios de demostración */}
          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Usuarios de demostración:</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <div>
                <strong>Admin:</strong> admin@felicita.com / admin123
              </div>
              <div>
                <strong>Contador:</strong> contador@felicita.com / contador123
              </div>
              <div>
                <strong>Vendedor:</strong> vendedor@felicita.com / vendedor123
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-8 text-center text-xs text-gray-500">
            <p>© 2024 FELICITA. Todos los derechos reservados.</p>
            <p className="mt-1">
              Sistema de Facturación Electrónica para Perú
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}