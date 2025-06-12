/**
 * INPUT COMPONENT - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Componente de input base siguiendo shadcn/ui patterns
 */

import React from 'react'
import { cn } from '../../utils/helpers'
import { validarDocumento, validarMonto, validarEmail, TipoDocumento } from '../../utils/validaciones'

// =============================================================================
// INTERFACES BASE
// =============================================================================

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  variant?: 'default' | 'filled' | 'outlined'
  inputSize?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
}

export interface SearchInputProps extends Omit<InputProps, 'type'> {
  onSearch?: (value: string) => void
  onClear?: () => void
  debounceMs?: number
  showClearButton?: boolean
}

export interface NumberInputProps extends Omit<InputProps, 'type'> {
  min?: number
  max?: number
  step?: number
  precision?: number
  allowNegative?: boolean
  format?: 'currency' | 'percentage' | 'decimal'
}

export interface DocumentInputProps extends Omit<InputProps, 'type'> {
  documentType?: TipoDocumento
  autoDetectType?: boolean
  onValidation?: (isValid: boolean, data?: any) => void
}

// =============================================================================
// COMPONENTE INPUT BASE
// =============================================================================

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({
    className,
    type = 'text',
    label,
    error,
    helperText,
    leftIcon,
    rightIcon,
    variant = 'default',
    inputSize = 'md',
    fullWidth = true,
    disabled,
    ...props
  }, ref) => {
    
    // Clases base
    const baseClasses = "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
    
    // Variantes de estilo
    const variantClasses = {
      default: "border-input",
      filled: "border-0 bg-muted",
      outlined: "border-2 border-input bg-transparent"
    }
    
    // Tamaños
    const sizeClasses = {
      sm: "h-8 px-2 text-xs",
      md: "h-10 px-3 text-sm",
      lg: "h-12 px-4 text-base"
    }
    
    // Estados de error
    const errorClasses = error ? "border-destructive focus-visible:ring-destructive" : ""
    
    // Clases para iconos
    const iconSpacing = {
      left: leftIcon ? "pl-10" : "",
      right: rightIcon ? "pr-10" : ""
    }

    return (
      <div className={cn("space-y-2", fullWidth ? "w-full" : "")}>
        {/* Label */}
        {label && (
          <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
            {label}
          </label>
        )}
        
        {/* Input Container */}
        <div className="relative">
          {/* Left Icon */}
          {leftIcon && (
            <div className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground">
              {leftIcon}
            </div>
          )}
          
          {/* Input */}
          <input
            type={type}
            className={cn(
              baseClasses,
              variantClasses[variant],
              sizeClasses[inputSize],
              errorClasses,
              iconSpacing.left,
              iconSpacing.right,
              className
            )}
            ref={ref}
            disabled={disabled}
            {...props}
          />
          
          {/* Right Icon */}
          {rightIcon && (
            <div className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground">
              {rightIcon}
            </div>
          )}
        </div>
        
        {/* Error Message */}
        {error && (
          <p className="text-sm text-destructive">
            {error}
          </p>
        )}
        
        {/* Helper Text */}
        {helperText && !error && (
          <p className="text-sm text-muted-foreground">
            {helperText}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = "Input"

// =============================================================================
// COMPONENTE SEARCH INPUT
// =============================================================================

const SearchInput = React.forwardRef<HTMLInputElement, SearchInputProps>(
  ({
    onSearch,
    onClear,
    debounceMs = 300,
    showClearButton = true,
    placeholder = "Buscar...",
    value,
    onChange,
    ...props
  }, ref) => {
    
    const [searchValue, setSearchValue] = React.useState(value || '')
    const [isSearching, setIsSearching] = React.useState(false)
    const timeoutRef = React.useRef<NodeJS.Timeout>()
    
    // Efecto para debounce de búsqueda
    React.useEffect(() => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
      
      setIsSearching(true)
      timeoutRef.current = setTimeout(() => {
        onSearch?.(searchValue)
        setIsSearching(false)
      }, debounceMs)
      
      return () => {
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current)
        }
      }
    }, [searchValue, debounceMs, onSearch])
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value
      setSearchValue(newValue)
      onChange?.(e)
    }
    
    const handleClear = () => {
      setSearchValue('')
      onClear?.()
    }
    
    const SearchIcon = () => (
      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    )
    
    const LoadingIcon = () => (
      <svg className="h-4 w-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    )
    
    const ClearIcon = () => (
      <button
        type="button"
        onClick={handleClear}
        className="h-4 w-4 hover:text-foreground transition-colors"
      >
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    )

    return (
      <Input
        ref={ref}
        type="text"
        placeholder={placeholder}
        value={searchValue}
        onChange={handleChange}
        leftIcon={isSearching ? <LoadingIcon /> : <SearchIcon />}
        rightIcon={showClearButton && searchValue ? <ClearIcon /> : undefined}
        {...props}
      />
    )
  }
)

SearchInput.displayName = "SearchInput"

// =============================================================================
// COMPONENTE NUMBER INPUT
// =============================================================================

const NumberInput = React.forwardRef<HTMLInputElement, NumberInputProps>(
  ({
    min,
    max,
    step = 1,
    precision = 2,
    allowNegative = false,
    format = 'decimal',
    value,
    onChange,
    onBlur,
    ...props
  }, ref) => {
    
    const [displayValue, setDisplayValue] = React.useState('')
    const [numericValue, setNumericValue] = React.useState<number>(0)
    
    // Formatear valor según el tipo
    const formatValue = (val: number): string => {
      switch (format) {
        case 'currency':
          return new Intl.NumberFormat('es-PE', {
            style: 'currency',
            currency: 'PEN',
            minimumFractionDigits: precision,
            maximumFractionDigits: precision,
          }).format(val)
        case 'percentage':
          return `${val.toFixed(precision)}%`
        default:
          return val.toFixed(precision)
      }
    }
    
    // Parsear valor de display a número
    const parseDisplayValue = (val: string): number => {
      const cleaned = val.replace(/[^\d.-]/g, '')
      const parsed = parseFloat(cleaned)
      return isNaN(parsed) ? 0 : parsed
    }
    
    // Manejar cambios
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      let inputValue = e.target.value
      
      // Remover caracteres no numéricos excepto punto y guión
      inputValue = inputValue.replace(/[^\d.-]/g, '')
      
      // Validar signo negativo
      if (!allowNegative) {
        inputValue = inputValue.replace(/-/g, '')
      }
      
      const parsedValue = parseDisplayValue(inputValue)
      
      // Validar límites
      if (min !== undefined && parsedValue < min) return
      if (max !== undefined && parsedValue > max) return
      
      setDisplayValue(inputValue)
      setNumericValue(parsedValue)
      
      // Crear evento sintético con valor numérico
      const syntheticEvent = {
        ...e,
        target: {
          ...e.target,
          value: parsedValue.toString()
        }
      }
      onChange?.(syntheticEvent as React.ChangeEvent<HTMLInputElement>)
    }
    
    // Manejar blur para formatear
    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setDisplayValue(formatValue(numericValue))
      onBlur?.(e)
    }
    
    // Manejar focus para mostrar valor crudo
    const handleFocus = () => {
      setDisplayValue(numericValue.toString())
    }
    
    React.useEffect(() => {
      if (value !== undefined) {
        const val = typeof value === 'string' ? parseFloat(value) : value
        setNumericValue(val)
        setDisplayValue(formatValue(val))
      }
    }, [value, format, precision])

    return (
      <Input
        ref={ref}
        type="text"
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        onFocus={handleFocus}
        {...props}
      />
    )
  }
)

NumberInput.displayName = "NumberInput"

// =============================================================================
// COMPONENTE DOCUMENT INPUT
// =============================================================================

const DocumentInput = React.forwardRef<HTMLInputElement, DocumentInputProps>(
  ({
    documentType,
    autoDetectType = true,
    onValidation,
    value,
    onChange,
    onBlur,
    ...props
  }, ref) => {
    
    const [inputValue, setInputValue] = React.useState(value || '')
    const [validation, setValidation] = React.useState<{ isValid: boolean; message?: string; data?: any }>({
      isValid: true
    })
    
    // Validar documento
    const validateDocument = (val: string, type?: TipoDocumento) => {
      if (!val.trim()) {
        setValidation({ isValid: true })
        onValidation?.(true)
        return
      }
      
      let docType = type
      if (autoDetectType && !docType) {
        // Auto-detectar tipo de documento
        const cleaned = val.replace(/\D/g, '')
        if (cleaned.length === 8) docType = 'DNI'
        else if (cleaned.length === 11) docType = 'RUC'
        else if (cleaned.length === 9) docType = 'CARNET_EXTRANJERIA'
        else if (/[A-Za-z]/.test(val)) docType = 'PASAPORTE'
      }
      
      if (docType) {
        const result = validarDocumento(val, docType)
        setValidation({
          isValid: result.valido,
          message: result.mensaje,
          data: result.datos
        })
        onValidation?.(result.valido, result.datos)
      } else {
        setValidation({ isValid: false, message: 'Tipo de documento no reconocido' })
        onValidation?.(false)
      }
    }
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value
      setInputValue(newValue)
      onChange?.(e)
    }
    
    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      validateDocument(inputValue, documentType)
      onBlur?.(e)
    }
    
    React.useEffect(() => {
      if (value !== undefined) {
        setInputValue(value)
      }
    }, [value])
    
    const DocumentIcon = () => {
      switch (documentType) {
        case 'RUC':
          return (
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          )
        case 'DNI':
          return (
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
            </svg>
          )
        default:
          return (
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          )
      }
    }

    return (
      <Input
        ref={ref}
        type="text"
        value={inputValue}
        onChange={handleChange}
        onBlur={handleBlur}
        leftIcon={<DocumentIcon />}
        error={!validation.isValid ? validation.message : undefined}
        {...props}
      />
    )
  }
)

DocumentInput.displayName = "DocumentInput"

// =============================================================================
// EXPORTACIONES
// =============================================================================

export { Input, SearchInput, NumberInput, DocumentInput }