/**
 * UI COMPONENTS INDEX - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Exportación centralizada de todos los componentes UI
 */

// =============================================================================
// COMPONENTES BÁSICOS
// =============================================================================

// Loading Spinner
export { default as LoadingSpinner } from './LoadingSpinner'

// Buttons
export { default as Button } from './Button'
export { default as IconButton } from './IconButton'
export { default as ButtonGroup } from './ButtonGroup'

// Inputs
export { default as Input } from './Input'
export { default as TextArea } from './TextArea'
export { default as Select } from './Select'
export { default as Checkbox } from './Checkbox'
export { default as Radio } from './Radio'
export { default as Switch } from './Switch'
export { default as DatePicker } from './DatePicker'
export { default as FileUpload } from './FileUpload'

// Layout
export { default as Card } from './Card'
export { default as Modal } from './Modal'
export { default as Drawer } from './Drawer'
export { default as Tabs } from './Tabs'
export { default as Accordion } from './Accordion'
export { default as Divider } from './Divider'
export { default as Spacer } from './Spacer'

// Feedback
export { default as Alert } from './Alert'
export { default as Toast } from './Toast'
export { default as Notification } from './Notification'
export { default as Progress } from './Progress'
export { default as Skeleton } from './Skeleton'

// Data Display
export { default as Table } from './Table'
export { default as DataTable } from './DataTable'
export { default as Pagination } from './Pagination'
export { default as Avatar } from './Avatar'
export { default as Badge } from './Badge'
export { default as Chip } from './Chip'
export { default as Tooltip } from './Tooltip'
export { default as Popover } from './Popover'

// Navigation
export { default as Breadcrumb } from './Breadcrumb'
export { default as Menu } from './Menu'
export { default as Steps } from './Steps'

// Specialized
export { default as SearchBox } from './SearchBox'
export { default as FilterPanel } from './FilterPanel'
export { default as FormField } from './FormField'
export { default as ErrorBoundary } from './ErrorBoundary'
export { default as ErrorFallback } from './ErrorFallback'
export { default as NetworkStatusIndicator } from './NetworkStatusIndicator'
export { default as NotificationCenter } from './NotificationCenter'

// =============================================================================
// IMPLEMENTACIONES BÁSICAS DE COMPONENTES CRÍTICOS
// =============================================================================

// LoadingSpinner.tsx
import React from 'react'
import { cn } from '../../utils/cn'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  color?: 'primary' | 'secondary' | 'white'
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className = '',
  color = 'primary'
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  }
  
  const colorClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-600',
    white: 'text-white'
  }
  
  return (
    <div className={cn('animate-spin', sizeClasses[size], colorClasses[color], className)}>
      <svg
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  )
}

export { LoadingSpinner }

// ErrorFallback.tsx
interface ErrorFallbackProps {
  error: Error
  resetErrorBoundary: () => void
  className?: string
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetErrorBoundary,
  className = ''
}) => {
  return (
    <div className={cn('p-6 text-center', className)}>
      <div className="max-w-md mx-auto">
        <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
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
        
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Oops! Algo salió mal
        </h3>
        
        <p className="text-gray-600 mb-4">
          Ha ocurrido un error inesperado. Por favor, intenta de nuevo.
        </p>
        
        {import.meta.env.DEV && (
          <details className="mb-4 text-left">
            <summary className="cursor-pointer text-sm text-gray-500">
              Detalles del error
            </summary>
            <pre className="mt-2 text-xs bg-gray-100 p-3 rounded overflow-auto">
              {error.message}
            </pre>
          </details>
        )}
        
        <button
          onClick={resetErrorBoundary}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
        >
          Intentar de nuevo
        </button>
      </div>
    </div>
  )
}

export { ErrorFallback }

// NetworkStatusIndicator.tsx
interface NetworkStatusIndicatorProps {
  isOnline: boolean
  isSlowConnection?: boolean
}

const NetworkStatusIndicator: React.FC<NetworkStatusIndicatorProps> = ({
  isOnline,
  isSlowConnection = false
}) => {
  if (isOnline && !isSlowConnection) {
    return null // No mostrar nada si todo está bien
  }
  
  return (
    <div className={cn(
      'fixed top-0 left-0 right-0 z-50 p-2 text-center text-sm font-medium',
      !isOnline ? 'bg-red-600 text-white' : 'bg-yellow-600 text-white'
    )}>
      {!isOnline ? (
        <>
          <span className="inline-block w-2 h-2 bg-white rounded-full mr-2"></span>
          Sin conexión a internet
        </>
      ) : (
        <>
          <span className="inline-block w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></span>
          Conexión lenta detectada
        </>
      )}
    </div>
  )
}

export { NetworkStatusIndicator }

// NotificationCenter.tsx
const NotificationCenter: React.FC = () => {
  // Este es un placeholder - en la implementación real se integraría
  // con el sistema de notificaciones global
  return null
}

export { NotificationCenter }

// Button.tsx - Implementación básica
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  icon?: React.ReactNode
  children: React.ReactNode
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2'
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-blue-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500'
  }
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }
  
  const isDisabled = disabled || loading
  
  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        isDisabled && 'opacity-50 cursor-not-allowed',
        className
      )}
      disabled={isDisabled}
      {...props}
    >
      {loading && <LoadingSpinner size="sm" className="mr-2" color="white" />}
      {!loading && icon && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  )
}

export { Button }

// Input.tsx - Implementación básica
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helper?: string
  startIcon?: React.ReactNode
  endIcon?: React.ReactNode
}

const Input: React.FC<InputProps> = ({
  label,
  error,
  helper,
  startIcon,
  endIcon,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      
      <div className="relative">
        {startIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {startIcon}
          </div>
        )}
        
        <input
          className={cn(
            'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm',
            'focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
            'disabled:bg-gray-50 disabled:text-gray-500',
            error && 'border-red-300 focus:border-red-500 focus:ring-red-500',
            startIcon && 'pl-10',
            endIcon && 'pr-10',
            className
          )}
          {...props}
        />
        
        {endIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            {endIcon}
          </div>
        )}
      </div>
      
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
      
      {helper && !error && (
        <p className="mt-1 text-sm text-gray-500">{helper}</p>
      )}
    </div>
  )
}

export { Input }

// Card.tsx - Implementación básica
interface CardProps {
  children: React.ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
  shadow?: 'none' | 'sm' | 'md' | 'lg'
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  padding = 'md',
  shadow = 'md'
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-6',
    lg: 'p-8'
  }
  
  const shadowClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg'
  }
  
  return (
    <div className={cn(
      'bg-white rounded-lg border border-gray-200',
      paddingClasses[padding],
      shadowClasses[shadow],
      className
    )}>
      {children}
    </div>
  )
}

export { Card }

// =============================================================================
// UTILITY FUNCTION
// =============================================================================

// utils/cn.ts - Utility para combinar clases CSS
const cn = (...classes: (string | undefined | null | false)[]): string => {
  return classes.filter(Boolean).join(' ')
}

export { cn }

// =============================================================================
// EXPORTACIÓN POR DEFECTO
// =============================================================================

const UIComponents = {
  LoadingSpinner,
  ErrorFallback,
  NetworkStatusIndicator,
  NotificationCenter,
  Button,
  Input,
  Card,
  cn
}

export default UIComponents