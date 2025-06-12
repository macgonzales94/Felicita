/**
 * CARD COMPONENT - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Componente de tarjeta base siguiendo shadcn/ui patterns
 */

import React from 'react'
import { cn } from '../../utils/helpers'

// =============================================================================
// INTERFACES
// =============================================================================

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'outlined' | 'elevated' | 'filled'
  size?: 'sm' | 'md' | 'lg'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
  clickable?: boolean
}

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'separated'
}

export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'separated'
  justify?: 'start' | 'center' | 'end' | 'between'
}

// =============================================================================
// COMPONENTE CARD PRINCIPAL
// =============================================================================

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ 
    className, 
    variant = 'default',
    size = 'md',
    padding = 'md',
    hover = false,
    clickable = false,
    children,
    onClick,
    ...props 
  }, ref) => {
    
    // Clases base
    const baseClasses = "rounded-lg border bg-card text-card-foreground shadow-sm"
    
    // Variantes de estilo
    const variantClasses = {
      default: "border-border",
      outlined: "border-2 border-border bg-transparent shadow-none",
      elevated: "border-0 shadow-lg",
      filled: "border-0 bg-muted"
    }
    
    // Tamaños
    const sizeClasses = {
      sm: "rounded-md",
      md: "rounded-lg", 
      lg: "rounded-xl"
    }
    
    // Padding
    const paddingClasses = {
      none: "",
      sm: "p-3",
      md: "p-6",
      lg: "p-8"
    }
    
    // Estados interactivos
    const interactiveClasses = {
      hover: hover ? "transition-shadow hover:shadow-md" : "",
      clickable: clickable || onClick ? "cursor-pointer transition-all hover:shadow-md active:scale-[0.98]" : ""
    }

    return (
      <div
        ref={ref}
        className={cn(
          baseClasses,
          variantClasses[variant],
          sizeClasses[size],
          paddingClasses[padding],
          interactiveClasses.hover,
          interactiveClasses.clickable,
          className
        )}
        onClick={onClick}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = "Card"

// =============================================================================
// COMPONENTE CARD HEADER
// =============================================================================

const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, variant = 'default', children, ...props }, ref) => {
    
    const baseClasses = "flex flex-col space-y-1.5"
    
    const variantClasses = {
      default: "p-6 pb-0",
      separated: "p-6 border-b border-border"
    }

    return (
      <div
        ref={ref}
        className={cn(baseClasses, variantClasses[variant], className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)

CardHeader.displayName = "CardHeader"

// =============================================================================
// COMPONENTE CARD CONTENT
// =============================================================================

const CardContent = React.forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, padding = 'md', children, ...props }, ref) => {
    
    const paddingClasses = {
      none: "",
      sm: "p-3 pt-0",
      md: "p-6 pt-0", 
      lg: "p-8 pt-0"
    }

    return (
      <div
        ref={ref}
        className={cn(paddingClasses[padding], className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)

CardContent.displayName = "CardContent"

// =============================================================================
// COMPONENTE CARD FOOTER
// =============================================================================

const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ 
    className, 
    variant = 'default',
    justify = 'start',
    children, 
    ...props 
  }, ref) => {
    
    const baseClasses = "flex items-center"
    
    const variantClasses = {
      default: "p-6 pt-0",
      separated: "p-6 border-t border-border"
    }
    
    const justifyClasses = {
      start: "justify-start",
      center: "justify-center",
      end: "justify-end",
      between: "justify-between"
    }

    return (
      <div
        ref={ref}
        className={cn(
          baseClasses,
          variantClasses[variant],
          justifyClasses[justify],
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

CardFooter.displayName = "CardFooter"

// =============================================================================
// COMPONENTE CARD TITLE
// =============================================================================

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, children, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  >
    {children}
  </h3>
))

CardTitle.displayName = "CardTitle"

// =============================================================================
// COMPONENTE CARD DESCRIPTION
// =============================================================================

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, children, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  >
    {children}
  </p>
))

CardDescription.displayName = "CardDescription"

// =============================================================================
// COMPONENTES ESPECIALIZADOS PARA POS
// =============================================================================

/**
 * Tarjeta de producto para el catálogo del POS
 */
export interface ProductCardProps extends CardProps {
  producto: {
    id: number
    codigo: string
    descripcion: string
    precio: number
    stock?: number
    imagen?: string
  }
  onSelect?: (producto: any) => void
  selected?: boolean
  disabled?: boolean
}

const ProductCard = React.forwardRef<HTMLDivElement, ProductCardProps>(
  ({ 
    producto, 
    onSelect, 
    selected = false,
    disabled = false,
    className,
    ...props 
  }, ref) => {
    
    return (
      <Card
        ref={ref}
        variant={selected ? "filled" : "default"}
        clickable={!disabled}
        hover={!disabled}
        className={cn(
          "relative transition-all duration-200",
          selected && "ring-2 ring-primary ring-offset-2",
          disabled && "opacity-50 cursor-not-allowed",
          !disabled && "hover:scale-[1.02]",
          className
        )}
        onClick={() => !disabled && onSelect?.(producto)}
        {...props}
      >
        {/* Badge de stock bajo */}
        {producto.stock !== undefined && producto.stock < 10 && (
          <div className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
            Stock: {producto.stock}
          </div>
        )}
        
        <CardContent padding="sm">
          {/* Imagen del producto */}
          {producto.imagen ? (
            <div className="w-full h-20 bg-gray-100 rounded-md mb-3 overflow-hidden">
              <img 
                src={producto.imagen} 
                alt={producto.descripcion}
                className="w-full h-full object-cover"
              />
            </div>
          ) : (
            <div className="w-full h-20 bg-gray-100 rounded-md mb-3 flex items-center justify-center">
              <span className="text-gray-400 text-xs">Sin imagen</span>
            </div>
          )}
          
          {/* Código del producto */}
          <div className="text-xs text-muted-foreground mb-1">
            {producto.codigo}
          </div>
          
          {/* Descripción */}
          <div className="font-medium text-sm mb-2 line-clamp-2">
            {producto.descripcion}
          </div>
          
          {/* Precio */}
          <div className="text-lg font-bold text-primary">
            S/ {producto.precio.toFixed(2)}
          </div>
          
          {/* Stock disponible */}
          {producto.stock !== undefined && (
            <div className="text-xs text-muted-foreground mt-1">
              Stock: {producto.stock}
            </div>
          )}
        </CardContent>
      </Card>
    )
  }
)

ProductCard.displayName = "ProductCard"

/**
 * Tarjeta de resumen para totales del carrito
 */
export interface SummaryCardProps extends CardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: React.ReactNode
  color?: 'default' | 'primary' | 'success' | 'warning' | 'error'
}

const SummaryCard = React.forwardRef<HTMLDivElement, SummaryCardProps>(
  ({ 
    title,
    value,
    subtitle,
    icon,
    color = 'default',
    className,
    ...props 
  }, ref) => {
    
    const colorClasses = {
      default: "text-foreground",
      primary: "text-primary",
      success: "text-green-600",
      warning: "text-yellow-600",
      error: "text-red-600"
    }
    
    return (
      <Card
        ref={ref}
        variant="outlined"
        className={cn("text-center", className)}
        {...props}
      >
        <CardContent padding="md">
          {icon && (
            <div className={cn("mx-auto mb-2 w-8 h-8", colorClasses[color])}>
              {icon}
            </div>
          )}
          
          <div className="text-sm text-muted-foreground mb-1">
            {title}
          </div>
          
          <div className={cn("text-2xl font-bold", colorClasses[color])}>
            {typeof value === 'number' ? `S/ ${value.toFixed(2)}` : value}
          </div>
          
          {subtitle && (
            <div className="text-xs text-muted-foreground mt-1">
              {subtitle}
            </div>
          )}
        </CardContent>
      </Card>
    )
  }
)

SummaryCard.displayName = "SummaryCard"

// =============================================================================
// EXPORTACIONES
// =============================================================================

export {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
  CardTitle,
  CardDescription,
  ProductCard,
  SummaryCard
}