/**
 * SERVICIOS DE FACTURAS - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Servicios para gestión de facturación electrónica y SUNAT
 */

import api from './api'
import { toast } from 'react-hot-toast'
import { SUNAT_CONFIG } from '../utils/constantes'

// =============================================================================
// TIPOS E INTERFACES
// =============================================================================

export interface Factura {
  id: number
  numero: number
  serie: string
  numero_completo: string
  tipo_comprobante: string
  cliente: {
    id: number
    numero_documento: string
    razon_social: string
    tipo_documento: string
    direccion?: string
    email?: string
  }
  fecha_emision: string
  fecha_vencimiento?: string
  moneda: string
  subtotal: number
  total_descuentos: number
  base_imponible: number
  igv: number
  total: number
  metodo_pago: string
  observaciones?: string
  estado: 'BORRADOR' | 'EMITIDO' | 'ENVIADO' | 'ACEPTADO' | 'RECHAZADO' | 'ANULADO'
  estado_sunat?: string
  hash_sunat?: string
  codigo_qr?: string
  xml_firmado?: string
  pdf_url?: string
  items: ItemFactura[]
  empresa: {
    id: number
    ruc: string
    razon_social: string
    direccion: string
  }
  usuario_creador: {
    id: number
    nombres: string
    apellidos: string
  }
  created_at: string
  updated_at: string
}

export interface Boleta {
  id: number
  numero: number
  serie: string
  numero_completo: string
  tipo_comprobante: string
  cliente?: {
    id: number
    numero_documento: string
    razon_social: string
    tipo_documento: string
  }
  fecha_emision: string
  moneda: string
  subtotal: number
  total_descuentos: number
  base_imponible: number
  igv: number
  total: number
  metodo_pago: string
  observaciones?: string
  estado: 'BORRADOR' | 'EMITIDO' | 'ENVIADO' | 'ACEPTADO' | 'RECHAZADO' | 'ANULADO'
  estado_sunat?: string
  hash_sunat?: string
  codigo_qr?: string
  xml_firmado?: string
  pdf_url?: string
  items: ItemBoleta[]
  empresa: {
    id: number
    ruc: string
    razon_social: string
    direccion: string
  }
  usuario_creador: {
    id: number
    nombres: string
    apellidos: string
  }
  created_at: string
  updated_at: string
}

export interface NotaCredito {
  id: number
  numero: number
  serie: string
  numero_completo: string
  tipo_comprobante: string
  comprobante_referencia: {
    id: number
    tipo: string
    serie: string
    numero: number
    numero_completo: string
  }
  motivo_codigo: string
  motivo_descripcion: string
  cliente: {
    id: number
    numero_documento: string
    razon_social: string
    tipo_documento: string
  }
  fecha_emision: string
  moneda: string
  subtotal: number
  total_descuentos: number
  base_imponible: number
  igv: number
  total: number
  observaciones?: string
  estado: 'BORRADOR' | 'EMITIDO' | 'ENVIADO' | 'ACEPTADO' | 'RECHAZADO' | 'ANULADO'
  estado_sunat?: string
  hash_sunat?: string
  codigo_qr?: string
  xml_firmado?: string
  pdf_url?: string
  items: ItemNotaCredito[]
  empresa: {
    id: number
    ruc: string
    razon_social: string
  }
  created_at: string
  updated_at: string
}

export interface ItemFactura {
  id: number
  producto: {
    id: number
    codigo: string
    descripcion: string
    unidad_medida: string
    precio_venta: number
  }
  cantidad: number
  precio_unitario: number
  descuento_porcentaje: number
  descuento_monto: number
  subtotal: number
  igv: number
  total: number
  observaciones?: string
}

export interface ItemBoleta {
  id: number
  producto: {
    id: number
    codigo: string
    descripcion: string
    unidad_medida: string
    precio_venta: number
  }
  cantidad: number
  precio_unitario: number
  descuento_porcentaje: number
  descuento_monto: number
  subtotal: number
  igv: number
  total: number
  observaciones?: string
}

export interface ItemNotaCredito {
  id: number
  producto: {
    id: number
    codigo: string
    descripcion: string
    unidad_medida: string
  }
  cantidad: number
  precio_unitario: number
  descuento_porcentaje: number
  descuento_monto: number
  subtotal: number
  igv: number
  total: number
  observaciones?: string
}

export interface SerieComprobante {
  id: number
  tipo_comprobante: string
  codigo_tipo: string
  serie: string
  siguiente_numero: number
  activo: boolean
  predeterminado: boolean
  created_at: string
}

export interface CrearFacturaRequest {
  cliente_id: number
  serie_id?: number
  tipo_comprobante?: string
  metodo_pago?: string
  observaciones?: string
  items: ItemComprobanteRequest[]
}

export interface CrearBoletaRequest {
  cliente_id?: number
  serie_id?: number
  tipo_comprobante?: string
  metodo_pago?: string
  observaciones?: string
  items: ItemComprobanteRequest[]
}

export interface CrearNotaCreditoRequest {
  comprobante_referencia_id: number
  motivo_codigo: string
  motivo_descripcion: string
  observaciones?: string
  items: ItemComprobanteRequest[]
}

export interface ItemComprobanteRequest {
  producto_id: number
  cantidad: number
  precio_unitario: number
  descuento_porcentaje?: number
  descuento_monto?: number
  observaciones?: string
}

export interface EstadoSunatResponse {
  estado: 'PENDIENTE' | 'ENVIADO' | 'ACEPTADO' | 'RECHAZADO' | 'ANULADO'
  codigo_respuesta?: string
  descripcion_respuesta?: string
  observaciones?: string
  fecha_envio?: string
  fecha_respuesta?: string
  hash?: string
  cdr_url?: string
  xml_url?: string
  pdf_url?: string
}

export interface FiltrosComprobantes {
  search?: string
  tipo_comprobante?: string
  estado?: string
  estado_sunat?: string
  cliente_id?: number
  fecha_desde?: string
  fecha_hasta?: string
  serie?: string
  numero_desde?: number
  numero_hasta?: number
  usuario_id?: number
  page?: number
  page_size?: number
  ordering?: string
}

export interface ResumenVentas {
  total_facturas: number
  total_boletas: number
  total_notas_credito: number
  total_ventas: number
  total_igv: number
  total_sin_igv: number
  promedio_venta: number
  mayor_venta: number
  menor_venta: number
  ventas_por_metodo_pago: Array<{
    metodo: string
    cantidad: number
    total: number
  }>
  ventas_por_dia: Array<{
    fecha: string
    cantidad: number
    total: number
  }>
}

// =============================================================================
// SERVICIOS DE FACTURAS
// =============================================================================

/**
 * Obtener lista de facturas con filtros
 */
export const obtenerFacturas = async (filtros?: FiltrosComprobantes) => {
  try {
    const params = new URLSearchParams()
    
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const response = await api.get(`/facturas/?${params.toString()}`)
    return response.data
  } catch (error) {
    console.error('Error al obtener facturas:', error)
    throw error
  }
}

/**
 * Obtener factura por ID
 */
export const obtenerFacturaPorId = async (id: number): Promise<Factura> => {
  try {
    const response = await api.get(`/facturas/${id}/`)
    return response.data
  } catch (error) {
    console.error('Error al obtener factura:', error)
    throw error
  }
}

/**
 * Crear nueva factura
 */
export const crearFactura = async (datos: CrearFacturaRequest): Promise<Factura> => {
  try {
    const response = await api.post('/facturas/', {
      ...datos,
      tipo_comprobante: datos.tipo_comprobante || '01'
    })
    
    toast.success(`Factura ${response.data.numero_completo} creada correctamente`)
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al crear factura'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Actualizar factura existente
 */
export const actualizarFactura = async (id: number, datos: Partial<CrearFacturaRequest>): Promise<Factura> => {
  try {
    const response = await api.patch(`/facturas/${id}/`, datos)
    toast.success('Factura actualizada correctamente')
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al actualizar factura'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Anular factura
 */
export const anularFactura = async (id: number, motivo: string): Promise<Factura> => {
  try {
    const response = await api.post(`/facturas/${id}/anular/`, { motivo })
    toast.success('Factura anulada correctamente')
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al anular factura'
    toast.error(mensaje)
    throw error
  }
}

// =============================================================================
// SERVICIOS DE BOLETAS
// =============================================================================

/**
 * Obtener lista de boletas
 */
export const obtenerBoletas = async (filtros?: FiltrosComprobantes) => {
  try {
    const params = new URLSearchParams()
    
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const response = await api.get(`/boletas/?${params.toString()}`)
    return response.data
  } catch (error) {
    console.error('Error al obtener boletas:', error)
    throw error
  }
}

/**
 * Crear nueva boleta
 */
export const crearBoleta = async (datos: CrearBoletaRequest): Promise<Boleta> => {
  try {
    const response = await api.post('/boletas/', {
      ...datos,
      tipo_comprobante: datos.tipo_comprobante || '03'
    })
    
    toast.success(`Boleta ${response.data.numero_completo} creada correctamente`)
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al crear boleta'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Anular boleta
 */
export const anularBoleta = async (id: number, motivo: string): Promise<Boleta> => {
  try {
    const response = await api.post(`/boletas/${id}/anular/`, { motivo })
    toast.success('Boleta anulada correctamente')
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al anular boleta'
    toast.error(mensaje)
    throw error
  }
}

// =============================================================================
// SERVICIOS DE NOTAS DE CRÉDITO
// =============================================================================

/**
 * Obtener lista de notas de crédito
 */
export const obtenerNotasCredito = async (filtros?: FiltrosComprobantes) => {
  try {
    const params = new URLSearchParams()
    
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const response = await api.get(`/notas-credito/?${params.toString()}`)
    return response.data
  } catch (error) {
    console.error('Error al obtener notas de crédito:', error)
    throw error
  }
}

/**
 * Crear nueva nota de crédito
 */
export const crearNotaCredito = async (datos: CrearNotaCreditoRequest): Promise<NotaCredito> => {
  try {
    const response = await api.post('/notas-credito/', {
      ...datos,
      tipo_comprobante: '07'
    })
    
    toast.success(`Nota de Crédito ${response.data.numero_completo} creada correctamente`)
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al crear nota de crédito'
    toast.error(mensaje)
    throw error
  }
}

// =============================================================================
// SERVICIOS DE SERIES
// =============================================================================

/**
 * Obtener series disponibles
 */
export const obtenerSeriesDisponibles = async (): Promise<SerieComprobante[]> => {
  try {
    const response = await api.get('/series-comprobantes/?activo=true')
    return response.data.results || response.data
  } catch (error) {
    console.error('Error al obtener series:', error)
    throw error
  }
}

/**
 * Obtener series por tipo de comprobante
 */
export const obtenerSeriesPorTipo = async (tipoComprobante: string): Promise<SerieComprobante[]> => {
  try {
    const response = await api.get(`/series-comprobantes/?tipo_comprobante=${tipoComprobante}&activo=true`)
    return response.data.results || response.data
  } catch (error) {
    console.error('Error al obtener series por tipo:', error)
    throw error
  }
}

/**
 * Crear nueva serie
 */
export const crearSerie = async (datos: {
  tipo_comprobante: string
  serie: string
  siguiente_numero?: number
  predeterminado?: boolean
}): Promise<SerieComprobante> => {
  try {
    const response = await api.post('/series-comprobantes/', datos)
    toast.success('Serie creada correctamente')
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al crear serie'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Actualizar serie
 */
export const actualizarSerie = async (id: number, datos: Partial<{
  serie: string
  siguiente_numero: number
  activo: boolean
  predeterminado: boolean
}>): Promise<SerieComprobante> => {
  try {
    const response = await api.patch(`/series-comprobantes/${id}/`, datos)
    toast.success('Serie actualizada correctamente')
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al actualizar serie'
    toast.error(mensaje)
    throw error
  }
}

// =============================================================================
// SERVICIOS DE SUNAT
// =============================================================================

/**
 * Enviar comprobante a SUNAT
 */
export const enviarComprobanteASunat = async (tipo: string, id: number): Promise<EstadoSunatResponse> => {
  try {
    const endpoint = tipo === 'factura' ? 'facturas' : 
                   tipo === 'boleta' ? 'boletas' : 'notas-credito'
    
    const response = await api.post(`/${endpoint}/${id}/enviar-sunat/`)
    
    if (response.data.estado === 'ACEPTADO') {
      toast.success('Comprobante enviado y aceptado por SUNAT')
    } else if (response.data.estado === 'RECHAZADO') {
      toast.error(`Comprobante rechazado por SUNAT: ${response.data.observaciones}`)
    } else {
      toast.info('Comprobante enviado a SUNAT, pendiente de respuesta')
    }
    
    return response.data
  } catch (error: any) {
    const mensaje = error.response?.data?.detail || 'Error al enviar a SUNAT'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Consultar estado en SUNAT
 */
export const consultarEstadoSunat = async (tipo: string, id: number): Promise<EstadoSunatResponse> => {
  try {
    const endpoint = tipo === 'factura' ? 'facturas' : 
                   tipo === 'boleta' ? 'boletas' : 'notas-credito'
    
    const response = await api.get(`/${endpoint}/${id}/estado-sunat/`)
    return response.data
  } catch (error: any) {
    console.error('Error al consultar estado SUNAT:', error)
    throw error
  }
}

/**
 * Descargar XML firmado
 */
export const descargarXML = async (tipo: string, id: number): Promise<Blob> => {
  try {
    const endpoint = tipo === 'factura' ? 'facturas' : 
                   tipo === 'boleta' ? 'boletas' : 'notas-credito'
    
    const response = await api.get(`/${endpoint}/${id}/xml/`, {
      responseType: 'blob'
    })
    
    return response.data
  } catch (error: any) {
    const mensaje = 'Error al descargar XML'
    toast.error(mensaje)
    throw error
  }
}

/**
 * Descargar PDF
 */
export const descargarPDF = async (tipo: string, id: number): Promise<Blob> => {
  try {
    const endpoint = tipo === 'factura' ? 'facturas' : 
                   tipo === 'boleta' ? 'boletas' : 'notas-credito'
    
    const response = await api.get(`/${endpoint}/${id}/pdf/`, {
      responseType: 'blob'
    })
    
    return response.data
  } catch (error: any) {
    const mensaje = 'Error al descargar PDF'
    toast.error(mensaje)
    throw error
  }
}

// =============================================================================
// SERVICIOS DE REPORTES
// =============================================================================

/**
 * Obtener resumen de ventas
 */
export const obtenerResumenVentas = async (filtros?: {
  fecha_desde?: string
  fecha_hasta?: string
  usuario_id?: number
  serie?: string
}): Promise<ResumenVentas> => {
  try {
    const params = new URLSearchParams()
    
    if (filtros) {
      Object.entries(filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value))
        }
      })
    }
    
    const response = await api.get(`/reportes/resumen-ventas/?${params.toString()}`)
    return response.data
  } catch (error) {
    console.error('Error al obtener resumen de ventas:', error)
    throw error
  }
}

/**
 * Obtener comprobantes por período
 */
export const obtenerComprobantesPorPeriodo = async (fechaDesde: string, fechaHasta: string) => {
  try {
    const response = await api.get(`/reportes/comprobantes-periodo/?fecha_desde=${fechaDesde}&fecha_hasta=${fechaHasta}`)
    return response.data
  } catch (error) {
    console.error('Error al obtener comprobantes por período:', error)
    throw error
  }
}

/**
 * Generar reporte PLE
 */
export const generarReportePLE = async (periodo: string, libro: string): Promise<Blob> => {
  try {
    const response = await api.get(`/reportes/ple/?periodo=${periodo}&libro=${libro}`, {
      responseType: 'blob'
    })
    
    return response.data
  } catch (error: any) {
    const mensaje = 'Error al generar reporte PLE'
    toast.error(mensaje)
    throw error
  }
}

// =============================================================================
// SERVICIOS DE VALIDACIÓN
// =============================================================================

/**
 * Validar numeración correlativa
 */
export const validarNumeracion = async (serieId: number): Promise<{
  valido: boolean
  siguiente_numero: number
  gaps?: number[]
  mensaje?: string
}> => {
  try {
    const response = await api.get(`/series-comprobantes/${serieId}/validar-numeracion/`)
    return response.data
  } catch (error) {
    console.error('Error al validar numeración:', error)
    return {
      valido: false,
      siguiente_numero: 1,
      mensaje: 'Error al validar numeración'
    }
  }
}

/**
 * Verificar duplicados
 */
export const verificarDuplicados = async (datos: {
  tipo_comprobante: string
  serie: string
  numero: number
  cliente_id?: number
  fecha_emision: string
}): Promise<{
  duplicado: boolean
  comprobantes_similares?: Array<{
    id: number
    numero_completo: string
    fecha_emision: string
  }>
}> => {
  try {
    const response = await api.post('/comprobantes/verificar-duplicados/', datos)
    return response.data
  } catch (error) {
    console.error('Error al verificar duplicados:', error)
    return { duplicado: false }
  }
}

// =============================================================================
// UTILIDADES
// =============================================================================

/**
 * Calcular totales de comprobante
 */
export const calcularTotalesComprobante = (items: ItemComprobanteRequest[]): {
  subtotal: number
  total_descuentos: number
  base_imponible: number
  igv: number
  total: number
} => {
  const resultado = items.reduce(
    (acc, item) => {
      const subtotalItem = item.cantidad * item.precio_unitario
      const descuentoItem = item.descuento_monto || (subtotalItem * (item.descuento_porcentaje || 0) / 100)
      const subtotalConDescuento = subtotalItem - descuentoItem
      const igvItem = subtotalConDescuento * SUNAT_CONFIG.TASAS_IMPUESTO.IGV
      
      return {
        subtotal: acc.subtotal + subtotalConDescuento,
        total_descuentos: acc.total_descuentos + descuentoItem,
        base_imponible: acc.base_imponible + subtotalConDescuento,
        igv: acc.igv + igvItem,
        total: acc.total + subtotalConDescuento + igvItem
      }
    },
    {
      subtotal: 0,
      total_descuentos: 0,
      base_imponible: 0,
      igv: 0,
      total: 0
    }
  )
  
  // Redondear a 2 decimales
  Object.keys(resultado).forEach(key => {
    resultado[key as keyof typeof resultado] = Math.round(resultado[key as keyof typeof resultado] * 100) / 100
  })
  
  return resultado
}

/**
 * Formatear número de comprobante
 */
export const formatearNumeroComprobante = (serie: string, numero: number): string => {
  return `${serie}-${numero.toString().padStart(8, '0')}`
}

/**
 * Obtener descripción de estado SUNAT
 */
export const obtenerDescripcionEstadoSunat = (estado: string): string => {
  const estados: Record<string, string> = {
    'PENDIENTE': 'Pendiente de envío',
    'ENVIADO': 'Enviado a SUNAT',
    'ACEPTADO': 'Aceptado por SUNAT',
    'RECHAZADO': 'Rechazado por SUNAT',
    'ANULADO': 'Anulado'
  }
  
  return estados[estado] || estado
}

/**
 * Validar comprobante antes del envío
 */
export const validarComprobanteParaEnvio = (comprobante: Factura | Boleta): {
  valido: boolean
  errores: string[]
} => {
  const errores: string[] = []
  
  // Validar que tenga items
  if (!comprobante.items || comprobante.items.length === 0) {
    errores.push('El comprobante debe tener al menos un item')
  }
  
  // Validar totales
  if (comprobante.total <= 0) {
    errores.push('El total debe ser mayor a cero')
  }
  
  // Validar cliente para facturas
  if (comprobante.tipo_comprobante === '01' && !comprobante.cliente) {
    errores.push('Las facturas requieren un cliente')
  }
  
  // Validar RUC del cliente para facturas
  if (comprobante.tipo_comprobante === '01' && comprobante.cliente?.tipo_documento !== 'RUC') {
    errores.push('Las facturas requieren un cliente con RUC')
  }
  
  return {
    valido: errores.length === 0,
    errores
  }
}

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

export default {
  // Facturas
  obtenerFacturas,
  obtenerFacturaPorId,
  crearFactura,
  actualizarFactura,
  anularFactura,
  
  // Boletas
  obtenerBoletas,
  crearBoleta,
  anularBoleta,
  
  // Notas de crédito
  obtenerNotasCredito,
  crearNotaCredito,
  
  // Series
  obtenerSeriesDisponibles,
  obtenerSeriesPorTipo,
  crearSerie,
  actualizarSerie,
  
  // SUNAT
  enviarComprobanteASunat,
  consultarEstadoSunat,
  descargarXML,
  descargarPDF,
  
  // Reportes
  obtenerResumenVentas,
  obtenerComprobantesPorPeriodo,
  generarReportePLE,
  
  // Validaciones
  validarNumeracion,
  verificarDuplicados,
  
  // Utilidades
  calcularTotalesComprobante,
  formatearNumeroComprobante,
  obtenerDescripcionEstadoSunat,
  validarComprobanteParaEnvio,
  descargarArchivo
}