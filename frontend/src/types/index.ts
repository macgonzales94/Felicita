/**
 * TYPES INDEX - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Definiciones de tipos TypeScript para toda la aplicación
 */

// =============================================================================
// TIPOS BÁSICOS DEL SISTEMA
// =============================================================================

/** ID único del sistema */
export type ID = string

/** Formato de fecha ISO */
export type Fecha = string

/** Moneda en formato decimal */
export type Moneda = number

/** Estado general de registros */
export type EstadoRegistro = 'ACTIVO' | 'INACTIVO'

/** Respuesta estándar de la API */
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  errors?: Record<string, string[]>
  meta?: {
    total?: number
    page?: number
    per_page?: number
    total_pages?: number
  }
}

/** Parámetros de paginación */
export interface PaginationParams {
  page?: number
  per_page?: number
  search?: string
  ordering?: string
}

/** Información de paginación */
export interface PaginationInfo {
  count: number
  next: string | null
  previous: string | null
  total_pages: number
  current_page: number
}

/** Respuesta paginada */
export interface PaginatedResponse<T> {
  results: T[]
  pagination: PaginationInfo
}

// =============================================================================
// TIPOS DE AUTENTICACIÓN
// =============================================================================

/** Datos del usuario autenticado */
export interface Usuario {
  id: ID
  email: string
  nombres: string
  apellido_paterno: string
  apellido_materno: string
  tipo_documento: TipoDocumento
  numero_documento: string
  telefono?: string
  cargo?: string
  departamento?: string
  fecha_ingreso: Fecha
  foto_perfil?: string
  is_active: boolean
  fecha_ultimo_login?: Fecha
  requiere_cambio_password: boolean
  empresa: Empresa
  roles: Rol[]
  permisos: string[]
}

/** Credenciales de login */
export interface LoginCredentials {
  email: string
  password: string
}

/** Respuesta de login exitoso */
export interface LoginResponse {
  access: string
  refresh: string
  user: Usuario
  session_id: string
  requires_password_change: boolean
}

/** Datos para cambiar contraseña */
export interface CambiarPasswordData {
  password_actual: string
  password_nueva: string
  confirmar_password: string
}

/** Token de acceso */
export interface TokenInfo {
  access: string
  refresh: string
  expires_in: number
}

// =============================================================================
// TIPOS DE DOCUMENTOS
// =============================================================================

/** Tipos de documento de identidad */
export type TipoDocumento = 'DNI' | 'RUC' | 'CARNET_EXTRANJERIA' | 'PASAPORTE'

/** Géneros */
export type Genero = 'MASCULINO' | 'FEMENINO' | 'OTRO'

// =============================================================================
// TIPOS DE EMPRESA
// =============================================================================

/** Datos de empresa */
export interface Empresa {
  id: ID
  ruc: string
  razon_social: string
  nombre_comercial?: string
  direccion: string
  distrito: string
  provincia: string
  departamento: string
  ubigeo: string
  telefono?: string
  email?: string
  pagina_web?: string
  estado: 'ACTIVO' | 'INACTIVO' | 'SUSPENDIDO'
  regimen_tributario: RegimenTributario
  activo: boolean
  configuracion_facturacion: any
  creado_en: Fecha
  actualizado_en: Fecha
}

/** Regímenes tributarios del Perú */
export type RegimenTributario = 'GENERAL' | 'ESPECIAL' | 'MYPE' | 'RUS'

/** Datos de sucursal */
export interface Sucursal {
  id: ID
  empresa: ID
  codigo: string
  nombre: string
  direccion: string
  distrito: string
  provincia: string
  departamento: string
  ubigeo: string
  telefono?: string
  email?: string
  es_principal: boolean
  activo: boolean
  creado_en: Fecha
  actualizado_en: Fecha
}

// =============================================================================
// TIPOS DE CLIENTES Y PROVEEDORES
// =============================================================================

/** Datos de cliente */
export interface Cliente {
  id: ID
  tipo_documento: TipoDocumento
  numero_documento: string
  nombres?: string
  apellido_paterno?: string
  apellido_materno?: string
  razon_social?: string
  nombre_comercial?: string
  email?: string
  telefono?: string
  fecha_nacimiento?: Fecha
  genero?: Genero
  direccion?: string
  distrito?: string
  provincia?: string
  departamento?: string
  ubigeo?: string
  es_empresa: boolean
  activo: boolean
  observaciones?: string
  creado_en: Fecha
  actualizado_en: Fecha
}

/** Datos de proveedor */
export interface Proveedor {
  id: ID
  tipo_documento: TipoDocumento
  numero_documento: string
  razon_social: string
  nombre_comercial?: string
  categoria?: string
  email?: string
  telefono?: string
  contacto_principal?: string
  direccion?: string
  distrito?: string
  provincia?: string
  departamento?: string
  ubigeo?: string
  dias_credito: number
  limite_credito?: Moneda
  moneda_preferida?: ID
  activo: boolean
  observaciones?: string
  creado_en: Fecha
  actualizado_en: Fecha
}

// =============================================================================
// TIPOS DE PRODUCTOS E INVENTARIO
// =============================================================================

/** Tipos de producto */
export type TipoProducto = 'BIEN' | 'SERVICIO'

/** Datos de producto */
export interface Producto {
  id: ID
  codigo: string
  nombre: string
  descripcion?: string
  categoria: Categoria
  tipo_producto: TipoProducto
  unidad_medida: UnidadMedida
  codigo_barra?: string
  precio_venta: Moneda
  precio_compra: Moneda
  stock_actual: number
  stock_minimo: number
  stock_maximo: number
  afecto_igv: boolean
  activo: boolean
  observaciones?: string
  creado_en: Fecha
  actualizado_en: Fecha
}

/** Datos de categoría */
export interface Categoria {
  id: ID
  codigo: string
  nombre: string
  descripcion?: string
  categoria_padre?: ID
  activo: boolean
  creado_en: Fecha
  actualizado_en: Fecha
}

/** Datos de unidad de medida */
export interface UnidadMedida {
  id: ID
  codigo: string
  nombre: string
  descripcion?: string
  activo: boolean
  creado_en: Fecha
  actualizado_en: Fecha
}

// =============================================================================
// TIPOS DE FACTURACIÓN
// =============================================================================

/** Tipos de documento de venta */
export type TipoDocumentoVenta = '01' | '03' | '07' | '08' // Factura, Boleta, Nota Crédito, Nota Débito

/** Estados de documento */
export type EstadoDocumento = 'BORRADOR' | 'EMITIDO' | 'ENVIADO' | 'ACEPTADO' | 'RECHAZADO' | 'ANULADO'

/** Estados SUNAT */
export type EstadoSunat = 'PENDIENTE' | 'ACEPTADO' | 'RECHAZADO' | 'BAJA_PENDIENTE' | 'ANULADO'

/** Datos de factura */
export interface Factura {
  id: ID
  empresa: ID
  sucursal: ID
  tipo_documento: TipoDocumentoVenta
  serie: string
  numero: string
  numero_completo: string
  cliente: Cliente
  fecha_emision: Fecha
  fecha_vencimiento?: Fecha
  moneda: Moneda
  tipo_cambio: number
  subtotal: Moneda
  descuento_global: Moneda
  igv: Moneda
  total: Moneda
  detalle: DetalleFactura[]
  observaciones?: string
  estado: EstadoDocumento
  estado_sunat: EstadoSunat
  hash_documento?: string
  xml_documento?: string
  pdf_documento?: string
  codigo_qr?: string
  usuario_creacion: ID
  fecha_envio_sunat?: Fecha
  respuesta_sunat?: string
  creado_en: Fecha
  actualizado_en: Fecha
}

/** Detalle de factura */
export interface DetalleFactura {
  id: ID
  factura: ID
  item: number
  producto: Producto
  descripcion: string
  cantidad: number
  precio_unitario: Moneda
  descuento: Moneda
  subtotal: Moneda
  igv: Moneda
  total: Moneda
  creado_en: Fecha
  actualizado_en: Fecha
}

// =============================================================================
// TIPOS DE CONFIGURACIÓN
// =============================================================================

/** Datos de moneda */
export interface MonedaConfig {
  id: ID
  codigo: string
  nombre: string
  simbolo: string
  activo: boolean
  creado_en: Fecha
  actualizado_en: Fecha
}

/** Tipo de cambio */
export interface TipoCambio {
  id: ID
  moneda_origen: MonedaConfig
  moneda_destino: MonedaConfig
  fecha: Fecha
  valor_compra: Moneda
  valor_venta: Moneda
  fuente: string
  creado_en: Fecha
  actualizado_en: Fecha
}

/** Configuración del sistema */
export interface ConfiguracionSistema {
  id: ID
  clave: string
  valor: string
  descripcion: string
  tipo_dato: 'STRING' | 'INTEGER' | 'DECIMAL' | 'BOOLEAN' | 'DATE' | 'JSON'
  categoria: string
  creado_en: Fecha
  actualizado_en: Fecha
}

// =============================================================================
// TIPOS DE ROLES Y PERMISOS
// =============================================================================

/** Datos de rol */
export interface Rol {
  id: ID
  nombre: string
  descripcion?: string
  nivel: number
  permisos: PermisoPersonalizado[]
  activo: boolean
  creado_en: Fecha
  actualizado_en: Fecha
}

/** Permiso personalizado */
export interface PermisoPersonalizado {
  id: ID
  nombre: string
  descripcion?: string
  modulo: string
  accion: string
  nivel: number
  activo: boolean
  creado_en: Fecha
}

// =============================================================================
// TIPOS DE SESIONES Y ACTIVIDAD
// =============================================================================

/** Sesión de usuario */
export interface SesionUsuario {
  id: ID
  usuario: ID
  token_sesion: string
  ip_address: string
  user_agent: string
  dispositivo: string
  navegador: string
  fecha_inicio: Fecha
  fecha_fin?: Fecha
  activa: boolean
}

/** Log de actividad */
export interface LogActividadUsuario {
  id: ID
  usuario: ID
  accion: string
  modulo: string
  descripcion: string
  ip_address: string
  user_agent?: string
  fecha: Fecha
}

// =============================================================================
// TIPOS DE UI Y COMPONENTES
// =============================================================================

/** Tamaños estándar */
export type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

/** Variantes de color */
export type ColorVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'

/** Estados de loading */
export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

/** Configuración de tabla */
export interface TableColumn<T = any> {
  key: keyof T | string
  label: string
  sortable?: boolean
  filterable?: boolean
  render?: (value: any, record: T) => React.ReactNode
  width?: string | number
  align?: 'left' | 'center' | 'right'
}

/** Props de paginación */
export interface PaginationProps {
  current: number
  total: number
  pageSize: number
  showSizeChanger?: boolean
  showQuickJumper?: boolean
  showTotal?: boolean
  onChange: (page: number, pageSize: number) => void
}

// =============================================================================
// TIPOS DE FILTROS
// =============================================================================

/** Filtros generales */
export interface BaseFilters {
  search?: string
  activo?: boolean
  fecha_desde?: string
  fecha_hasta?: string
  page?: number
  per_page?: number
  ordering?: string
}

/** Filtros de cliente */
export interface ClienteFilters extends BaseFilters {
  tipo_documento?: TipoDocumento
  es_empresa?: boolean
  departamento?: string
  provincia?: string
  distrito?: string
}

/** Filtros de producto */
export interface ProductoFilters extends BaseFilters {
  categoria?: ID
  tipo_producto?: TipoProducto
  precio_min?: number
  precio_max?: number
  con_stock?: boolean
  stock_bajo?: boolean
}

/** Filtros de factura */
export interface FacturaFilters extends BaseFilters {
  tipo_documento?: TipoDocumentoVenta
  estado?: EstadoDocumento
  estado_sunat?: EstadoSunat
  cliente?: ID
  fecha_emision_desde?: string
  fecha_emision_hasta?: string
  monto_min?: number
  monto_max?: number
}

// =============================================================================
// TIPOS DE FORMULARIOS
// =============================================================================

/** Estado de campo de formulario */
export interface FieldState {
  value: any
  error?: string
  touched: boolean
}

/** Estado de formulario */
export interface FormState<T = Record<string, any>> {
  values: T
  errors: Record<keyof T, string>
  touched: Record<keyof T, boolean>
  isSubmitting: boolean
  isValid: boolean
}

/** Validador de campo */
export type FieldValidator<T = any> = (value: T) => string | undefined

/** Reglas de validación */
export interface ValidationRules {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: FieldValidator
}

// =============================================================================
// TIPOS DE NOTIFICACIONES
// =============================================================================

/** Tipos de notificación */
export type NotificationType = 'success' | 'error' | 'warning' | 'info'

/** Notificación */
export interface Notification {
  id: ID
  type: NotificationType
  title: string
  message: string
  duration?: number
  persistent?: boolean
  actions?: NotificationAction[]
  createdAt: Date
}

/** Acción de notificación */
export interface NotificationAction {
  label: string
  action: () => void
  style?: 'primary' | 'secondary'
}

// =============================================================================
// TIPOS DE TEMA
// =============================================================================

/** Tema de la aplicación */
export type Theme = 'light' | 'dark' | 'system'

/** Configuración de tema */
export interface ThemeConfig {
  theme: Theme
  primaryColor: string
  fontFamily: string
  borderRadius: string
  compactMode: boolean
}

// =============================================================================
// TIPOS DE NAVEGACIÓN
// =============================================================================

/** Elemento de menú */
export interface MenuItem {
  key: string
  label: string
  icon?: React.ReactNode
  path?: string
  children?: MenuItem[]
  permission?: string
  badge?: number | string
  disabled?: boolean
}

/** Breadcrumb */
export interface BreadcrumbItem {
  label: string
  path?: string
  icon?: React.ReactNode
}

// =============================================================================
// TIPOS DE REPORTES
// =============================================================================

/** Tipos de reporte */
export type TipoReporte = 'VENTAS' | 'COMPRAS' | 'INVENTARIO' | 'FINANCIERO' | 'TRIBUTARIO'

/** Formato de reporte */
export type FormatoReporte = 'PDF' | 'EXCEL' | 'CSV'

/** Parámetros de reporte */
export interface ParametrosReporte {
  tipo: TipoReporte
  formato: FormatoReporte
  fecha_desde: string
  fecha_hasta: string
  filtros?: Record<string, any>
}

/** Reporte generado */
export interface ReporteGenerado {
  id: ID
  tipo: TipoReporte
  formato: FormatoReporte
  nombre: string
  archivo_url: string
  parametros: ParametrosReporte
  estado: 'GENERANDO' | 'COMPLETADO' | 'ERROR'
  usuario: ID
  creado_en: Fecha
  expires_at: Fecha
}

// =============================================================================
// TIPOS DE ERRORES
// =============================================================================

/** Error de la API */
export interface ApiError {
  status: number
  message: string
  details?: Record<string, any>
  timestamp: string
}

/** Error de validación */
export interface ValidationError {
  field: string
  message: string
  code: string
}

// =============================================================================
// TIPOS DE HOOKS
// =============================================================================

/** Estado de hook de datos */
export interface DataHookState<T> {
  data: T | null
  loading: boolean
  error: Error | null
  refetch: () => void
}

/** Opciones de hook de mutación */
export interface MutationOptions<TData, TVariables> {
  onSuccess?: (data: TData, variables: TVariables) => void
  onError?: (error: Error, variables: TVariables) => void
  onSettled?: (data: TData | undefined, error: Error | null, variables: TVariables) => void
}

// =============================================================================
// EXPORTACIONES ADICIONALES
// =============================================================================

/** Tipo genérico para selección */
export interface SelectOption<T = string> {
  label: string
  value: T
  disabled?: boolean
  icon?: React.ReactNode
}

/** Configuración de datatable */
export interface DataTableConfig<T> {
  columns: TableColumn<T>[]
  data: T[]
  loading?: boolean
  pagination?: PaginationProps
  selection?: {
    selectedRowKeys: string[]
    onChange: (selectedRowKeys: string[], selectedRows: T[]) => void
  }
  actions?: {
    label: string
    action: (record: T) => void
    icon?: React.ReactNode
    disabled?: (record: T) => boolean
  }[]
}

/** Configuración de filtros avanzados */
export interface AdvancedFiltersConfig {
  fields: {
    key: string
    label: string
    type: 'text' | 'select' | 'date' | 'number' | 'boolean'
    options?: SelectOption[]
    placeholder?: string
  }[]
  onApply: (filters: Record<string, any>) => void
  onReset: () => void
}

export default {}