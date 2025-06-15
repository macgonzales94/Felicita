export interface ApiResponse<T = any> {
  count?: number
  next?: string | null
  previous?: string | null
  results?: T[]
  data?: T
}

export interface Cliente {
  id: number
  tipo_documento: string
  numero_documento: string
  razon_social: string
  nombre_comercial?: string
  direccion?: string
  telefono?: string
  email?: string
  activo: boolean
}

export interface Producto {
  id: number
  codigo: string
  descripcion: string
  categoria?: string
  precio_venta: number
  stock_actual: number
  activo: boolean
}