/**
 * UTILIDADES HELPER - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Funciones auxiliares para la aplicación
 */

import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

// =============================================================================
// UTILIDADES DE CLASES CSS
// =============================================================================

/**
 * Combina clases de CSS con Tailwind merge
 * Evita conflictos entre clases de Tailwind
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// =============================================================================
// UTILIDADES DE FORMATEO
// =============================================================================

/**
 * Formatea números como moneda peruana
 */
export const formatearMoneda = (monto: number): string => {
  return new Intl.NumberFormat('es-PE', {
    style: 'currency',
    currency: 'PEN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(monto)
}

/**
 * Formatea números con separadores de miles
 */
export const formatearNumero = (numero: number, decimales: number = 2): string => {
  return new Intl.NumberFormat('es-PE', {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  }).format(numero)
}

/**
 * Formatea fechas en formato peruano
 */
export const formatearFecha = (fecha: Date | string): string => {
  const fechaObj = typeof fecha === 'string' ? new Date(fecha) : fecha
  return fechaObj.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

/**
 * Formatea fechas con hora
 */
export const formatearFechaHora = (fecha: Date | string): string => {
  const fechaObj = typeof fecha === 'string' ? new Date(fecha) : fecha
  return fechaObj.toLocaleString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// =============================================================================
// UTILIDADES DE TEXTO
// =============================================================================

/**
 * Capitaliza la primera letra de cada palabra
 */
export const capitalizarTexto = (texto: string): string => {
  return texto
    .toLowerCase()
    .split(' ')
    .map(palabra => palabra.charAt(0).toUpperCase() + palabra.slice(1))
    .join(' ')
}

/**
 * Trunca texto a una longitud específica
 */
export const truncarTexto = (texto: string, longitud: number = 50): string => {
  if (texto.length <= longitud) return texto
  return texto.substring(0, longitud) + '...'
}

/**
 * Genera iniciales de un nombre
 */
export const generarIniciales = (nombre: string): string => {
  return nombre
    .split(' ')
    .map(palabra => palabra.charAt(0).toUpperCase())
    .slice(0, 2)
    .join('')
}

// =============================================================================
// UTILIDADES DE ARRAYS Y OBJETOS
// =============================================================================

/**
 * Elimina duplicados de un array basado en una propiedad
 */
export const eliminarDuplicados = <T>(array: T[], key: keyof T): T[] => {
  const seen = new Set()
  return array.filter(item => {
    const valor = item[key]
    if (seen.has(valor)) {
      return false
    }
    seen.add(valor)
    return true
  })
}

/**
 * Agrupa array por una propiedad específica
 */
export const agruparPor = <T>(array: T[], key: keyof T): Record<string, T[]> => {
  return array.reduce((grupos, item) => {
    const valor = String(item[key])
    if (!grupos[valor]) {
      grupos[valor] = []
    }
    grupos[valor].push(item)
    return grupos
  }, {} as Record<string, T[]>)
}

/**
 * Ordena array por una propiedad
 */
export const ordenarPor = <T>(
  array: T[], 
  key: keyof T, 
  direccion: 'asc' | 'desc' = 'asc'
): T[] => {
  return [...array].sort((a, b) => {
    const valorA = a[key]
    const valorB = b[key]
    
    if (valorA < valorB) return direccion === 'asc' ? -1 : 1
    if (valorA > valorB) return direccion === 'asc' ? 1 : -1
    return 0
  })
}

// =============================================================================
// UTILIDADES DE NÚMEROS
// =============================================================================

/**
 * Redondea un número a decimales específicos
 */
export const redondear = (numero: number, decimales: number = 2): number => {
  return Number(Math.round(Number(numero + 'e' + decimales)) + 'e-' + decimales)
}

/**
 * Calcula porcentaje
 */
export const calcularPorcentaje = (valor: number, total: number): number => {
  if (total === 0) return 0
  return redondear((valor / total) * 100, 2)
}

/**
 * Suma array de números
 */
export const sumarArray = (numeros: number[]): number => {
  return redondear(numeros.reduce((suma, num) => suma + num, 0), 2)
}

// =============================================================================
// UTILIDADES DE VALIDACIÓN
// =============================================================================

/**
 * Verifica si un valor está vacío
 */
export const estaVacio = (valor: any): boolean => {
  if (valor === null || valor === undefined) return true
  if (typeof valor === 'string') return valor.trim() === ''
  if (Array.isArray(valor)) return valor.length === 0
  if (typeof valor === 'object') return Object.keys(valor).length === 0
  return false
}

/**
 * Verifica si es un email válido
 */
export const esEmailValido = (email: string): boolean => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

/**
 * Verifica si es un número válido
 */
export const esNumeroValido = (valor: any): boolean => {
  return !isNaN(valor) && !isNaN(parseFloat(valor))
}

// =============================================================================
// UTILIDADES DE URLS Y SLUGS
// =============================================================================

/**
 * Convierte texto a slug URL-friendly
 */
export const crearSlug = (texto: string): string => {
  return texto
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '') // Remover caracteres especiales
    .replace(/[\s_-]+/g, '-') // Reemplazar espacios con guiones
    .replace(/^-+|-+$/g, '') // Remover guiones al inicio y final
}

/**
 * Construye query string de parámetros
 */
export const construirQueryString = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams()
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value))
    }
  })
  
  return searchParams.toString()
}

// =============================================================================
// UTILIDADES DE TIEMPO
// =============================================================================

/**
 * Obtiene fecha actual en formato ISO
 */
export const fechaActualISO = (): string => {
  return new Date().toISOString()
}

/**
 * Añade días a una fecha
 */
export const añadirDias = (fecha: Date, dias: number): Date => {
  const nuevaFecha = new Date(fecha)
  nuevaFecha.setDate(nuevaFecha.getDate() + dias)
  return nuevaFecha
}

/**
 * Calcula diferencia en días entre fechas
 */
export const diferenciaDias = (fecha1: Date, fecha2: Date): number => {
  const unDia = 24 * 60 * 60 * 1000
  return Math.round((fecha2.getTime() - fecha1.getTime()) / unDia)
}

// =============================================================================
// UTILIDADES DE ALMACENAMIENTO
// =============================================================================

/**
 * Guarda datos en localStorage de forma segura
 */
export const guardarEnStorage = (clave: string, valor: any): boolean => {
  try {
    localStorage.setItem(clave, JSON.stringify(valor))
    return true
  } catch (error) {
    console.error('Error al guardar en localStorage:', error)
    return false
  }
}

/**
 * Obtiene datos de localStorage de forma segura
 */
export const obtenerDeStorage = <T>(clave: string, valorDefault: T): T => {
  try {
    const item = localStorage.getItem(clave)
    return item ? JSON.parse(item) : valorDefault
  } catch (error) {
    console.error('Error al leer de localStorage:', error)
    return valorDefault
  }
}

/**
 * Elimina datos de localStorage
 */
export const eliminarDeStorage = (clave: string): void => {
  try {
    localStorage.removeItem(clave)
  } catch (error) {
    console.error('Error al eliminar de localStorage:', error)
  }
}

// =============================================================================
// UTILIDADES DE DEBUGGING
// =============================================================================

/**
 * Log de desarrollo que solo se ejecuta en modo dev
 */
export const logDev = (...args: any[]): void => {
  if (import.meta.env.DEV) {
    console.log('🔧 [FELICITA DEV]:', ...args)
  }
}

/**
 * Mide tiempo de ejecución de una función
 */
export const medirTiempo = async <T>(
  nombre: string, 
  fn: () => Promise<T>
): Promise<T> => {
  const inicio = performance.now()
  const resultado = await fn()
  const fin = performance.now()
  
  logDev(`⏱️ ${nombre}: ${(fin - inicio).toFixed(2)}ms`)
  
  return resultado
}

// =============================================================================
// UTILIDADES DE ERRORES
// =============================================================================

/**
 * Manejo seguro de errores async
 */
export const manejarErrorSeguro = async <T>(
  promesa: Promise<T>
): Promise<[T | null, Error | null]> => {
  try {
    const resultado = await promesa
    return [resultado, null]
  } catch (error) {
    return [null, error as Error]
  }
}

/**
 * Extrae mensaje de error legible
 */
export const extraerMensajeError = (error: any): string => {
  if (typeof error === 'string') return error
  if (error?.response?.data?.message) return error.response.data.message
  if (error?.message) return error.message
  return 'Ha ocurrido un error inesperado'
}