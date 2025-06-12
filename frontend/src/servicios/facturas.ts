/**
 * SERVICIOS DE FACTURACIÓN - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Servicios para comunicación con API de facturación
 */

import api from './api';
import { 
  Factura, 
  Boleta, 
  NotaCredito, 
  CrearFacturaRequest,
  CrearBoletaRequest,
  CrearNotaCreditoRequest,
  EstadoSunatResponse,
  ResumenDiarioResponse,
  SerieComprobante,
  FiltrosFactura,
  AccionMasivaRequest,
  ReporteVentas
} from '../types';

// =============================================================================
// SERVICIOS DE FACTURAS
// =============================================================================

/**
 * Obtener lista de facturas con filtros
 */
export const obtenerFacturas = async (filtros?: FiltrosFactura): Promise<{
  count: number;
  next: string | null;
  previous: string | null;
  results: Factura[];
}> => {
  const params = new URLSearchParams();
  
  if (filtros) {
    Object.entries(filtros).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });
  }
  
  const response = await api.get(`/api/facturacion/facturas/?${params.toString()}`);
  return response.data;
};

/**
 * Obtener factura por ID
 */
export const obtenerFacturaPorId = async (id: number): Promise<Factura> => {
  const response = await api.get(`/api/facturacion/facturas/${id}/`);
  return response.data;
};

/**
 * Crear nueva factura
 */
export const crearFactura = async (datosFactura: CrearFacturaRequest): Promise<Factura> => {
  const response = await api.post('/api/facturacion/facturas/', datosFactura);
  return response.data;
};

/**
 * Actualizar factura
 */
export const actualizarFactura = async (id: number, datosFactura: Partial<CrearFacturaRequest>): Promise<Factura> => {
  const response = await api.patch(`/api/facturacion/facturas/${id}/`, datosFactura);
  return response.data;
};

/**
 * Eliminar factura
 */
export const eliminarFactura = async (id: number): Promise<void> => {
  await api.delete(`/api/facturacion/facturas/${id}/`);
};

/**
 * Enviar factura a SUNAT
 */
export const enviarFacturaSunat = async (id: number): Promise<{
  success: boolean;
  message: string;
  nubefact_id: string;
  estado_sunat: string;
}> => {
  const response = await api.post(`/api/facturacion/facturas/${id}/enviar_sunat/`);
  return response.data;
};

/**
 * Consultar estado de factura en SUNAT
 */
export const consultarEstadoFactura = async (id: number): Promise<EstadoSunatResponse> => {
  const response = await api.get(`/api/facturacion/facturas/${id}/consultar_estado/`);
  return response.data;
};

/**
 * Anular factura
 */
export const anularFactura = async (id: number, motivo: string, codigoMotivo: string = '01'): Promise<{
  success: boolean;
  message: string;
  ticket: string;
}> => {
  const response = await api.post(`/api/facturacion/facturas/${id}/anular/`, {
    motivo,
    codigo_motivo: codigoMotivo
  });
  return response.data;
};

/**
 * Descargar XML de factura
 */
export const descargarXmlFactura = async (id: number): Promise<{
  xml_content: string;
  filename: string;
}> => {
  const response = await api.get(`/api/facturacion/facturas/${id}/descargar_xml/`);
  return response.data;
};

/**
 * Descargar PDF de factura
 */
export const descargarPdfFactura = async (id: number): Promise<{
  pdf_url: string;
  filename: string;
}> => {
  const response = await api.get(`/api/facturacion/facturas/${id}/descargar_pdf/`);
  return response.data;
};

/**
 * Obtener resumen diario de facturas
 */
export const obtenerResumenDiarioFacturas = async (): Promise<ResumenDiarioResponse> => {
  const response = await api.get('/api/facturacion/facturas/resumen_diario/');
  return response.data;
};

/**
 * Obtener facturas por cliente
 */
export const obtenerFacturasPorCliente = async (clienteId: number, page?: number): Promise<{
  count: number;
  next: string | null;
  previous: string | null;
  results: Factura[];
}> => {
  const params = new URLSearchParams();
  params.append('cliente_id', String(clienteId));
  if (page) params.append('page', String(page));
  
  const response = await api.get(`/api/facturacion/facturas/por_cliente/?${params.toString()}`);
  return response.data;
};

// =============================================================================
// SERVICIOS DE BOLETAS
// =============================================================================

/**
 * Obtener lista de boletas
 */
export const obtenerBoletas = async (filtros?: FiltrosFactura): Promise<{
  count: number;
  next: string | null;
  previous: string | null;
  results: Boleta[];
}> => {
  const params = new URLSearchParams();
  
  if (filtros) {
    Object.entries(filtros).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });
  }
  
  const response = await api.get(`/api/facturacion/boletas/?${params.toString()}`);
  return response.data;
};

/**
 * Crear nueva boleta
 */
export const crearBoleta = async (datosBoleta: CrearBoletaRequest): Promise<Boleta> => {
  const response = await api.post('/api/facturacion/boletas/', datosBoleta);
  return response.data;
};

/**
 * Enviar boleta a SUNAT
 */
export const enviarBoletaSunat = async (id: number): Promise<{
  success: boolean;
  message: string;
  nubefact_id: string;
  estado_sunat: string;
}> => {
  const response = await api.post(`/api/facturacion/boletas/${id}/enviar_sunat/`);
  return response.data;
};

/**
 * Obtener resumen diario de boletas
 */
export const obtenerResumenDiarioBoletas = async (): Promise<ResumenDiarioResponse> => {
  const response = await api.get('/api/facturacion/boletas/resumen_diario/');
  return response.data;
};

// =============================================================================
// SERVICIOS DE NOTAS DE CRÉDITO
// =============================================================================

/**
 * Obtener lista de notas de crédito
 */
export const obtenerNotasCredito = async (filtros?: FiltrosFactura): Promise<{
  count: number;
  next: string | null;
  previous: string | null;
  results: NotaCredito[];
}> => {
  const params = new URLSearchParams();
  
  if (filtros) {
    Object.entries(filtros).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });
  }
  
  const response = await api.get(`/api/facturacion/notas-credito/?${params.toString()}`);
  return response.data;
};

/**
 * Crear nota de crédito
 */
export const crearNotaCredito = async (datosNota: CrearNotaCreditoRequest): Promise<NotaCredito> => {
  const response = await api.post('/api/facturacion/notas-credito/', datosNota);
  return response.data;
};

/**
 * Crear nota de crédito desde factura
 */
export const crearNotaCreditoDesdeFactura = async (
  facturaId: number,
  serie: string,
  codigoMotivo: string,
  descripcionMotivo: string
): Promise<NotaCredito> => {
  const response = await api.post('/api/facturacion/notas-credito/desde_factura/', {
    factura_id: facturaId,
    serie,
    codigo_motivo: codigoMotivo,
    descripcion_motivo: descripcionMotivo
  });
  return response.data;
};

// =============================================================================
// SERVICIOS DE SERIES
// =============================================================================

/**
 * Obtener series de comprobantes
 */
export const obtenerSeries = async (): Promise<SerieComprobante[]> => {
  const response = await api.get('/api/facturacion/series/');
  return response.data.results || response.data;
};

/**
 * Obtener series por tipo de comprobante
 */
export const obtenerSeriesPorTipo = async (tipo: string): Promise<SerieComprobante[]> => {
  const response = await api.get(`/api/facturacion/series/por_tipo/?tipo=${tipo}`);
  return response.data;
};

/**
 * Crear nueva serie
 */
export const crearSerie = async (serie: Omit<SerieComprobante, 'id'>): Promise<SerieComprobante> => {
  const response = await api.post('/api/facturacion/series/', serie);
  return response.data;
};

/**
 * Actualizar serie
 */
export const actualizarSerie = async (id: number, serie: Partial<SerieComprobante>): Promise<SerieComprobante> => {
  const response = await api.patch(`/api/facturacion/series/${id}/`, serie);
  return response.data;
};

/**
 * Reiniciar numeración de serie
 */
export const reiniciarNumeracionSerie = async (id: number, siguienteNumero: number): Promise<{
  success: boolean;
  message: string;
  siguiente_numero: number;
}> => {
  const response = await api.post(`/api/facturacion/series/${id}/reiniciar_numeracion/`, {
    siguiente_numero: siguienteNumero
  });
  return response.data;
};

// =============================================================================
// SERVICIOS DE PUNTO DE VENTA
// =============================================================================

/**
 * Crear venta desde punto de venta
 */
export const crearVentaPOS = async (datosVenta: {
  tipo_comprobante: 'factura' | 'boleta';
  cliente_id: number;
  items: Array<{
    producto_id: number;
    cantidad: number;
    precio_unitario: number;
    descuento?: number;
  }>;
  medio_pago?: string;
  observaciones?: string;
}): Promise<Factura | Boleta> => {
  const response = await api.post('/api/pos/crear-venta/', datosVenta);
  return response.data;
};

/**
 * Buscar cliente para POS
 */
export const buscarClientePOS = async (consulta: string): Promise<Array<{
  id: number;
  numero_documento: string;
  razon_social: string;
  tipo_documento: string;
}>> => {
  const response = await api.get(`/api/pos/buscar-cliente/?q=${encodeURIComponent(consulta)}`);
  return response.data;
};

/**
 * Buscar producto para POS
 */
export const buscarProductoPOS = async (consulta: string): Promise<Array<{
  id: number;
  codigo_producto: string;
  descripcion: string;
  precio_venta: number;
  stock_disponible: number;
  activo: boolean;
}>> => {
  const response = await api.get(`/api/pos/buscar-producto/?q=${encodeURIComponent(consulta)}`);
  return response.data;
};

/**
 * Calcular totales para POS
 */
export const calcularTotalesPOS = async (items: Array<{
  producto_id: number;
  cantidad: number;
  precio_unitario: number;
  descuento?: number;
}>, descuentoGlobal?: number): Promise<{
  subtotal: number;
  igv: number;
  total: number;
  items_calculados: Array<{
    subtotal: number;
    igv: number;
    total: number;
  }>;
}> => {
  const response = await api.post('/api/pos/calcular-totales/', {
    items,
    descuento_global: descuentoGlobal || 0
  });
  return response.data;
};

// =============================================================================
// SERVICIOS DE REPORTES
// =============================================================================

/**
 * Obtener estadísticas para dashboard
 */
export const obtenerEstadisticasDashboard = async (): Promise<{
  fecha_consulta: string;
  facturas: any;
  boletas: any;
  totales: {
    ingresos_hoy: number;
    comprobantes_hoy: number;
    ingresos_semana: number;
    ingresos_mes: number;
  };
}> => {
  const response = await api.get('/api/facturacion/estadisticas/dashboard/');
  return response.data;
};

/**
 * Obtener ventas por período
 */
export const obtenerVentasPorPeriodo = async (
  periodo: 'dia' | 'semana' | 'mes' = 'dia',
  limite: number = 30
): Promise<{
  periodo: string;
  ventas: Array<{
    fecha: string;
    total_facturas: number;
    cantidad_facturas: number;
    total_boletas: number;
    cantidad_boletas: number;
    total_general: number;
    cantidad_general: number;
  }>;
}> => {
  const response = await api.get(`/api/facturacion/estadisticas/ventas_por_periodo/?periodo=${periodo}&limite=${limite}`);
  return response.data;
};

/**
 * Obtener reporte de ventas diarias
 */
export const obtenerReporteVentasDiarias = async (
  fechaDesde: string,
  fechaHasta: string
): Promise<ReporteVentas> => {
  const response = await api.get(`/api/reportes/ventas-diarias/?fecha_desde=${fechaDesde}&fecha_hasta=${fechaHasta}`);
  return response.data;
};

/**
 * Obtener top clientes
 */
export const obtenerTopClientes = async (limite: number = 10): Promise<Array<{
  cliente_id: number;
  cliente_nombre: string;
  cliente_documento: string;
  total_ventas: number;
  cantidad_comprobantes: number;
  ultima_compra: string;
}>> => {
  const response = await api.get(`/api/reportes/top-clientes/?limite=${limite}`);
  return response.data;
};

// =============================================================================
// SERVICIOS DE VALIDACIÓN
// =============================================================================

/**
 * Validar numeración de comprobante
 */
export const validarNumeracion = async (
  serie: string,
  numero: number,
  tipoComprobante: string
): Promise<{
  valido: boolean;
  mensaje: string;
  siguiente_numero_sugerido?: number;
}> => {
  const response = await api.post('/api/validar-numeracion/', {
    serie,
    numero,
    tipo_comprobante: tipoComprobante
  });
  return response.data;
};

/**
 * Validar cliente para tipo de comprobante
 */
export const validarClienteComprobante = async (
  clienteId: number,
  tipoComprobante: 'factura' | 'boleta'
): Promise<{
  valido: boolean;
  mensaje: string;
}> => {
  const response = await api.post('/api/validar-cliente-comprobante/', {
    cliente_id: clienteId,
    tipo_comprobante: tipoComprobante
  });
  return response.data;
};

/**
 * Consultar RUC en SUNAT
 */
export const consultarRuc = async (ruc: string): Promise<{
  ruc: string;
  razon_social: string;
  estado: string;
  direccion: string;
  ubigeo: string;
  valido: boolean;
}> => {
  const response = await api.get(`/api/consultar-ruc/${ruc}/`);
  return response.data;
};

/**
 * Consultar DNI en RENIEC
 */
export const consultarDni = async (dni: string): Promise<{
  dni: string;
  nombres: string;
  apellido_paterno: string;
  apellido_materno: string;
  nombre_completo: string;
  valido: boolean;
}> => {
  const response = await api.get(`/api/consultar-dni/${dni}/`);
  return response.data;
};

// =============================================================================
// SERVICIOS DE EXPORTACIÓN
// =============================================================================

/**
 * Exportar facturas a Excel
 */
export const exportarFacturasExcel = async (filtros?: FiltrosFactura): Promise<Blob> => {
  const params = new URLSearchParams();
  
  if (filtros) {
    Object.entries(filtros).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });
  }
  
  const response = await api.get(`/api/exportar/facturas-excel/?${params.toString()}`, {
    responseType: 'blob'
  });
  return response.data;
};

/**
 * Exportar boletas a Excel
 */
export const exportarBoletasExcel = async (filtros?: FiltrosFactura): Promise<Blob> => {
  const params = new URLSearchParams();
  
  if (filtros) {
    Object.entries(filtros).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });
  }
  
  const response = await api.get(`/api/exportar/boletas-excel/?${params.toString()}`, {
    responseType: 'blob'
  });
  return response.data;
};

// =============================================================================
// SERVICIOS DE SINCRONIZACIÓN
// =============================================================================

/**
 * Sincronizar estados con SUNAT
 */
export const sincronizarEstadosSunat = async (): Promise<{
  success: boolean;
  comprobantes_actualizados: number;
  mensaje: string;
}> => {
  const response = await api.post('/api/sync/estados-sunat/');
  return response.data;
};

/**
 * Reenviar comprobantes pendientes
 */
export const reenviarComprobantesPendientes = async (): Promise<{
  success: boolean;
  comprobantes_reenviados: number;
  mensaje: string;
}> => {
  const response = await api.post('/api/sync/reenviar-pendientes/');
  return response.data;
};

// =============================================================================
// SERVICIOS DE ACCIONES MASIVAS
// =============================================================================

/**
 * Ejecutar acciones masivas en facturas
 */
export const ejecutarAccionMasivaFacturas = async (accion: AccionMasivaRequest): Promise<{
  success: boolean;
  procesados: number;
  errores: number;
  mensaje: string;
  detalles: Array<{
    id: number;
    resultado: 'exitoso' | 'error';
    mensaje: string;
  }>;
}> => {
  const response = await api.post('/api/facturas/acciones-masivas/', accion);
  return response.data;
};

// =============================================================================
// UTILIDADES
// =============================================================================

/**
 * Descargar archivo desde blob
 */
export const descargarArchivo = (blob: Blob, nombreArchivo: string): void => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = nombreArchivo;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Formatear número de comprobante
 */
export const formatearNumeroComprobante = (serie: string, numero: number): string => {
  return `${serie}-${numero.toString().padStart(8, '0')}`;
};

/**
 * Obtener color según estado SUNAT
 */
export const obtenerColorEstadoSunat = (estado: string): string => {
  switch (estado) {
    case 'ACEPTADO':
      return 'green';
    case 'RECHAZADO':
      return 'red';
    case 'ANULADO':
      return 'gray';
    case 'PENDIENTE':
    default:
      return 'yellow';
  }
};

/**
 * Validar formato de serie
 */
export const validarFormatoSerie = (serie: string): boolean => {
  // Serie debe tener 4 caracteres: 1 letra + 3 números
  const regex = /^[A-Z]\d{3}$/;
  return regex.test(serie);
};

/**
 * Calcular IGV
 */
export const calcularIgv = (subtotal: number, tasaIgv: number = 0.18): number => {
  return Number((subtotal * tasaIgv).toFixed(2));
};

/**
 * Calcular total con IGV
 */
export const calcularTotalConIgv = (subtotal: number, tasaIgv: number = 0.18): number => {
  return Number((subtotal * (1 + tasaIgv)).toFixed(2));
};