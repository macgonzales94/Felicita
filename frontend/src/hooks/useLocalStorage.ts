/**
 * COMPONENTE CARGANDO - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Componentes de loading states para diferentes contextos
 */

import React from 'react'
import { cn } from '../../utils/helpers'

// =============================================================================
// INTERFACES
// =============================================================================

export interface CargandoProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'spinner' | 'dots' | 'pulse' | 'skeleton' | 'bars'
  color?: 'primary' | 'secondary' | 'white' | 'gray'
  fullScreen?: boolean
  overlay?: boolean
  message?: string
  className?: string
}

export interface SkeletonProps {
  width?: string | number
  height?: string | number
  className?: string
  animate?: boolean
}

export interface LoadingOverlayProps {
  visible: boolean
  message?: string
  transparent?: boolean
  className?: string
  children?: React.ReactNode
}

// =============================================================================
// COMPONENTE SPINNER PRINCIPAL
// =============================================================================

const Cargando: React.FC<CargandoProps> = ({
  size = 'md',
  variant = 'spinner',
  color = 'primary',
  fullScreen = false,
  overlay = false,
  message,
  className
}) => {
  
  // Tamaños para diferentes variantes
  const sizeClasses = {
    xs: {
      spinner: 'w-3 h-3',
      dots: 'w-1 h-1',
      bars: 'w-6 h-3'
    },
    sm: {
      spinner: 'w-4 h-4', 
      dots: 'w-1.5 h-1.5',
      bars: 'w-8 h-4'
    },
    md: {
      spinner: 'w-6 h-6',
      dots: 'w-2 h-2', 
      bars: 'w-10 h-5'
    },
    lg: {
      spinner: 'w-8 h-8',
      dots: 'w-3 h-3',
      bars: 'w-12 h-6'
    },
    xl: {
      spinner: 'w-12 h-12',
      dots: 'w-4 h-4',
      bars: 'w-16 h-8'
    }
  }
  
  // Colores
  const colorClasses = {
    primary: 'text-blue-600',
    secondary: 'text-gray-600', 
    white: 'text-white',
    gray: 'text-gray-400'
  }
  
  // Contenedor base
  const containerClasses = cn(
    'flex items-center justify-center',
    fullScreen && 'fixed inset-0 z-50',
    overlay && 'absolute inset-0 bg-white/80 backdrop-blur-sm',
    className
  )
  
  // Renderizar diferentes variantes
  const renderLoader = () => {
    switch (variant) {
      case 'spinner':
        return <SpinnerLoader size={sizeClasses[size].spinner} color={colorClasses[color]} />
      case 'dots':
        return <DotsLoader size={sizeClasses[size].dots} color={colorClasses[color]} />
      case 'pulse':
        return <PulseLoader size={sizeClasses[size].spinner} color={colorClasses[color]} />
      case 'bars':
        return <BarsLoader size={sizeClasses[size].bars} color={colorClasses[color]} />
      case 'skeleton':
        return <SkeletonLoader />
      default:
        return <SpinnerLoader size={sizeClasses[size].spinner} color={colorClasses[color]} />
    }
  }

  return (
    <div className={containerClasses}>
      <div className="flex flex-col items-center gap-3">
        {renderLoader()}
        {message && (
          <p className={cn('text-sm font-medium', colorClasses[color])}>
            {message}
          </p>
        )}
      </div>
    </div>
  )
}

// =============================================================================
// SPINNER ROTATORIO
// =============================================================================

const SpinnerLoader: React.FC<{ size: string; color: string }> = ({ size, color }) => (
  <svg
    className={cn('animate-spin', size, color)}
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
)

// =============================================================================
// LOADER DE PUNTOS
// =============================================================================

const DotsLoader: React.FC<{ size: string; color: string }> = ({ size, color }) => (
  <div className="flex space-x-1">
    {[0, 1, 2].map((i) => (
      <div
        key={i}
        className={cn(
          'rounded-full animate-pulse',
          size,
          color.replace('text-', 'bg-')
        )}
        style={{
          animationDelay: `${i * 0.2}s`,
          animationDuration: '1.4s'
        }}
      />
    ))}
  </div>
)

// =============================================================================
// LOADER PULSANTE
// =============================================================================

const PulseLoader: React.FC<{ size: string; color: string }> = ({ size, color }) => (
  <div className={cn('rounded-full animate-ping', size, color.replace('text-', 'bg-'))} />
)

// =============================================================================
// LOADER DE BARRAS
// =============================================================================

const BarsLoader: React.FC<{ size: string; color: string }> = ({ size, color }) => (
  <div className={cn('flex items-end space-x-1', size)}>
    {[0, 1, 2, 3].map((i) => (
      <div
        key={i}
        className={cn(
          'w-1 animate-pulse rounded-sm',
          color.replace('text-', 'bg-')
        )}
        style={{
          height: `${25 + (i % 2) * 25}%`,
          animationDelay: `${i * 0.1}s`,
          animationDuration: '1s'
        }}
      />
    ))}
  </div>
)

// =============================================================================
// SKELETON LOADER
// =============================================================================

const SkeletonLoader: React.FC = () => (
  <div className="space-y-3">
    <div className="h-4 bg-gray-200 rounded animate-pulse" />
    <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
    <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
  </div>
)

// =============================================================================
// COMPONENTE SKELETON PERSONALIZABLE
// =============================================================================

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '1rem',
  className,
  animate = true
}) => {
  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height
  }

  return (
    <div
      className={cn(
        'bg-gray-200 rounded',
        animate && 'animate-pulse',
        className
      )}
      style={style}
    />
  )
}

// =============================================================================
// LOADING OVERLAY
// =============================================================================

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  visible,
  message = 'Cargando...',
  transparent = false,
  className,
  children
}) => {
  if (!visible) {
    return <>{children}</>
  }

  return (
    <div className={cn('relative', className)}>
      {children}
      <div className={cn(
        'absolute inset-0 flex items-center justify-center z-40',
        transparent ? 'bg-white/60' : 'bg-white/90',
        'backdrop-blur-sm'
      )}>
        <div className="flex flex-col items-center gap-3">
          <SpinnerLoader size="w-8 h-8" color="text-blue-600" />
          <p className="text-sm font-medium text-gray-700">{message}</p>
        </div>
      </div>
    </div>
  )
}

// =============================================================================
// COMPONENTES ESPECIALIZADOS PARA POS
// =============================================================================

/**
 * Loading para catálogo de productos
 */
export const ProductGridSkeleton: React.FC<{ count?: number }> = ({ count = 8 }) => (
  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="bg-white p-4 rounded-lg border shadow-sm">
        <Skeleton height="5rem" className="mb-3" />
        <Skeleton height="0.75rem" className="mb-2" />
        <Skeleton height="0.75rem" width="60%" className="mb-2" />
        <Skeleton height="1rem" width="40%" />
      </div>
    ))}
  </div>
)

/**
 * Loading para lista de elementos
 */
export const ListSkeleton: React.FC<{ count?: number; showAvatar?: boolean }> = ({ 
  count = 5, 
  showAvatar = false 
}) => (
  <div className="space-y-3">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="flex items-center space-x-3 p-4 bg-white rounded-lg border">
        {showAvatar && (
          <Skeleton width="3rem" height="3rem" className="rounded-full" />
        )}
        <div className="flex-1 space-y-2">
          <Skeleton height="1rem" width="80%" />
          <Skeleton height="0.75rem" width="60%" />
        </div>
        <Skeleton width="5rem" height="2rem" />
      </div>
    ))}
  </div>
)

/**
 * Loading para tabla
 */
export const TableSkeleton: React.FC<{ 
  rows?: number
  columns?: number 
}> = ({ rows = 5, columns = 4 }) => (
  <div className="bg-white rounded-lg border overflow-hidden">
    {/* Header */}
    <div className="grid grid-cols-4 gap-4 p-4 bg-gray-50 border-b">
      {Array.from({ length: columns }).map((_, i) => (
        <Skeleton key={i} height="1rem" />
      ))}
    </div>
    
    {/* Rows */}
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div key={rowIndex} className="grid grid-cols-4 gap-4 p-4 border-b border-gray-100 last:border-b-0">
        {Array.from({ length: columns }).map((_, colIndex) => (
          <Skeleton key={colIndex} height="1rem" />
        ))}
      </div>
    ))}
  </div>
)

/**
 * Loading para dashboard cards
 */
export const DashboardCardSkeleton: React.FC = () => (
  <div className="bg-white p-6 rounded-lg border shadow-sm">
    <div className="flex items-center justify-between mb-4">
      <Skeleton width="6rem" height="1rem" />
      <Skeleton width="2rem" height="2rem" className="rounded" />
    </div>
    <Skeleton width="4rem" height="2rem" className="mb-2" />
    <Skeleton width="8rem" height="0.75rem" />
  </div>
)

/**
 * Loading para formularios
 */
export const FormSkeleton: React.FC<{ fields?: number }> = ({ fields = 4 }) => (
  <div className="space-y-6">
    {Array.from({ length: fields }).map((_, i) => (
      <div key={i} className="space-y-2">
        <Skeleton width="6rem" height="1rem" />
        <Skeleton height="2.5rem" />
      </div>
    ))}
    
    <div className="flex justify-end space-x-3 pt-4">
      <Skeleton width="5rem" height="2.5rem" />
      <Skeleton width="5rem" height="2.5rem" />
    </div>
  </div>
)

/**
 * Loading específico para POS
 */
export const POSLoadingSkeleton: React.FC = () => (
  <div className="grid grid-cols-12 gap-6 h-screen p-6">
    {/* Panel izquierdo - Productos */}
    <div className="col-span-8 space-y-4">
      <Skeleton height="3rem" />
      <ProductGridSkeleton count={12} />
    </div>
    
    {/* Panel derecho - Carrito */}
    <div className="col-span-4 space-y-4">
      <Skeleton height="3rem" />
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="bg-white p-4 rounded-lg border">
            <div className="flex justify-between items-start mb-2">
              <Skeleton width="60%" height="1rem" />
              <Skeleton width="3rem" height="1rem" />
            </div>
            <div className="flex justify-between items-center">
              <Skeleton width="40%" height="0.75rem" />
              <Skeleton width="4rem" height="1.5rem" />
            </div>
          </div>
        ))}
      </div>
      
      <div className="bg-white p-4 rounded-lg border space-y-3">
        <Skeleton height="1rem" />
        <Skeleton height="1rem" />
        <Skeleton height="3rem" />
      </div>
    </div>
  </div>
)

// =============================================================================
// LOADING STATES PARA DIFERENTES OPERACIONES
// =============================================================================

export const LoadingStates = {
  guardando: (
    <Cargando 
      variant="spinner" 
      message="Guardando datos..." 
      color="primary" 
    />
  ),
  
  cargando: (
    <Cargando 
      variant="spinner" 
      message="Cargando información..." 
      color="primary" 
    />
  ),
  
  enviandoSunat: (
    <Cargando 
      variant="dots" 
      message="Enviando a SUNAT..." 
      color="primary" 
    />
  ),
  
  procesandoVenta: (
    <Cargando 
      variant="pulse" 
      message="Procesando venta..." 
      color="primary" 
    />
  ),
  
  generandoReporte: (
    <Cargando 
      variant="bars" 
      message="Generando reporte..." 
      color="primary" 
    />
  )
}

// =============================================================================
// EXPORTACIONES
// =============================================================================

export default Cargando
export {
  Skeleton,
  LoadingOverlay,
  ProductGridSkeleton,
  ListSkeleton,
  TableSkeleton,
  DashboardCardSkeleton,
  FormSkeleton,
  POSLoadingSkeleton,
  LoadingStates
}