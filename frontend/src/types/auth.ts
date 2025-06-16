/**
 * FELICITA - Types de Autenticación
 * Sistema de Facturación Electrónica para Perú
 * 
 * Interfaces y tipos TypeScript para autenticación y usuarios
 */

// ===========================================
// INTERFACES BASE USUARIO
// ===========================================

export interface Usuario {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  nombre_completo: string
  rol: UsuarioRol
  telefono?: string
  documento_identidad?: string
  empresa_id?: number
  empresa_nombre?: string
  permisos: string[]
  sucursales_info?: SucursalInfo[]
  is_active: boolean
  puede_acceder: boolean
  esta_bloqueado: boolean
  ultimo_acceso_ip?: string
  notificaciones_email: boolean
  notificaciones_sistema: boolean
  last_login?: string
  date_joined: string
}

export interface SucursalInfo {
  id: number
  codigo: string
  nombre: string
  es_principal: boolean
}

// ===========================================
// ENUMS Y TIPOS
// ===========================================

export type UsuarioRol = 
  | 'administrador'
  | 'contador' 
  | 'vendedor'
  | 'supervisor'
  | 'cliente'

export type EstadoSesion = 'activa' | 'expirada' | 'cerrada'

export type AccionAuditoria = 
  | 'LOGIN'
  | 'LOGIN_FALLIDO'
  | 'LOGOUT'
  | 'REGISTRO'
  | 'CREAR_USUARIO'
  | 'ACTUALIZAR_USUARIO'
  | 'ELIMINAR_USUARIO'
  | 'ACTIVAR_USUARIO'
  | 'DESACTIVAR_USUARIO'
  | 'DESBLOQUEAR_USUARIO'
  | 'CAMBIAR_PASSWORD'
  | 'CERRAR_SESION'
  | 'CERRAR_TODAS_SESIONES'

export type ResultadoAuditoria = 'EXITOSO' | 'FALLIDO' | 'ERROR'

// ===========================================
// INTERFACES DE REQUESTS
// ===========================================

export interface LoginRequest {
  username: string
  password: string
}

export interface RegistroRequest {
  username: string
  email: string
  first_name: string
  last_name: string
  telefono?: string
  documento_identidad?: string
  password: string
  confirmar_password: string
}

export interface CambiarPasswordRequest {
  password_actual: string
  password_nuevo: string
  confirmar_password: string
}

export interface ActualizarPerfilRequest {
  first_name?: string
  last_name?: string
  email?: string
  telefono?: string
  notificaciones_email?: boolean
  notificaciones_sistema?: boolean
}

export interface CrearUsuarioRequest {
  username: string
  email: string
  first_name: string
  last_name: string
  rol: UsuarioRol
  telefono?: string
  documento_identidad?: string
  empresa?: number
  sucursales?: number[]
  password: string
  confirmar_password: string
  is_active?: boolean
}

export interface ActualizarUsuarioRequest {
  email?: string
  first_name?: string
  last_name?: string
  rol?: UsuarioRol
  telefono?: string
  documento_identidad?: string
  empresa?: number
  sucursales?: number[]
  is_active?: boolean
  notificaciones_email?: boolean
  notificaciones_sistema?: boolean
}

// ===========================================
// INTERFACES DE RESPONSES
// ===========================================

export interface LoginResponse {
  access: string
  refresh: string
  usuario: Usuario
}

export interface RegistroResponse {
  message: string
  usuario_id: number
}

export interface RefreshTokenResponse {
  access: string
  refresh?: string
}

export interface MessageResponse {
  message: string
}

export interface ErrorResponse {
  detail?: string
  message?: string
  errors?: Record<string, string[]>
  non_field_errors?: string[]
}

// ===========================================
// INTERFACES DE SESIONES
// ===========================================

export interface SesionUsuario {
  id: number
  usuario: number
  usuario_nombre: string
  token_jti: string
  ip_address: string
  user_agent: string
  dispositivo_info: DispositivoInfo
  ubicacion?: string
  activa: boolean
  fecha_inicio: string
  fecha_expiracion: string
  ultima_actividad: string
}

export interface DispositivoInfo {
  navegador: string
  sistema: string
  dispositivo: string
}

// ===========================================
// INTERFACES DE AUDITORÍA
// ===========================================

export interface LogAuditoria {
  id: number
  usuario?: number
  usuario_nombre?: string
  accion: AccionAuditoria
  recurso: string
  ip_address?: string
  user_agent?: string
  datos_adicionales: Record<string, any>
  resultado: ResultadoAuditoria
  fecha_hora: string
}

// ===========================================
// INTERFACES DE PERMISOS
// ===========================================

export interface VerificarPermisosRequest {
  permisos: string[]
}

export interface VerificarPermisosResponse {
  usuario: string
  rol: UsuarioRol
  permisos: Record<string, boolean>
}

export interface PermisoInfo {
  codigo: string
  nombre: string
  descripcion: string
  modulo: string
}

// ===========================================
// INTERFACES DE ESTADÍSTICAS
// ===========================================

export interface EstadisticasUsuarios {
  total_usuarios: number
  usuarios_activos: number
  usuarios_inactivos: number
  usuarios_bloqueados: number
  por_rol: Record<string, number>
  sesiones_activas: number
  logins_hoy: number
  logins_esta_semana: number
}

export interface EstadisticasSesiones {
  sesiones_activas: number
  sesiones_total: number
  dispositivos_unicos: number
  ubicaciones_activas: string[]
  sesiones_por_dia: Array<{
    fecha: string
    cantidad: number
  }>
}

// ===========================================
// INTERFACES DE FILTROS
// ===========================================

export interface FiltrosUsuarios {
  search?: string
  rol?: UsuarioRol
  empresa?: number
  is_active?: boolean
  esta_bloqueado?: boolean
  ordering?: string
  page?: number
  page_size?: number
}

export interface FiltrosLogs {
  usuario?: number
  accion?: AccionAuditoria
  recurso?: string
  resultado?: ResultadoAuditoria
  fecha_desde?: string
  fecha_hasta?: string
  ip_address?: string
  ordering?: string
  page?: number
  page_size?: number
}

export interface FiltrosSesiones {
  usuario?: number
  activa?: boolean
  ip_address?: string
  fecha_desde?: string
  fecha_hasta?: string
  ordering?: string
  page?: number
  page_size?: number
}

// ===========================================
// INTERFACES DE PAGINACIÓN
// ===========================================

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface PaginationInfo {
  page: number
  pages: number
  per_page: number
  total: number
  has_next: boolean
  has_prev: boolean
}

// ===========================================
// INTERFACES DE FORMULARIOS
// ===========================================

export interface LoginFormData {
  username: string
  password: string
  remember_me?: boolean
}

export interface RegistroFormData {
  username: string
  email: string
  first_name: string
  last_name: string
  telefono: string
  documento_identidad: string
  password: string
  confirmar_password: string
  acepta_terminos: boolean
}

export interface CambiarPasswordFormData {
  password_actual: string
  password_nuevo: string
  confirmar_password: string
}

export interface PerfilFormData {
  first_name: string
  last_name: string
  email: string
  telefono: string
  notificaciones_email: boolean
  notificaciones_sistema: boolean
}

export interface UsuarioFormData {
  username: string
  email: string
  first_name: string
  last_name: string
  rol: UsuarioRol
  telefono: string
  documento_identidad: string
  empresa?: number
  sucursales: number[]
  password?: string
  confirmar_password?: string
  is_active: boolean
  notificaciones_email: boolean
  notificaciones_sistema: boolean
}

// ===========================================
// INTERFACES DE VALIDACIÓN
// ===========================================

export interface ValidationError {
  field: string
  message: string
}

export interface FormErrors {
  [key: string]: string | string[]
}

export interface ValidationResult {
  isValid: boolean
  errors: FormErrors
}

// ===========================================
// INTERFACES DE CONFIGURACIÓN
// ===========================================

export interface AuthConfig {
  loginUrl: string
  logoutUrl: string
  refreshUrl: string
  tokenKey: string
  refreshTokenKey: string
  autoRefreshEnabled: boolean
  sessionTimeout: number
  maxLoginAttempts: number
  lockoutDuration: number
}

export interface SecuritySettings {
  passwordMinLength: number
  passwordRequireNumbers: boolean
  passwordRequireSymbols: boolean
  passwordRequireUppercase: boolean
  passwordRequireLowercase: boolean
  sessionTimeoutMinutes: number
  maxConcurrentSessions: number
  requireEmailVerification: boolean
  enable2FA: boolean
}

// ===========================================
// INTERFACES DEL CONTEXTO
// ===========================================

export interface AuthContextValue {
  // Estado
  usuario: Usuario | null
  isLoading: boolean
  isAuthenticated: boolean
  
  // Acciones principales
  login: (credentials: LoginRequest) => Promise<LoginResponse>
  logout: () => Promise<void>
  refreshUser: () => Promise<Usuario>
  
  // Gestión de perfil
  updateProfile: (data: ActualizarPerfilRequest) => Promise<Usuario>
  changePassword: (data: CambiarPasswordRequest) => Promise<void>
  
  // Gestión de sesiones
  getSessions: () => Promise<SesionUsuario[]>
  closeSessions: (tokenJti?: string) => Promise<void>
  closeAllSessions: () => Promise<void>
  
  // Permisos
  hasPermission: (permission: string) => boolean
  hasRole: (roles: UsuarioRol[]) => boolean
  checkPermissions: (permissions: string[]) => Promise<Record<string, boolean>>
}

// ===========================================
// TYPES HELPER
// ===========================================

export type ApiResponse<T> = Promise<T>
export type ApiError = Error & { 
  response?: { 
    data: ErrorResponse 
    status: number 
  } 
}

export type AuthAction = 
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: Usuario | null }
  | { type: 'LOGIN_SUCCESS'; payload: Usuario }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: Partial<Usuario> }
  | { type: 'SET_ERROR'; payload: string | null }

export type AuthState = {
  usuario: Usuario | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null
}

// ===========================================
// CONSTANTS
// ===========================================

export const ROLES_LABELS: Record<UsuarioRol, string> = {
  administrador: 'Administrador',
  contador: 'Contador',
  vendedor: 'Vendedor',
  supervisor: 'Supervisor',
  cliente: 'Cliente'
}

export const ACCIONES_AUDITORIA_LABELS: Record<AccionAuditoria, string> = {
  LOGIN: 'Inicio de sesión',
  LOGIN_FALLIDO: 'Intento de login fallido',
  LOGOUT: 'Cierre de sesión',
  REGISTRO: 'Registro de usuario',
  CREAR_USUARIO: 'Crear usuario',
  ACTUALIZAR_USUARIO: 'Actualizar usuario',
  ELIMINAR_USUARIO: 'Eliminar usuario',
  ACTIVAR_USUARIO: 'Activar usuario',
  DESACTIVAR_USUARIO: 'Desactivar usuario',
  DESBLOQUEAR_USUARIO: 'Desbloquear usuario',
  CAMBIAR_PASSWORD: 'Cambiar contraseña',
  CERRAR_SESION: 'Cerrar sesión específica',
  CERRAR_TODAS_SESIONES: 'Cerrar todas las sesiones'
}

export const PERMISOS_POR_ROL: Record<UsuarioRol, string[]> = {
  administrador: ['*'],
  contador: [
    'core.view_empresa',
    'core.view_sucursal', 
    'core.view_cliente',
    'facturacion.*',
    'inventario.view_*',
    'contabilidad.*',
    'reportes.*'
  ],
  vendedor: [
    'core.view_cliente',
    'core.add_cliente',
    'facturacion.view_factura',
    'facturacion.add_factura',
    'punto_venta.*'
  ],
  supervisor: [
    'core.view_*',
    'usuarios.view_usuario',
    'facturacion.*',
    'inventario.view_*',
    'punto_venta.*',
    'reportes.view_reporte'
  ],
  cliente: [
    'facturacion.view_own_factura',
    'reportes.view_own_reporte'
  ]
}

// ===========================================
// UTILIDADES DE TIPO
// ===========================================

export type PickOptional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequireFields<T, K extends keyof T> = T & Required<Pick<T, K>>
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}