/**
 * COMPONENTE HEADER - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Barra de navegación superior con usuario, notificaciones y menú
 */

import React, { useState, useRef, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { 
  User, 
  Bell, 
  Settings, 
  LogOut, 
  Menu, 
  Search,
  ChevronDown,
  Sun,
  Moon,
  Monitor,
  HelpCircle,
  RefreshCcw
} from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { useUserPreferences } from '../../hooks/useLocalStorage'
import { Button } from '../ui/button'
import { Card } from '../ui/card'
import { SearchInput } from '../ui/input'
import { cn } from '../../utils/helpers'
import { formatearFecha } from '../../utils/helpers'

// =============================================================================
// INTERFACES
// =============================================================================

export interface HeaderProps {
  onMenuToggle?: () => void
  showMenuButton?: boolean
  className?: string
}

interface NotificationItem {
  id: string
  tipo: 'info' | 'warning' | 'error' | 'success'
  titulo: string
  mensaje: string
  fecha: Date
  leida: boolean
  accion?: () => void
}

// =============================================================================
// COMPONENTE PRINCIPAL
// =============================================================================

const Header: React.FC<HeaderProps> = ({
  onMenuToggle,
  showMenuButton = true,
  className
}) => {
  const { 
    usuario, 
    nombreCompleto, 
    iniciales, 
    empresa, 
    logout, 
    esAdministrador,
    esContador 
  } = useAuth()
  
  const [preferences, setPreferences] = useUserPreferences()
  const navigate = useNavigate()
  const location = useLocation()
  
  // Estados locales
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showSearch, setShowSearch] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [notificaciones, setNotificaciones] = useState<NotificationItem[]>([])
  
  // Referencias para dropdowns
  const userMenuRef = useRef<HTMLDivElement>(null)
  const notificationsRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLDivElement>(null)

  // =============================================================================
  // EFECTOS
  // =============================================================================

  // Cerrar dropdowns al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false)
      }
      if (notificationsRef.current && !notificationsRef.current.contains(event.target as Node)) {
        setShowNotifications(false)
      }
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearch(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Simulación de notificaciones (en producción vendrían de API)
  useEffect(() => {
    const mockNotifications: NotificationItem[] = [
      {
        id: '1',
        tipo: 'success',
        titulo: 'Factura enviada a SUNAT',
        mensaje: 'La factura F001-00000123 fue aceptada por SUNAT',
        fecha: new Date(),
        leida: false
      },
      {
        id: '2',
        tipo: 'warning',
        titulo: 'Stock bajo',
        mensaje: 'El producto "Laptop HP" tiene stock bajo (3 unidades)',
        fecha: new Date(Date.now() - 30 * 60 * 1000),
        leida: false
      },
      {
        id: '3',
        tipo: 'info',
        titulo: 'Cliente agregado',
        mensaje: 'Se agregó un nuevo cliente: "Empresa ABC SAC"',
        fecha: new Date(Date.now() - 60 * 60 * 1000),
        leida: true
      }
    ]
    setNotificaciones(mockNotifications)
  }, [])

  // =============================================================================
  // FUNCIONES
  // =============================================================================

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/login')
    } catch (error) {
      console.error('Error al cerrar sesión:', error)
    }
  }

  const handleThemeChange = (theme: 'light' | 'dark' | 'system') => {
    setPreferences(prev => ({ ...prev, theme }))
  }

  const handleSearch = (query: string) => {
    if (query.trim()) {
      navigate(`/buscar?q=${encodeURIComponent(query)}`)
      setShowSearch(false)
      setSearchQuery('')
    }
  }

  const markNotificationAsRead = (id: string) => {
    setNotificaciones(prev => 
      prev.map(notif => 
        notif.id === id ? { ...notif, leida: true } : notif
      )
    )
  }

  const unreadCount = notificaciones.filter(n => !n.leida).length

  // =============================================================================
  // COMPONENTES INTERNOS
  // =============================================================================

  const UserMenu = () => (
    <div 
      ref={userMenuRef}
      className="absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
    >
      {/* Información del usuario */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
            {iniciales}
          </div>
          <div className="flex-1">
            <div className="font-semibold text-gray-900">{nombreCompleto}</div>
            <div className="text-sm text-gray-600">{usuario?.email}</div>
            <div className="text-xs text-gray-500">{empresa}</div>
          </div>
        </div>
      </div>

      {/* Opciones del menú */}
      <div className="py-2">
        <button
          onClick={() => {
            navigate('/perfil')
            setShowUserMenu(false)
          }}
          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-3"
        >
          <User className="w-4 h-4" />
          <span>Mi Perfil</span>
        </button>

        {(esAdministrador || esContador) && (
          <button
            onClick={() => {
              navigate('/configuracion')
              setShowUserMenu(false)
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-3"
          >
            <Settings className="w-4 h-4" />
            <span>Configuración</span>
          </button>
        )}

        <div className="px-4 py-2">
          <div className="text-xs text-gray-500 mb-2">Tema</div>
          <div className="flex space-x-1">
            <button
              onClick={() => handleThemeChange('light')}
              className={cn(
                'p-2 rounded text-xs',
                preferences.theme === 'light' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
              )}
            >
              <Sun className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleThemeChange('dark')}
              className={cn(
                'p-2 rounded text-xs',
                preferences.theme === 'dark' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
              )}
            >
              <Moon className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleThemeChange('system')}
              className={cn(
                'p-2 rounded text-xs',
                preferences.theme === 'system' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
              )}
            >
              <Monitor className="w-4 h-4" />
            </button>
          </div>
        </div>

        <button
          onClick={() => {
            navigate('/ayuda')
            setShowUserMenu(false)
          }}
          className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-3"
        >
          <HelpCircle className="w-4 h-4" />
          <span>Ayuda</span>
        </button>
      </div>

      {/* Cerrar sesión */}
      <div className="border-t border-gray-100 py-2">
        <button
          onClick={handleLogout}
          className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-3"
        >
          <LogOut className="w-4 h-4" />
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </div>
  )

  const NotificationsMenu = () => (
    <div 
      ref={notificationsRef}
      className="absolute right-0 top-full mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-hidden"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100 flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Notificaciones</h3>
        {unreadCount > 0 && (
          <button 
            onClick={() => setNotificaciones(prev => prev.map(n => ({ ...n, leida: true })))}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            Marcar todas como leídas
          </button>
        )}
      </div>

      {/* Lista de notificaciones */}
      <div className="max-h-80 overflow-y-auto">
        {notificaciones.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Bell className="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p>No hay notificaciones</p>
          </div>
        ) : (
          notificaciones.map((notificacion) => (
            <div
              key={notificacion.id}
              className={cn(
                'p-4 border-b border-gray-50 hover:bg-gray-50 cursor-pointer',
                !notificacion.leida && 'bg-blue-50'
              )}
              onClick={() => {
                markNotificationAsRead(notificacion.id)
                notificacion.accion?.()
              }}
            >
              <div className="flex items-start space-x-3">
                <div className={cn(
                  'w-2 h-2 rounded-full mt-2',
                  {
                    'bg-blue-500': notificacion.tipo === 'info',
                    'bg-green-500': notificacion.tipo === 'success',
                    'bg-yellow-500': notificacion.tipo === 'warning',
                    'bg-red-500': notificacion.tipo === 'error'
                  }
                )} />
                <div className="flex-1">
                  <div className="font-medium text-sm text-gray-900">
                    {notificacion.titulo}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {notificacion.mensaje}
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    {formatearFecha(notificacion.fecha)}
                  </div>
                </div>
                {!notificacion.leida && (
                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-100">
        <button
          onClick={() => {
            navigate('/notificaciones')
            setShowNotifications(false)
          }}
          className="w-full text-center text-sm text-blue-600 hover:text-blue-800"
        >
          Ver todas las notificaciones
        </button>
      </div>
    </div>
  )

  const SearchBar = () => (
    <div 
      ref={searchRef}
      className={cn(
        'absolute left-1/2 transform -translate-x-1/2 top-full mt-2 w-96 z-50 transition-all duration-200',
        showSearch ? 'opacity-100 visible' : 'opacity-0 invisible'
      )}
    >
      <Card className="p-4">
        <SearchInput
          placeholder="Buscar productos, clientes, facturas..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onSearch={handleSearch}
          onClear={() => setSearchQuery('')}
          className="w-full"
          autoFocus
        />
        <div className="mt-2 text-xs text-gray-500">
          Presiona Enter para buscar o Esc para cancelar
        </div>
      </Card>
    </div>
  )

  // =============================================================================
  // RENDER
  // =============================================================================

  return (
    <header className={cn(
      'bg-white border-b border-gray-200 shadow-sm relative z-40',
      className
    )}>
      <div className="px-4 lg:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Lado izquierdo */}
          <div className="flex items-center space-x-4">
            {/* Botón menú móvil */}
            {showMenuButton && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onMenuToggle}
                className="lg:hidden"
              >
                <Menu className="w-5 h-5" />
              </Button>
            )}

            {/* Logo y título */}
            <Link to="/dashboard" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">F</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="font-bold text-xl text-gray-900">FELICITA</h1>
                <p className="text-xs text-gray-500">Facturación Electrónica</p>
              </div>
            </Link>
          </div>

          {/* Centro - Breadcrumb/Título de página */}
          <div className="hidden md:flex items-center space-x-2 text-sm text-gray-600">
            <span className="capitalize">
              {location.pathname.split('/')[1] || 'Dashboard'}
            </span>
            {location.pathname.split('/').length > 2 && (
              <>
                <span>/</span>
                <span className="capitalize">
                  {location.pathname.split('/')[2]}
                </span>
              </>
            )}
          </div>

          {/* Lado derecho */}
          <div className="flex items-center space-x-2">
            {/* Búsqueda */}
            <div className="relative">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowSearch(!showSearch)}
                className="hidden sm:flex"
              >
                <Search className="w-5 h-5" />
              </Button>
              <SearchBar />
            </div>

            {/* Refresh */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => window.location.reload()}
              className="hidden md:flex"
            >
              <RefreshCcw className="w-4 h-4" />
            </Button>

            {/* Notificaciones */}
            <div className="relative">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </Button>
              {showNotifications && <NotificationsMenu />}
            </div>

            {/* Usuario */}
            <div className="relative">
              <Button
                variant="ghost"
                className="flex items-center space-x-2 px-3"
                onClick={() => setShowUserMenu(!showUserMenu)}
              >
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  {iniciales}
                </div>
                <div className="hidden sm:block text-left">
                  <div className="text-sm font-medium text-gray-900">
                    {nombreCompleto}
                  </div>
                  <div className="text-xs text-gray-500">
                    {usuario?.email}
                  </div>
                </div>
                <ChevronDown className="w-4 h-4 text-gray-500" />
              </Button>
              {showUserMenu && <UserMenu />}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header