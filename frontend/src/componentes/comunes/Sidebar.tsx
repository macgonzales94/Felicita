/**
 * SERVICIOS DE PRODUCTOS - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Servicios para gestión de productos e inventario
 */

import api from './api'
import { toast } from 'react-hot-toast'

// =============================================================================
// TIPOS E INTERFACES
// =============================================================================

export interface Producto {
  id: number
  codigo: string
  codigo_barra?: string
  descripcion: string
  descripcion_corta?: string
  categoria: Categoria
  unidad_medida: UnidadMedida
  tipo_producto: 'BIEN' | 'SERVICIO'
  precio_compra: number
  precio_venta: number
  precio_mayorista?: number
  margen_ganancia?: number
  stock_actual: number
  stock_minimo: number
  stock_maximo: number
  ubicacion?: string
  afecto_igv: boolean
  activo: boolean
  imagen_url?: string
  peso?: number
  dimensiones?: string
  observaciones?: string
  proveedor_principal?: number
  fecha_ultima_compra?: string
  fecha_ultima_venta?: string
  created_at: string
  updated_at: string
}

export interface Categoria {
  id: number
  codigo: string
  nombre: string
  descripcion?: string
  categoria_padre?: number
  imagen_url?: string
  activo: boolean
  productos_count?: number
  created_at: string
  updated_at: string
}

export interface UnidadMedida {
  id: number
  codigo: string
  nombre: string
  abreviacion: string
  descripcion?: string
  activo: boolean
  created_at: string
  updated_at: string
}

export interface MovimientoInventario {
  id: number
  producto: Producto
  tipo: 'ENTRADA' | 'SALIDA' | 'AJUSTE' | 'TRANSFERENCIA'
  cantidad: number
  precio_unitario?: number
  total?: number
  stock_anterior: number
  stock_nuevo: number
  motivo: string
  documento_referencia?: string
  usuario: number
  fecha: string
  created_at: string
}

export interface ProductoStock {
  producto_id: number
  codigo: string
  descripcion: string
  stock_actual: number
  stock_minimo: number
  stock_maximo: number
  valor_stock: number
  ultimo_movimiento?: string
  alerta_stock: 'NORMAL' | 'BAJO' | 'AGOTADO' | 'EXCESO'
}

export interface ProductoVenta {
  id: number
  codigo: string
  descripcion: string
  precio_venta: number
  stock_disponible: number
  categoria: string
  imagen_url?: string
  activo: boolean
}

export interface ProductoFiltros {
  search?: string
  categoria?: number
  activo?: boolean
  con_stock?: boolean
  stock_bajo?: boolean
  precio_min?: number
  precio_max?: number
  tipo_producto?: 'BIEN' | 'SERVICIO'
  afecto_igv?: boolean
  proveedor?: number
  page?: number
  page_size?: number
  ordering?: string
}

export interface CrearProductoRequest {
  codigo: string
  codigo_barra?: string
  descripcion: string
  descripcion_corta?: string
  categoria_id: number
  unidad_medida_id: number
  tipo_producto: 'BIEN' | 'SERVICIO'
  precio_compra: number
  precio_venta: number
  precio_mayorista?: number
  stock_inicial?: number
  stock_minimo: number
  stock_maximo: number
  ubicacion?: string
  afecto_igv?: boolean
  imagen?: File
  peso?: number
  dimensiones?: string
  observaciones?: string
  proveedor_principal_id?: number
}

export interface ActualizarStockRequest {
  productos: Array<{
    producto_id: number
    cantidad: number
    tipo: 'ENTRADA' | 'SALIDA' | 'AJUSTE'
    motivo?: string
    precio_unitario?: number
  }>
  motivo_general?: string
  documento_referencia?: string
}

// =============================================================================
// SERVICIOS DE PRODUCTOS
// =============================================================================

/**
 * Obtener lista de productos con filtros y paginación
 */
export const obtenerProductos = async (filtros?: ProductoFiltros) => {
  try {
    const params = new URLSearchParams()
    
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const response = await api.get(`/productos/?${params.toString()}`)
    return response.data
  } catch (error) {
    console.error('Error al obtener productos:', error)
    throw error
  }
}

/**
 * Obtener producto por ID
 */
export const obtenerProductoPorId = async (id: number): Promise<Producto> => {
  try {
    const response = await api.get(`/productos/${id}/`)
    return response.data
  } catch (error) {
    console.error('Error al obtener producto:', error)
    throw error
  }
}

/**
 * Buscar productos para el POS
 */
export const buscarProductosPOS = async (query: string): Promise<ProductoVenta[]> => {
  try {
    if (query.length < 2) return []
    
    const response = await api.get(`/productos/pos/buscar/?q=${encodeURIComponent(query)}`)
    return response.data
  } catch (error) {
    console.error('Error al buscar productos POS:', error)
    return []
  }
}

/**
 * Obtener productos con stock bajo
 */
export const obtenerProductosStockBajo = async (): Promise<ProductoStock[]> => {
  try {
    const response = await api.get('/productos/stock-bajo/')
    return response.data
  } catch (error) {
    console.error('Error al obtener productos con stock bajo:', error)
    throw error
  }
}

/**
 * Obtener catálogo para POS con cache
 */
export const obtenerCatalogoPOS = async (categoria?: number): Promise<ProductoVenta[]> => {
  try {
    const params = new URLSearchParams()
    params.append('activo', 'true')
    params.append('con_stock', 'true')
    params.append('page_size', '100')
    
    if (categoria) {
      params.append('categoria', String(categoria))
    }
    
    const response = await api.get(`/productos/pos/catalogo/?${params.toString()}`)
    return response.data.results || response.data
  } catch (error) {
    console.error('Error al obtener catálogo POS:', error)
    throw error
  }
}

/**
 * Crear nuevo producto
 */
export const crearProducto = async (datos: CrearProductoRequest): Promise<Producto> => {
  try {
    const formData = new FormData()
    
    // Agregar campos al FormData
    Object.entries(datos).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (key === 'imagen' && value instanceof File) {
          formData.append('imagen', value)
        } else {
          formData.append(key, String(value))
        }
      }
    })
    
    const response = await api.post('/productos/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    toast.success('Producto creado correctamente')
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al crear producto'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Actualizar producto existente
 */
export const actualizarProducto = async (id: number, datos: Partial<CrearProductoRequest>): Promise<Producto> => {
  try {
    const formData = new FormData()
    
    Object.entries(datos).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (key === 'imagen' && value instanceof File) {
          formData.append('imagen', value)
        } else {
          formData.append(key, String(value))
        }
      }
    })
    
    const response = await api.patch(`/productos/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    toast.success('Producto actualizado correctamente')
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al actualizar producto'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Eliminar producto
 */
export const eliminarProducto = async (id: number): Promise<void> => {
  try {
    await api.delete(`/productos/${id}/`)
    toast.success('Producto eliminado correctamente')
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al eliminar producto'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Actualizar stock de productos
 */
export const actualizarStock = async (datos: ActualizarStockRequest): Promise<MovimientoInventario[]> => {
  try {
    const response = await api.post('/productos/actualizar-stock/', datos)
    toast.success(`Stock actualizado para ${datos.productos.length} producto(s)`)
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al actualizar stock'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Obtener movimientos de inventario
 */
export const obtenerMovimientosInventario = async (filtros?: {
  producto_id?: number
  tipo?: string
  fecha_desde?: string
  fecha_hasta?: string
  page?: number
}) => {
  try {
    const params = new URLSearchParams()
    
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const response = await api.get(`/inventario/movimientos/?${params.toString()}`)
    return response.data
  } catch (error) {
    console.error('Error al obtener movimientos:', error)
    throw error
  }
}

/**
 * Verificar stock disponible
 */
export const verificarStock = async (productoId: number): Promise<{
  stock_actual: number
  stock_disponible: number
  reservado: number
  ubicaciones: Array<{ ubicacion: string; cantidad: number }>
}> => {
  try {
    const response = await api.get(`/productos/${productoId}/stock/`)
    return response.data
  } catch (error) {
    console.error('Error al verificar stock:', error)
    throw error
  }
}

/**
 * Obtener productos más vendidos
 */
export const obtenerProductosMasVendidos = async (periodo: 'dia' | 'semana' | 'mes' = 'mes', limite: number = 10) => {
  try {
    const response = await api.get(`/productos/mas-vendidos/?periodo=${periodo}&limite=${limite}`)
    return response.data
  } catch (error) {
    console.error('Error al obtener productos más vendidos:', error)
    throw error
  }
}

// =============================================================================
// SERVICIOS DE CATEGORÍAS
// =============================================================================

/**
 * Obtener todas las categorías
 */
export const obtenerCategorias = async (filtros?: {
  activo?: boolean
  con_productos?: boolean
  parent?: number
}): Promise<Categoria[]> => {
  try {
    const params = new URLSearchParams()
    
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const response = await api.get(`/categorias/?${params.toString()}`)
    return response.data.results || response.data
  } catch (error) {
    console.error('Error al obtener categorías:', error)
    throw error
  }
}

/**
 * Crear nueva categoría
 */
export const crearCategoria = async (datos: {
  codigo: string
  nombre: string
  descripcion?: string
  categoria_padre_id?: number
  imagen?: File
}): Promise<Categoria> => {
  try {
    const formData = new FormData()
    
    Object.entries(datos).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (key === 'imagen' && value instanceof File) {
          formData.append('imagen', value)
        } else {
          formData.append(key, String(value))
        }
      }
    })
    
    const response = await api.post('/categorias/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    toast.success('Categoría creada correctamente')
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al crear categoría'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Actualizar categoría
 */
export const actualizarCategoria = async (id: number, datos: Partial<{
  nombre: string
  descripcion?: string
  categoria_padre_id?: number
  activo?: boolean
  imagen?: File
}>): Promise<Categoria> => {
  try {
    const formData = new FormData()
    
    Object.entries(datos).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (key === 'imagen' && value instanceof File) {
          formData.append('imagen', value)
        } else {
          formData.append(key, String(value))
        }
      }
    })
    
    const response = await api.patch(`/categorias/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    toast.success('Categoría actualizada correctamente')
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al actualizar categoría'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Eliminar categoría
 */
export const eliminarCategoria = async (id: number): Promise<void> => {
  try {
    await api.delete(`/categorias/${id}/`)
    toast.success('Categoría eliminada correctamente')
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al eliminar categoría'
    toast.error(mensaje)
    throw error
  }
}

// =============================================================================
// SERVICIOS DE UNIDADES DE MEDIDA
// =============================================================================

/**
 * Obtener unidades de medida
 */
export const obtenerUnidadesMedida = async (): Promise<UnidadMedida[]> => {
  try {
    const response = await api.get('/unidades-medida/')
    return response.data.results || response.data
  } catch (error) {
    console.error('Error al obtener unidades de medida:', error)
    throw error
  }
}

/**
 * Crear unidad de medida
 */
export const crearUnidadMedida = async (datos: {
  codigo: string
  nombre: string
  abreviacion: string
  descripcion?: string
}): Promise<UnidadMedida> => {
  try {
    const response = await api.post('/unidades-medida/', datos)
    toast.success('Unidad de medida creada correctamente')
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al crear unidad de medida'
    toast.error(mensaje)
    throw error
  }
}

// =============================================================================
// SERVICIOS DE REPORTES DE PRODUCTOS
// =============================================================================

/**
 * Generar reporte de inventario
 */
export const generarReporteInventario = async (filtros?: {
  categoria?: number
  con_valorizado?: boolean
  formato?: 'PDF' | 'EXCEL'
}): Promise<Blob> => {
  try {
    const params = new URLSearchParams()
    
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const response = await api.get(`/reportes/inventario/?${params.toString()}`, {
      responseType: 'blob'
    })
    
    return response.data
  } catch (error) {
    console.error('Error al generar reporte:', error)
    throw error
  }
}

/**
 * Exportar productos a Excel
 */
export const exportarProductosExcel = async (filtros?: ProductoFiltros): Promise<Blob> => {
  try {
    const params = new URLSearchParams()
    
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const response = await api.get(`/productos/exportar/?${params.toString()}`, {
      responseType: 'blob'
    })
    
    return response.data
  } catch (error) {
    console.error('Error al exportar productos:', error)
    throw error
  }
}

/**
 * Importar productos desde Excel
 */
export const importarProductosExcel = async (archivo: File): Promise<{
  exitosos: number
  errores: number
  detalles: Array<{ fila: number; error: string }>
}> => {
  try {
    const formData = new FormData()
    formData.append('archivo', archivo)
    
    const response = await api.post('/productos/importar/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    toast.success(`Importación completada: ${response.data.exitosos} productos procesados`)
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al importar productos'
    toast.error(mensaje)
    throw error
  }
}

// =============================================================================
// UTILIDADES
// =============================================================================

/**
 * Descargar archivo blob
 */
export const descargarArchivo = (blob: Blob, nombreArchivo: string): void => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = nombreArchivo
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

/**
 * Calcular margen de ganancia
 */
export const calcularMargen = (precioVenta: number, precioCompra: number): number => {
  if (precioCompra === 0) return 0
  return ((precioVenta - precioCompra) / precioCompra) * 100
}

/**
 * Calcular precio de venta con margen
 */
export const calcularPrecioConMargen = (precioCompra: number, margen: number): number => {
  return precioCompra * (1 + margen / 100)
}

/**
 * Validar código de producto
 */
export const validarCodigoProducto = async (codigo: string, productoId?: number): Promise<boolean> => {
  try {
    const params = new URLSearchParams()
    params.append('codigo', codigo)
    if (productoId) {
      params.append('exclude_id', String(productoId))
    }
    
    const response = await api.get(`/productos/validar-codigo/?${params.toString()}`)
    return response.data.disponible
  } catch (error) {
    console.error('Error al validar código:', error)
    return false
  }
}

export default {
  obtenerProductos,
  obtenerProductoPorId,
  buscarProductosPOS,
  obtenerProductosStockBajo,
  obtenerCatalogoPOS,
  crearProducto,
  actualizarProducto,
  eliminarProducto,
  actualizarStock,
  obtenerMovimientosInventario,
  verificarStock,
  obtenerProductosMasVendidos,
  obtenerCategorias,
  crearCategoria,
  actualizarCategoria,
  eliminarCategoria,
  obtenerUnidadesMedida,
  crearUnidadMedida,
  generarReporteInventario,
  exportarProductosExcel,
  importarProductosExcel,
  descargarArchivo,
  calcularMargen,
  calcularPrecioConMargen,
  validarCodigoProducto
}