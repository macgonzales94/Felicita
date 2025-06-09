/**
 * APP.TSX - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Componente principal de la aplicación React
 */

import React, { Suspense, useEffect, useState } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { QueryErrorResetBoundary } from '@tanstack/react-query'
import { ErrorBoundary } from 'react-error-boundary'
import { Helmet } from 'react-helmet-async'

// Componentes de Loading y Error
import LoadingSpinner from './componentes/ui/LoadingSpinner'
import ErrorFallback from './componentes/ui/ErrorFallback'

// Lazy loading de páginas principales
const LoginPage = React.lazy(() => import('./paginas/auth/LoginPage'))
const DashboardPage = React.lazy(() => import('./paginas/dashboard/DashboardPage'))
const FacturacionPage = React.lazy(() => import('./paginas/facturacion/FacturacionPage'))
const InventarioPage = React.lazy(() => import('./paginas/inventario/InventarioPage'))
const ClientesPage = React.lazy(() => import('./paginas/clientes/ClientesPage'))
const ReportesPage = React.lazy(() => import('./paginas/reportes/ReportesPage'))
const ConfiguracionPage = React.lazy(() => import('./paginas/configuracion/ConfiguracionPage'))

// Hooks personalizados
import { useAuth } from './hooks/useAuth'
import { useTheme } from './hooks/useTheme'
import { useNetworkStatus } from './hooks/useNetworkStatus'

// Contextos
import { AuthProvider } from './contextos/AuthContext'
import { ThemeProvider } from './contextos/ThemeContext'
import { NotificationProvider } from './contextos/NotificationContext'

// Componentes de Layout
import MainLayout from './componentes/layout/MainLayout'
import AuthLayout from './componentes/layout/AuthLayout'

// Componentes de UI
import { NetworkStatusIndicator } from './componentes/ui/NetworkStatusIndicator'
import { NotificationCenter } from './componentes/ui/NotificationCenter'

// Tipos
interface AppProps {}

// =============================================================================
// COMPONENTE DE LOADING GLOBAL
// =============================================================================
const GlobalLoadingSpinner: React.FC = () => (
  <div className="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
    <div className="text-center">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-gray-600 font-medium">Cargando FELICITA...</p>
      <p className="mt-2 text-sm text-gray-500">Sistema de Facturación Electrónica</p>
    </div>
  </div>
)

// =============================================================================
// COMPONENTE DE ERROR GLOBAL
// =============================================================================
const GlobalErrorFallback: React.FC<{
  error: Error
  resetErrorBoundary: () => void
}> = ({ error, resetErrorBoundary }) => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div className="max-w-md w-full">
      <div className="bg-white rounded-lg shadow-lg p-6 text-center">
        <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center mb-4">
          <svg
            className="w-8 h-8 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
        </div>
        
        <h1 className="text-xl font-bold text-gray-900 mb-2">
          Error en FELICITA
        </h1>
        
        <p className="text-gray-600 mb-6">
          Ha ocurrido un error inesperado en la aplicación.
        </p>
        
        {import.meta.env.DEV && (
          <details className="mb-4 text-left">
            <summary className="cursor-pointer text-sm text-gray-500 mb-2">
              Detalles del error (modo desarrollo)
            </summary>
            <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto max-h-32">
              {error.message}
              {error.stack && '\n\n' + error.stack}
            </pre>
          </details>
        )}
        
        <div className="space-y-3">
          <button
            onClick={resetErrorBoundary}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
          >
            Intentar de nuevo
          </button>
          
          <button
            onClick={() => window.location.reload()}
            className="w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors"
          >
            Recargar página
          </button>
        </div>
      </div>
    </div>
  </div>
)

// =============================================================================
// COMPONENTE PROTECTOR DE RUTAS
// =============================================================================
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth()
  const location = useLocation()
  
  if (loading) {
    return <GlobalLoadingSpinner />
  }
  
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  
  return <>{children}</>
}

// =============================================================================
// COMPONENTE DE RUTAS PÚBLICAS
// =============================================================================
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <GlobalLoadingSpinner />
  }
  
  if (user) {
    return <Navigate to="/dashboard" replace />
  }
  
  return <>{children}</>
}

// =============================================================================
// COMPONENTE PRINCIPAL DE RUTAS
// =============================================================================
const AppRoutes: React.FC = () => {
  const location = useLocation()
  const isAuthRoute = location.pathname.startsWith('/login') || location.pathname.startsWith('/register')
  
  return (
    <Routes>
      {/* Rutas de Autenticación */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <AuthLayout>
              <Suspense fallback={<GlobalLoadingSpinner />}>
                <LoginPage />
              </Suspense>
            </AuthLayout>
          </PublicRoute>
        }
      />
      
      {/* Rutas Protegidas */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Suspense fallback={<LoadingSpinner />}>
                <DashboardPage />
              </Suspense>
            </MainLayout>
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/facturacion/*"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Suspense fallback={<LoadingSpinner />}>
                <FacturacionPage />
              </Suspense>
            </MainLayout>
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/inventario/*"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Suspense fallback={<LoadingSpinner />}>
                <InventarioPage />
              </Suspense>
            </MainLayout>
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/clientes/*"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Suspense fallback={<LoadingSpinner />}>
                <ClientesPage />
              </Suspense>
            </MainLayout>
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/reportes/*"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Suspense fallback={<LoadingSpinner />}>
                <ReportesPage />
              </Suspense>
            </MainLayout>
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/configuracion/*"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Suspense fallback={<LoadingSpinner />}>
                <ConfiguracionPage />
              </Suspense>
            </MainLayout>
          </ProtectedRoute>
        }
      />
      
      {/* Redirecciones */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

// =============================================================================
// COMPONENTE PRINCIPAL DE LA APP
// =============================================================================
const App: React.FC<AppProps> = () => {
  const [appReady, setAppReady] = useState(false)
  const [initError, setInitError] = useState<string | null>(null)
  
  // Inicialización de la aplicación
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Simular inicialización de servicios
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Verificar servicios críticos
        if (!window.localStorage) {
          throw new Error('LocalStorage no disponible')
        }
        
        setAppReady(true)
        
        if (import.meta.env.DEV) {
          console.log('✅ Aplicación FELICITA inicializada correctamente')
        }
        
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Error desconocido'
        setInitError(errorMessage)
        console.error('❌ Error al inicializar aplicación:', error)
      }
    }
    
    initializeApp()
  }, [])
  
  // Hook de estado de red
  const { isOnline, isSlowConnection } = useNetworkStatus()
  
  // Mostrar error de inicialización
  if (initError) {
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h1 className="text-xl font-bold text-red-600 mb-4">
              Error de Inicialización
            </h1>
            <p className="text-gray-700 mb-4">{initError}</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Recargar Aplicación
            </button>
          </div>
        </div>
      </div>
    )
  }
  
  // Mostrar loading inicial
  if (!appReady) {
    return <GlobalLoadingSpinner />
  }
  
  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          FallbackComponent={GlobalErrorFallback}
          onError={(error, errorInfo) => {
            console.error('Error capturado por ErrorBoundary:', error, errorInfo)
          }}
          onReset={reset}
        >
          <ThemeProvider>
            <AuthProvider>
              <NotificationProvider>
                <div className="app">
                  {/* Meta tags dinámicos */}
                  <Helmet>
                    <title>FELICITA - Sistema de Facturación Electrónica</title>
                    <meta name="description" content="Sistema de facturación electrónica para empresas peruanas" />
                  </Helmet>
                  
                  {/* Indicador de estado de red */}
                  <NetworkStatusIndicator 
                    isOnline={isOnline} 
                    isSlowConnection={isSlowConnection} 
                  />
                  
                  {/* Rutas principales */}
                  <Suspense fallback={<GlobalLoadingSpinner />}>
                    <AppRoutes />
                  </Suspense>
                  
                  {/* Centro de notificaciones */}
                  <NotificationCenter />
                  
                  {/* Debug info en desarrollo */}
                  {import.meta.env.DEV && (
                    <div className="fixed bottom-4 left-4 bg-black bg-opacity-75 text-white text-xs p-2 rounded z-50">
                      <div>Modo: {import.meta.env.MODE}</div>
                      <div>Red: {isOnline ? '🟢 Online' : '🔴 Offline'}</div>
                      {isSlowConnection && <div>⚠️ Conexión lenta</div>}
                    </div>
                  )}
                </div>
              </NotificationProvider>
            </AuthProvider>
          </ThemeProvider>
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  )
}

export default App