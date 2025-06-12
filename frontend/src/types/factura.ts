/**
 * TYPES DE FACTURACIÓN - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Tipos TypeScript para el módulo de facturación
 */

import { Cliente } from './cliente';
import { Producto } from './producto';

// =============================================================================
// ENUMS Y CONSTANTES
// =============================================================================

export enum TipoComprobante {
  FACTURA = '01',
  BOLETA = '03',
  NOTA_CREDITO = '07',
  NOTA_DEBITO = '08',
  GUIA_REMISION = '09'
}

export enum EstadoSunat {
  PENDIENTE = 'PENDIENTE',
  ACEPTADO = 'ACEPTADO',
  RECHAZADO = 'RECHAZADO',
  ANULADO = 'ANULADO'
}

export enum Moneda {
  PEN = 'PEN',
  USD = 'USD',
  EUR = 'EUR'
}

export enum CondicionPago {
  CONTADO = 'CONTADO',
  CREDITO_30 = 'CREDITO_30',
  CREDITO_60 = 'CREDITO_60',
  CREDITO_90 = 'CREDITO_90'
}

export enum MedioPago {
  EFECTIVO = 'EFECTIVO',
  TRANSFERENCIA = 'TRANSFERENCIA',
  TARJETA = 'TARJETA',
  CHEQUE = 'CHEQUE'
}

export enum CodigoMotivoNotaCredito {
  ANULACION_OPERACION = '01',
  ANULACION_ERROR_RUC = '02',
  CORRECCION_ERROR_DESCRIPCION = '03',
  DESCUENTO_GLOBAL = '04',
  DESCUENTO_ITEM = '05',
  DEVOLUCION_TOTAL = '06',
  DEVOLUCION_ITEM = '07',
  BONIFICACION = '08',
  DISMINUCION_VALOR = '09',
  OTROS_CONCEPTOS = '10'
}

// =============================================================================
// INTERFACES BASE
// =============================================================================

export interface ItemComprobanteBase {
  id?: number;
  producto: Producto;
  descripcion: string;
  cantidad: number;
  precio_unitario: number;
  descuento: number;
  subtotal: number;
  igv: number;
  total: number;
  unidad_medida?: string;
  tipo_afectacion_igv?: number;
}

export interface ComprobanteBase {
  id: number;
  serie: string;
  numero: number;
  numero_completo: string;
  fecha_emision: string;
  fecha_vencimiento?: string;
  cliente: Cliente;
  cliente_data?: Cliente;
  moneda: Moneda;
  tipo_cambio: number;
  subtotal: number;
  descuento_global: number;
  igv: number;
  total: number;
  observaciones?: string;
  estado_sunat: EstadoSunat;
  estado_sunat_display: string;
  nubefact_id?: string;
  hash_cpe?: string;
  fecha_envio_sunat?: string;
  codigo_respuesta_sunat?: string;
  mensaje_sunat?: string;
  pdf_url?: string;
  xml_url?: string;
  usuario_creacion?: number;
  created_at: string;
  updated_at: string;
}

// =============================================================================
// INTERFACES ESPECÍFICAS DE COMPROBANTES
// =============================================================================

export interface ItemFactura extends ItemComprobanteBase {
  factura?: number;
}

export interface Factura extends ComprobanteBase {
  condicion_pago: CondicionPago;
  medio_pago: MedioPago;
  items: ItemFactura[];
  items_detalle?: ItemFactura[];
}

export interface ItemBoleta extends ItemComprobanteBase {
  boleta?: number;
}

export interface Boleta extends ComprobanteBase {
  items: ItemBoleta[];
  items_detalle?: ItemBoleta[];
}

export interface ItemNotaCredito extends ItemComprobanteBase {
  nota_credito?: number;
}

export interface NotaCredito extends ComprobanteBase {
  codigo_motivo: CodigoMotivoNotaCredito;
  descripcion_motivo: string;
  documento_modificado_tipo: TipoComprobante;
  documento_modificado_serie: string;
  documento_modificado_numero: number;
  items: ItemNotaCredito[];
  items_detalle?: ItemNotaCredito[];
}

export interface GuiaRemision {
  id: number;
  serie: string;
  numero: number;
  numero_completo: string;
  fecha_emision: string;
  punto_partida: string;
  punto_llegada: string;
  transportista: string;
  placa_vehiculo: string;
  motivo_traslado: string;
  peso_total: number;
  cantidad_bultos: number;
  observaciones?: string;
  estado_sunat: EstadoSunat;
  created_at: string;
  updated_at: string;
}

// =============================================================================
// INTERFACES PARA CREACIÓN
// =============================================================================

export interface ItemComprobanteRequest {
  producto_id: number;
  descripcion: string;
  cantidad: number;
  precio_unitario: number;
  descuento?: number;
}

export interface CrearComprobanteBaseRequest {
  cliente: number;
  serie: string;
  fecha_emision?: string;
  fecha_vencimiento?: string;
  moneda?: Moneda;
  tipo_cambio?: number;
  descuento_global?: number;
  observaciones?: string;
  items: ItemComprobanteRequest[];
}

export interface CrearFacturaRequest extends CrearComprobanteBaseRequest {
  condicion_pago?: CondicionPago;
  medio_pago?: MedioPago;
}

export interface CrearBoletaRequest extends CrearComprobanteBaseRequest {
  // Las boletas pueden tener campos específicos adicionales si es necesario
}

export interface CrearNotaCreditoRequest extends CrearComprobanteBaseRequest {
  codigo_motivo: CodigoMotivoNotaCredito;
  descripcion_motivo: string;
  documento_modificado_tipo: TipoComprobante;
  documento_modificado_serie: string;
  documento_modificado_numero: number;
}

// =============================================================================
// INTERFACES PARA SERIES
// =============================================================================

export interface SerieComprobante {
  id: number;
  serie: string;
  tipo_comprobante: TipoComprobante;
  siguiente_numero: number;
  activa: boolean;
  descripcion?: string;
  empresa?: number;
  created_at: string;
  updated_at: string;
}

// =============================================================================
// INTERFACES PARA FILTROS
// =============================================================================

export interface FiltrosFactura {
  fecha_emision?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  periodo?: 'hoy' | 'ayer' | 'semana' | 'mes' | 'trimestre' | 'año';
  cliente?: number;
  cliente_documento?: string;
  cliente_nombre?: string;
  serie?: string;
  numero?: number;
  numero_desde?: number;
  numero_hasta?: number;
  total?: number;
  total_desde?: number;
  total_hasta?: number;
  estado_sunat?: EstadoSunat;
  moneda?: Moneda;
  enviado_sunat?: boolean;
  condicion_pago?: CondicionPago;
  medio_pago?: MedioPago;
  fecha_vencimiento?: string;
  vencimiento_desde?: string;
  vencimiento_hasta?: string;
  vencidas?: boolean;
  por_vencer?: number;
  solo_ruc?: boolean;
  solo_dni?: boolean;
  page?: number;
  page_size?: number;
  ordering?: string;
  search?: string;
}

// =============================================================================
// INTERFACES PARA RESPUESTAS
// =============================================================================

export interface EstadoSunatResponse {
  nubefact_id: string;
  estado_sunat: EstadoSunat;
  codigo_respuesta: string;
  mensaje_sunat: string;
  fecha_consulta: string;
}

export interface ResumenDiarioResponse {
  fecha: string;
  resumen: {
    total_facturas: number;
    total_monto: number;
    total_aceptadas: number;
    total_pendientes: number;
  };
  facturas_recientes: Factura[];
}

export interface ResumenDiarioBoletasResponse {
  fecha: string;
  resumen: {
    total_boletas: number;
    total_monto: number;
    total_aceptadas: number;
    total_pendientes: number;
  };
  boletas_recientes: Boleta[];
}

export interface EstadisticasDashboard {
  fecha_consulta: string;
  facturas: {
    total_hoy: number;
    cantidad_hoy: number;
    total_ayer: number;
    total_semana: number;
    total_mes: number;
    aceptadas_sunat: number;
    pendientes_sunat: number;
    rechazadas_sunat: number;
  };
  boletas: {
    total_hoy: number;
    cantidad_hoy: number;
    total_semana: number;
    total_mes: number;
  };
  totales: {
    ingresos_hoy: number;
    comprobantes_hoy: number;
    ingresos_semana: number;
    ingresos_mes: number;
  };
}

export interface VentasPorPeriodo {
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
}

// =============================================================================
// INTERFACES PARA REPORTES
// =============================================================================

export interface ReporteVentas {
  periodo: {
    fecha_desde: string;
    fecha_hasta: string;
  };
  resumen: {
    total_ventas: number;
    total_comprobantes: number;
    promedio_venta: number;
    cliente_frecuente: string;
    producto_mas_vendido: string;
  };
  ventas_diarias: Array<{
    fecha: string;
    facturas: number;
    boletas: number;
    total: number;
  }>;
  top_clientes: Array<{
    cliente: string;
    total: number;
    cantidad: number;
  }>;
  top_productos: Array<{
    producto: string;
    cantidad: number;
    total: number;
  }>;
}

export interface TopCliente {
  cliente_id: number;
  cliente_nombre: string;
  cliente_documento: string;
  total_ventas: number;
  cantidad_comprobantes: number;
  ultima_compra: string;
}

export interface TopProducto {
  producto_id: number;
  producto_codigo: string;
  producto_descripcion: string;
  cantidad_vendida: number;
  total_ventas: number;
  promedio_precio: number;
}

// =============================================================================
// INTERFACES PARA PUNTO DE VENTA
// =============================================================================

export interface ItemPOS {
  producto_id: number;
  producto?: Producto;
  descripcion: string;
  cantidad: number;
  precio_unitario: number;
  descuento: number;
  subtotal: number;
  igv: number;
  total: number;
}

export interface VentaPOS {
  tipo_comprobante: 'factura' | 'boleta';
  cliente_id: number;
  cliente?: Cliente;
  serie?: string;
  items: ItemPOS[];
  subtotal: number;
  descuento_global: number;
  igv: number;
  total: number;
  medio_pago: MedioPago;
  observaciones?: string;
}

export interface CalculoTotalesPOS {
  subtotal: number;
  igv: number;
  total: number;
  items_calculados: Array<{
    subtotal: number;
    igv: number;
    total: number;
  }>;
}

// =============================================================================
// INTERFACES PARA ACCIONES MASIVAS
// =============================================================================

export interface AccionMasivaRequest {
  accion: 'enviar_sunat' | 'anular' | 'exportar' | 'eliminar';
  comprobantes_ids: number[];
  parametros?: {
    motivo_anulacion?: string;
    formato_exportacion?: 'excel' | 'pdf' | 'csv';
    filtros_adicionales?: any;
  };
}

export interface ResultadoAccionMasiva {
  success: boolean;
  procesados: number;
  errores: number;
  mensaje: string;
  detalles: Array<{
    id: number;
    resultado: 'exitoso' | 'error';
    mensaje: string;
  }>;
}

// =============================================================================
// INTERFACES PARA VALIDACIONES
// =============================================================================

export interface ValidacionNumeracion {
  valido: boolean;
  mensaje: string;
  siguiente_numero_sugerido?: number;
}

export interface ValidacionCliente {
  valido: boolean;
  mensaje: string;
}

export interface ConsultaRuc {
  ruc: string;
  razon_social: string;
  estado: string;
  direccion: string;
  ubigeo: string;
  valido: boolean;
}

export interface ConsultaDni {
  dni: string;
  nombres: string;
  apellido_paterno: string;
  apellido_materno: string;
  nombre_completo: string;
  valido: boolean;
}

// =============================================================================
// INTERFACES PARA NOTIFICACIONES
// =============================================================================

export interface NotificacionComprobante {
  id: number;
  tipo: 'info' | 'warning' | 'error' | 'success';
  titulo: string;
  mensaje: string;
  comprobante_id?: number;
  comprobante_tipo?: string;
  comprobante_numero?: string;
  fecha: string;
  leida: boolean;
}

// =============================================================================
// INTERFACES PARA CONFIGURACIÓN
// =============================================================================

export interface ConfiguracionFacturacion {
  series_activas: SerieComprobante[];
  igv_tasa: number;
  moneda_default: Moneda;
  condicion_pago_default: CondicionPago;
  medio_pago_default: MedioPago;
  envio_automatico_sunat: boolean;
  numeracion_automatica: boolean;
  validar_stock: boolean;
  generar_asientos_automaticos: boolean;
}

// =============================================================================
// INTERFACES PARA ESTADOS DE CARGA
// =============================================================================

export interface EstadoCargaComprobante {
  cargando: boolean;
  error: string | null;
  datos: Factura | Boleta | NotaCredito | null;
}

export interface EstadoCargaLista<T> {
  cargando: boolean;
  error: string | null;
  datos: T[];
  total: number;
  pagina_actual: number;
  paginas_totales: number;
}

// =============================================================================
// TYPES UTILITY
// =============================================================================

export type TipoComprobanteUnion = Factura | Boleta | NotaCredito;

export type CrearComprobanteUnion = CrearFacturaRequest | CrearBoletaRequest | CrearNotaCreditoRequest;

export type ItemComprobanteUnion = ItemFactura | ItemBoleta | ItemNotaCredito;

// =============================================================================
// INTERFACES PARA FORMULARIOS
// =============================================================================

export interface FormularioFactura {
  cliente_id: number | null;
  serie: string;
  fecha_emision: string;
  fecha_vencimiento: string;
  condicion_pago: CondicionPago;
  medio_pago: MedioPago;
  moneda: Moneda;
  tipo_cambio: number;
  observaciones: string;
  descuento_global: number;
  items: ItemComprobanteRequest[];
}

export interface FormularioBoleta {
  cliente_id: number | null;
  serie: string;
  fecha_emision: string;
  moneda: Moneda;
  tipo_cambio: number;
  observaciones: string;
  descuento_global: number;
  items: ItemComprobanteRequest[];
}

export interface FormularioNotaCredito {
  cliente_id: number | null;
  serie: string;
  fecha_emision: string;
  codigo_motivo: CodigoMotivoNotaCredito;
  descripcion_motivo: string;
  documento_modificado_tipo: TipoComprobante;
  documento_modificado_serie: string;
  documento_modificado_numero: number;
  moneda: Moneda;
  tipo_cambio: number;
  observaciones: string;
  items: ItemComprobanteRequest[];
}

// =============================================================================
// INTERFACES PARA CONTEXTO REACT
// =============================================================================

export interface ContextoFacturacion {
  // Estado
  facturas: Factura[];
  boletas: Boleta[];
  notasCredito: NotaCredito[];
  series: SerieComprobante[];
  configuracion: ConfiguracionFacturacion | null;
  
  // Estados de carga
  cargandoFacturas: boolean;
  cargandoBoletas: boolean;
  cargandoNotasCredito: boolean;
  
  // Errores
  errorFacturas: string | null;
  errorBoletas: string | null;
  errorNotasCredito: string | null;
  
  // Acciones
  cargarFacturas: (filtros?: FiltrosFactura) => Promise<void>;
  cargarBoletas: (filtros?: FiltrosFactura) => Promise<void>;
  cargarNotasCredito: (filtros?: FiltrosFactura) => Promise<void>;
  crearFactura: (datos: CrearFacturaRequest) => Promise<Factura>;
  crearBoleta: (datos: CrearBoletaRequest) => Promise<Boleta>;
  crearNotaCredito: (datos: CrearNotaCreditoRequest) => Promise<NotaCredito>;
  enviarSunat: (id: number, tipo: 'factura' | 'boleta' | 'nota_credito') => Promise<void>;
  consultarEstado: (id: number, tipo: 'factura' | 'boleta' | 'nota_credito') => Promise<EstadoSunatResponse>;
  anularComprobante: (id: number, tipo: 'factura' | 'boleta' | 'nota_credito', motivo: string) => Promise<void>;
  
  // Utilidades
  calcularTotales: (items: ItemComprobanteRequest[], descuentoGlobal?: number) => CalculoTotalesPOS;
  validarNumeracion: (serie: string, numero: number, tipo: string) => Promise<ValidacionNumeracion>;
  limpiarCache: () => void;
}