/**
 * MAIN.TSX - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Entry point de la aplicación React
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'react-hot-toast'

import App from './App.tsx'
import './index.css'

// =============================================================================
// CONFIGURACIÓN DE REACT QUERY
// =============================================================================
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Tiempo de stale: 5 minutos
      staleTime: 5 * 60 * 1000,
      // Tiempo de cache: 10 minutos
      cacheTime: 10 * 60 * 1000,
      // Reintentos en caso de error
      retry: 3,
      // Intervalo de reintento
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      // Refetch en window focus
      refetchOnWindowFocus: false,
      // Refetch en reconexión
      refetchOnReconnect: true,
    },
    mutations: {
      // Reintentos para mutaciones
      retry: 1,
      // Tiempo de reintento
      retryDelay: 1000,
    },
  },
})

// =============================================================================
// CONFIGURACIÓN DE TOAST
// =============================================================================
const toasterConfig = {
  duration: 4000,
  position: 'top-right' as const,
  reverseOrder: false,
  gutter: 8,
  containerClassName: '',
  containerStyle: {
    top: 20,
    left: 20,
    bottom: 20,
    right: 20,
  },
  toastOptions: {
    className: '',
    duration: 4000,
    style: {
      background: '#ffffff',
      color: '#374151',
      border: '1px solid #d1d5db',
      borderRadius: '0.5rem',
      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      fontSize: '14px',
      fontWeight: '500',
      padding: '12px 16px',
      maxWidth: '400px',
    },
    success: {
      duration: 3000,
      style: {
        background: '#f0fdf4',
        color: '#166534',
        border: '1px solid #bbf7d0',
      },
      iconTheme: {
        primary: '#22c55e',
        secondary: '#f0fdf4',
      },
    },
    error: {
      duration: 5000,
      style: {
        background: '#fef2f2',
        color: '#991b1b',
        border: '1px solid #fecaca',
      },
      iconTheme: {
        primary: '#ef4444',
        secondary: '#fef2f2',
      },
    },
    loading: {
      style: {
        background: '#f8fafc',
        color: '#475569',
        border: '1px solid #e2e8f0',
      },
      iconTheme: {
        primary: '#0ea5e9',
        secondary: '#f8fafc',
      },
    },
  },
}

// =============================================================================
// CONFIGURACIÓN DE DESARROLLO
// =============================================================================
const isDevelopment = import.meta.env.DEV
const isProduction = import.meta.env.PROD

// Logging en desarrollo
if (isDevelopment) {
  console.log('🚀 FELICITA Frontend iniciando en modo desarrollo')
  console.log('📊 React Query DevTools habilitado')
  console.log('🔄 Hot Module Replacement activo')
}

// =============================================================================
// MANEJO DE ERRORES GLOBALES
// =============================================================================
window.addEventListener('error', (event) => {
  console.error('Error global capturado:', event.error)
  
  if (isDevelopment) {
    console.error('Stack trace:', event.error.stack)
  }
  
  // En producción, reportar errores a servicio de monitoreo
  if (isProduction) {
    // TODO: Integrar con servicio de monitoreo (Sentry, LogRocket, etc.)
    console.error('Error en producción:', event.error)
  }
})

// Manejo de promesas rechazadas no capturadas
window.addEventListener('unhandledrejection', (event) => {
  console.error('Promesa rechazada no capturada:', event.reason)
  
  if (isProduction) {
    // TODO: Reportar a servicio de monitoreo
    console.error('Promise rejection en producción:', event.reason)
  }
})

// =============================================================================
// VERIFICACIONES DE COMPATIBILIDAD
// =============================================================================
const verificarCompatibilidad = () => {
  const features = {
    fetch: typeof fetch !== 'undefined',
    localStorage: typeof Storage !== 'undefined',
    sessionStorage: typeof sessionStorage !== 'undefined',
    webWorkers: typeof Worker !== 'undefined',
    notifications: 'Notification' in window,
    serviceWorker: 'serviceWorker' in navigator,
  }
  
  const incompatibleFeatures = Object.entries(features)
    .filter(([_, supported]) => !supported)
    .map(([feature]) => feature)
  
  if (incompatibleFeatures.length > 0) {
    console.warn('⚠️ Características no compatibles:', incompatibleFeatures)
    
    // Mostrar mensaje de compatibilidad si hay problemas críticos
    if (!features.fetch || !features.localStorage) {
      alert(
        'Su navegador no es compatible con todas las características necesarias. ' +
        'Por favor, actualice su navegador para una mejor experiencia.'
      )
    }
  }
  
  return features
}

// =============================================================================
// INFORMACIÓN DEL SISTEMA
// =============================================================================
const mostrarInfoSistema = () => {
  if (isDevelopment) {
    console.group('📋 Información del Sistema FELICITA')
    console.log('🏢 Empresa:', 'FELICITA - Sistema de Facturación Electrónica')
    console.log('🇵🇪 País:', 'Perú')
    console.log('⚛️ React:', React.version)
    console.log('🔧 Vite:', import.meta.env.VITE_VERSION || 'N/A')
    console.log('🌐 Modo:', isDevelopment ? 'Desarrollo' : 'Producción')
    console.log('📱 User Agent:', navigator.userAgent)
    console.log('🌍 Idioma:', navigator.language)
    console.log('⏰ Zona Horaria:', Intl.DateTimeFormat().resolvedOptions().timeZone)
    console.groupEnd()
  }
}

// =============================================================================
// CONFIGURACIÓN DE METADATOS
// =============================================================================
const configurarMetadatos = () => {
  // Configurar título de la página
  document.title = 'FELICITA - Sistema de Facturación Electrónica'
  
  // Configurar meta tags
  const metaTags = {
    'description': 'Sistema de Facturación Electrónica para empresas peruanas',
    'keywords': 'facturación electrónica, Perú, SUNAT, facturas, boletas',
    'author': 'FELICITA Development Team',
    'viewport': 'width=device-width, initial-scale=1.0',
    'theme-color': '#1f2937',
  }
  
  Object.entries(metaTags).forEach(([name, content]) => {
    let meta = document.querySelector(`meta[name="${name}"]`)
    if (!meta) {
      meta = document.createElement('meta')
      meta.setAttribute('name', name)
      document.head.appendChild(meta)
    }
    meta.setAttribute('content', content)
  })
  
  // Configurar favicon
  const favicon = document.querySelector('link[rel="icon"]')
  if (!favicon) {
    const link = document.createElement('link')
    link.rel = 'icon'
    link.href = '/favicon.ico'
    document.head.appendChild(link)
  }
}

// =============================================================================
// INICIALIZACIÓN
// =============================================================================
const inicializar = () => {
  // Verificar compatibilidad del navegador
  verificarCompatibilidad()
  
  // Mostrar información del sistema en desarrollo
  mostrarInfoSistema()
  
  // Configurar metadatos
  configurarMetadatos()
  
  // Limpiar consola en producción
  if (isProduction) {
    console.clear()
    console.log(
      '%cFELICITA%c Sistema de Facturación Electrónica',
      'color: #1f2937; font-size: 24px; font-weight: bold;',
      'color: #6b7280; font-size: 16px;'
    )
  }
}

// =============================================================================
// RENDERIZADO DE LA APLICACIÓN
// =============================================================================
const renderizarApp = () => {
  const rootElement = document.getElementById('root')
  
  if (!rootElement) {
    throw new Error('No se encontró el elemento root')
  }
  
  const root = ReactDOM.createRoot(rootElement)
  
  root.render(
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
          <Toaster {...toasterConfig} />
        </BrowserRouter>
        
        {/* React Query DevTools solo en desarrollo */}
        {isDevelopment && (
          <ReactQueryDevtools
            initialIsOpen={false}
            position="bottom-right"
            toggleButtonProps={{
              style: {
                marginLeft: '5px',
                transform: 'scale(0.8)',
                transformOrigin: 'bottom right',
              },
            }}
          />
        )}
      </QueryClientProvider>
    </React.StrictMode>
  )
  
  // Log de inicialización exitosa
  if (isDevelopment) {
    console.log('✅ Aplicación FELICITA renderizada correctamente')
  }
}

// =============================================================================
// PUNTO DE ENTRADA PRINCIPAL
// =============================================================================
try {
  // Inicializar configuraciones
  inicializar()
  
  // Renderizar aplicación
  renderizarApp()
  
} catch (error) {
  console.error('❌ Error fatal al inicializar FELICITA:', error)
  
  // Mostrar mensaje de error básico
  document.body.innerHTML = `
    <div style="
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      font-family: system-ui, -apple-system, sans-serif;
      background-color: #f9fafb;
      color: #374151;
      text-align: center;
      padding: 20px;
    ">
      <div>
        <h1 style="color: #dc2626; margin-bottom: 16px;">Error al cargar FELICITA</h1>
        <p style="margin-bottom: 16px;">Ha ocurrido un error al inicializar la aplicación.</p>
        <p style="font-size: 14px; color: #6b7280;">
          Por favor, recargue la página o contacte al soporte técnico.
        </p>
        <button 
          onclick="window.location.reload()"
          style="
            margin-top: 20px;
            padding: 8px 16px;
            background-color: #1f2937;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
          "
        >
          Recargar Página
        </button>
      </div>
    </div>
  `
}

// =============================================================================
// EXPORTACIONES PARA TESTING
// =============================================================================
if (isDevelopment) {
  // Exponer queryClient globalmente para testing
  ;(window as any).queryClient = queryClient
  ;(window as any).React = React
  
  console.log('🧪 Variables de testing expuestas en window')
}