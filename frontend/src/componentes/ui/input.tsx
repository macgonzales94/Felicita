/**
 * CONSTANTES DEL SISTEMA - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Valores constantes para configuración y operación del sistema
 */

// =============================================================================
// CONSTANTES DE APLICACIÓN
// =============================================================================

export const APP_CONFIG = {
  // Información básica
  NOMBRE: 'FELICITA',
  DESCRIPCION: 'Sistema de Facturación Electrónica para Perú',
  VERSION: '1.0.0',
  EMPRESA: 'FELICITA Development Team',
  
  // URLs y endpoints
  BASE_URL: import.meta.env.VITE_APP_URL || 'http://localhost:3000',
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  NUBEFACT_URL: import.meta.env.VITE_NUBEFACT_URL || 'https://api.nubefact.com',
  
  // Configuración de autenticación
  JWT_EXPIRE_TIME: 24 * 60 * 60 * 1000, // 24 horas
  REFRESH_THRESHOLD: 5 * 60 * 1000, // 5 minutos antes de expirar
  SESSION_STORAGE_KEY: 'felicita_session',
  
  // Límites del sistema
  MAX_UPLOAD_SIZE: 10 * 1024 * 1024, // 10MB
  MAX_ITEMS_PER_PAGE: 100,
  DEFAULT_PAGE_SIZE: 20,
  
  // Configuración de UX
  DEBOUNCE_DELAY: 300, // ms para búsquedas
  TOAST_DURATION: 4000, // ms para notificaciones
  LOADING_DELAY: 200, // ms antes de mostrar loading
} as const

// =============================================================================
// CONSTANTES DE FACTURACIÓN PERUANA
// =============================================================================

export const SUNAT_CONFIG = {
  // Tipos de comprobante según SUNAT
  TIPOS_COMPROBANTE: {
    FACTURA: '01',
    BOLETA: '03',
    NOTA_CREDITO: '07',
    NOTA_DEBITO: '08',
    GUIA_REMISION: '09',
    COMPROBANTE_RETENCION: '20',
    COMPROBANTE_PERCEPCION: '40'
  },
  
  // Series válidas por tipo de comprobante
  SERIES_VALIDAS: {
    FACTURA: ['F001', 'F002', 'F003', 'F004', 'F005'],
    BOLETA: ['B001', 'B002', 'B003', 'B004', 'B005'],
    NOTA_CREDITO: ['FC01', 'BC01'],
    NOTA_DEBITO: ['FD01', 'BD01']
  },
  
  // Estados de documentos en SUNAT
  ESTADOS_SUNAT: {
    PENDIENTE: 'PENDIENTE',
    ACEPTADO: 'ACEPTADO',
    RECHAZADO: 'RECHAZADO',
    ANULADO: 'ANULADO',
    BAJA_PENDIENTE: 'BAJA_PENDIENTE'
  },
  
  // Códigos de motivo para notas de crédito
  MOTIVOS_NOTA_CREDITO: {
    ANULACION_OPERACION: '01',
    ANULACION_ERROR_RUC: '02',
    CORRECCION_ERROR_DESCRIPCION: '03',
    DESCUENTO_GLOBAL: '04',
    DESCUENTO_ITEM: '05',
    DEVOLUCION_TOTAL: '06',
    DEVOLUCION_ITEM: '07',
    BONIFICACION: '08',
    DISMINUCION_VALOR: '09',
    OTROS_CONCEPTOS: '10'
  },
  
  // Códigos de motivo para notas de débito
  MOTIVOS_NOTA_DEBITO: {
    INTERES_MORA: '01',
    AUMENTO_VALOR: '02',
    MAYOR_VALOR: '03',
    OTROS_CONCEPTOS: '10'
  },
  
  // Tasas de impuestos
  TASAS_IMPUESTO: {
    IGV: 0.18, // 18%
    ISC: 0.17, // Variable según producto
    PERCEPCION_VENTA_INTERNA: 0.02, // 2%
    RETENCION_RENTA: 0.08 // 8%
  },
  
  // Límites para facturación
  LIMITES: {
    MONTO_MAXIMO_BOLETA_SIN_DOCUMENTO: 700, // S/ 700
    MONTO_MAXIMO_BOLETA_CON_DOCUMENTO: 20000, // S/ 20,000
    CARACTERES_DESCRIPCION: 250,
    ITEMS_POR_COMPROBANTE: 200
  }
} as const

// =============================================================================
// CONSTANTES DE DOCUMENTOS DE IDENTIDAD
// =============================================================================

export const DOCUMENTOS_IDENTIDAD = {
  // Tipos de documento
  TIPOS: {
    DNI: 'DNI',
    RUC: 'RUC',
    CARNET_EXTRANJERIA: 'CARNET_EXTRANJERIA',
    PASAPORTE: 'PASAPORTE'
  },
  
  // Longitudes válidas
  LONGITUDES: {
    DNI: 8,
    RUC: 11,
    CARNET_EXTRANJERIA: 9,
    PASAPORTE: { min: 6, max: 9 }
  },
  
  // Patrones de validación
  PATRONES: {
    DNI: /^\d{8}$/,
    RUC: /^\d{11}$/,
    CARNET_EXTRANJERIA: /^\d{9}$/,
    PASAPORTE: /^[A-Z0-9]{6,9}$/
  },
  
  // Descripciones
  DESCRIPCIONES: {
    DNI: 'Documento Nacional de Identidad',
    RUC: 'Registro Único de Contribuyentes',
    CARNET_EXTRANJERIA: 'Carnet de Extranjería',
    PASAPORTE: 'Pasaporte'
  }
} as const

// =============================================================================
// CONSTANTES DE MONEDAS
// =============================================================================

export const MONEDAS = {
  // Códigos ISO
  PEN: 'PEN', // Sol peruano
  USD: 'USD', // Dólar estadounidense  
  EUR: 'EUR', // Euro
  
  // Símbolos
  SIMBOLOS: {
    PEN: 'S/',
    USD: '$',
    EUR: '€'
  },
  
  // Nombres
  NOMBRES: {
    PEN: 'Sol Peruano',
    USD: 'Dólar Estadounidense',
    EUR: 'Euro'
  },
  
  // Decimales
  DECIMALES: {
    PEN: 2,
    USD: 2,
    EUR: 2
  },
  
  // Moneda por defecto
  DEFAULT: 'PEN'
} as const

// =============================================================================
// CONSTANTES DE MÉTODOS DE PAGO
// =============================================================================

export const METODOS_PAGO = {
  // Tipos
  EFECTIVO: 'EFECTIVO',
  TRANSFERENCIA: 'TRANSFERENCIA',
  TARJETA_CREDITO: 'TARJETA_CREDITO',
  TARJETA_DEBITO: 'TARJETA_DEBITO',
  CHEQUE: 'CHEQUE',
  DEPOSITO: 'DEPOSITO',
  
  // Descripciones
  DESCRIPCIONES: {
    EFECTIVO: 'Efectivo',
    TRANSFERENCIA: 'Transferencia Bancaria',
    TARJETA_CREDITO: 'Tarjeta de Crédito',
    TARJETA_DEBITO: 'Tarjeta de Débito',
    CHEQUE: 'Cheque',
    DEPOSITO: 'Depósito Bancario'
  },
  
  // Iconos (clases de iconos o SVGs)
  ICONOS: {
    EFECTIVO: 'cash-icon',
    TRANSFERENCIA: 'transfer-icon',
    TARJETA_CREDITO: 'credit-card-icon',
    TARJETA_DEBITO: 'debit-card-icon',
    CHEQUE: 'check-icon',
    DEPOSITO: 'deposit-icon'
  }
} as const

// =============================================================================
// CONSTANTES DE CONDICIONES DE PAGO
// =============================================================================

export const CONDICIONES_PAGO = {
  // Tipos
  CONTADO: 'CONTADO',
  CREDITO_15: 'CREDITO_15',
  CREDITO_30: 'CREDITO_30',
  CREDITO_45: 'CREDITO_45',
  CREDITO_60: 'CREDITO_60',
  CREDITO_90: 'CREDITO_90',
  CREDITO_120: 'CREDITO_120',
  
  // Descripciones
  DESCRIPCIONES: {
    CONTADO: 'Al contado',
    CREDITO_15: 'Crédito a 15 días',
    CREDITO_30: 'Crédito a 30 días',
    CREDITO_45: 'Crédito a 45 días',
    CREDITO_60: 'Crédito a 60 días',
    CREDITO_90: 'Crédito a 90 días',
    CREDITO_120: 'Crédito a 120 días'
  },
  
  // Días de crédito
  DIAS: {
    CONTADO: 0,
    CREDITO_15: 15,
    CREDITO_30: 30,
    CREDITO_45: 45,
    CREDITO_60: 60,
    CREDITO_90: 90,
    CREDITO_120: 120
  }
} as const

// =============================================================================
// CONSTANTES DE UNIDADES DE MEDIDA
// =============================================================================

export const UNIDADES_MEDIDA = {
  // Códigos SUNAT
  NIU: 'NIU', // Unidad (pieza)
  KGM: 'KGM', // Kilogramo
  LTR: 'LTR', // Litro
  MTR: 'MTR', // Metro
  MTK: 'MTK', // Metro cuadrado
  MTQ: 'MTQ', // Metro cúbico
  MIL: 'MIL', // Millar
  CEN: 'CEN', // Ciento
  DOC: 'DOC', // Docena
  PAR: 'PAR', // Par
  SET: 'SET', // Juego/Set
  
  // Descripciones
  DESCRIPCIONES: {
    NIU: 'Unidad (pieza)',
    KGM: 'Kilogramo',
    LTR: 'Litro',
    MTR: 'Metro',
    MTK: 'Metro cuadrado',
    MTQ: 'Metro cúbico',
    MIL: 'Millar',
    CEN: 'Ciento',
    DOC: 'Docena',
    PAR: 'Par',
    SET: 'Juego/Set'
  },
  
  // Unidad por defecto
  DEFAULT: 'NIU'
} as const

// =============================================================================
// CONSTANTES DE ESTADOS DEL SISTEMA
// =============================================================================

export const ESTADOS_SISTEMA = {
  // Estados de carga
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
  IDLE: 'idle',
  
  // Estados de formularios
  PRISTINE: 'pristine',
  DIRTY: 'dirty',
  SUBMITTING: 'submitting',
  SUBMITTED: 'submitted',
  VALIDATING: 'validating',
  
  // Estados de conexión
  ONLINE: 'online',
  OFFLINE: 'offline',
  RECONNECTING: 'reconnecting'
} as const

// =============================================================================
// CONSTANTES DE ROLES Y PERMISOS
// =============================================================================

export const ROLES_SISTEMA = {
  // Roles principales
  SUPER_ADMIN: 'SUPER_ADMIN',
  ADMINISTRADOR: 'ADMINISTRADOR',
  CONTADOR: 'CONTADOR',
  VENDEDOR: 'VENDEDOR',
  CLIENTE: 'CLIENTE',
  
  // Descripciones
  DESCRIPCIONES: {
    SUPER_ADMIN: 'Super Administrador',
    ADMINISTRADOR: 'Administrador',
    CONTADOR: 'Contador',
    VENDEDOR: 'Vendedor',
    CLIENTE: 'Cliente'
  },
  
  // Niveles de acceso
  NIVELES: {
    SUPER_ADMIN: 100,
    ADMINISTRADOR: 80,
    CONTADOR: 60,
    VENDEDOR: 40,
    CLIENTE: 20
  }
} as const

export const PERMISOS_SISTEMA = {
  // Módulos
  MODULOS: {
    DASHBOARD: 'dashboard',
    FACTURACION: 'facturacion',
    INVENTARIO: 'inventario',
    CLIENTES: 'clientes',
    REPORTES: 'reportes',
    CONFIGURACION: 'configuracion',
    USUARIOS: 'usuarios'
  },
  
  // Acciones
  ACCIONES: {
    VER: 'ver',
    CREAR: 'crear',
    EDITAR: 'editar',
    ELIMINAR: 'eliminar',
    EXPORTAR: 'exportar',
    APROBAR: 'aprobar',
    ANULAR: 'anular'
  }
} as const

// =============================================================================
// CONSTANTES DE CONFIGURACIÓN UI
// =============================================================================

export const UI_CONFIG = {
  // Breakpoints responsive
  BREAKPOINTS: {
    mobile: '640px',
    tablet: '768px',
    laptop: '1024px',
    desktop: '1280px'
  },
  
  // Tamaños de componentes
  SIZES: {
    xs: 'xs',
    sm: 'sm',
    md: 'md',
    lg: 'lg',
    xl: 'xl'
  },
  
  // Variantes de color
  VARIANTS: {
    default: 'default',
    primary: 'primary',
    secondary: 'secondary',
    success: 'success',
    warning: 'warning',
    error: 'error',
    info: 'info'
  },
  
  // Animaciones
  ANIMATIONS: {
    DURATION: {
      fast: 150,
      normal: 300,
      slow: 500
    },
    EASING: {
      ease: 'ease',
      easeIn: 'ease-in',
      easeOut: 'ease-out',
      easeInOut: 'ease-in-out'
    }
  }
} as const

// =============================================================================
// CONSTANTES DE VALIDACIÓN
// =============================================================================

export const VALIDATION_CONFIG = {
  // Límites de texto
  TEXT_LIMITS: {
    nombre: { min: 2, max: 100 },
    descripcion: { min: 5, max: 500 },
    observaciones: { min: 0, max: 1000 },
    email: { min: 5, max: 254 },
    telefono: { min: 7, max: 15 },
    direccion: { min: 10, max: 200 }
  },
  
  // Límites numéricos
  NUMERIC_LIMITS: {
    cantidad: { min: 0.01, max: 999999.99 },
    precio: { min: 0.01, max: 999999.99 },
    descuento: { min: 0, max: 100 },
    stock: { min: 0, max: 999999 }
  },
  
  // Patrones comunes
  PATTERNS: {
    email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    telefono: /^[+]?[\d\s\-\(\)]{7,15}$/,
    decimal: /^\d+(\.\d{1,2})?$/,
    entero: /^\d+$/,
    codigo: /^[A-Z0-9\-_]{3,20}$/
  }
} as const

// =============================================================================
// CONSTANTES DE ALMACENAMIENTO LOCAL
// =============================================================================

export const STORAGE_KEYS = {
  // Autenticación
  AUTH_TOKEN: 'felicita_auth_token',
  REFRESH_TOKEN: 'felicita_refresh_token',
  USER_DATA: 'felicita_user_data',
  
  // Configuración de usuario
  USER_PREFERENCES: 'felicita_user_preferences',
  THEME: 'felicita_theme',
  LANGUAGE: 'felicita_language',
  
  // Cache temporal
  PRODUCTOS_CACHE: 'felicita_productos_cache',
  CLIENTES_CACHE: 'felicita_clientes_cache',
  CARRITO_TEMP: 'felicita_carrito_temp',
  
  // Configuración POS
  POS_CONFIG: 'felicita_pos_config',
  ULTIMA_SERIE_USADA: 'felicita_ultima_serie'
} as const

// =============================================================================
// EXPORTACIÓN AGRUPADA
// =============================================================================

export const CONSTANTES = {
  APP: APP_CONFIG,
  SUNAT: SUNAT_CONFIG,
  DOCUMENTOS: DOCUMENTOS_IDENTIDAD,
  MONEDAS,
  METODOS_PAGO,
  CONDICIONES_PAGO,
  UNIDADES_MEDIDA,
  ESTADOS: ESTADOS_SISTEMA,
  ROLES: ROLES_SISTEMA,
  PERMISOS: PERMISOS_SISTEMA,
  UI: UI_CONFIG,
  VALIDATION: VALIDATION_CONFIG,
  STORAGE: STORAGE_KEYS
} as const

export default CONSTANTES