/**
 * API SERVICE - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Cliente HTTP para comunicación con el backend Django
 */

import axios, { 
  AxiosInstance, 
  AxiosRequestConfig, 
  AxiosResponse, 
  AxiosError 
} from 'axios'
import { toast } from 'react-hot-toast'

// Tipos
import type {
  ApiResponse,
  PaginatedResponse,
  LoginCredentials,
  LoginResponse,
  Usuario,
  Cliente,
  Proveedor,
  Producto,
  Factura,
  Empresa,
  CambiarPasswordData,
  PaginationParams,
  ClienteFilters,
  ProductoFilters,
  FacturaFilters
} from '../types'

// =============================================================================
// CONFIGURACIÓN BASE
// =============================================================================

/** URL base de la API */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

/** Timeout por defecto */
const DEFAULT_TIMEOUT = 30000

/** Clave para el token en localStorage */
const TOKEN_STORAGE_KEY = 'felicita_token'
const REFRESH_TOKEN_STORAGE_KEY = 'felicita_refresh_token'

// =============================================================================
// CONFIGURACIÓN DE AXIOS
// =============================================================================

/** Instancia principal de Axios */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: DEFAULT_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// =============================================================================
// GESTIÓN DE TOKENS
// =============================================================================

/** Obtener token de acceso del storage */
const getAccessToken = (): string | null => {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY)
  } catch {
    return null
  }
}

/** Obtener token de refresh del storage */
const getRefreshToken = (): string | null => {
  try {
    return localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY)
  } catch {
    return null
  }
}

/** Guardar tokens en storage */
const saveTokens = (accessToken: string, refreshToken: string): void => {
  try {
    localStorage.setItem(TOKEN_STORAGE_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, refreshToken)
  } catch (error) {
    console.error('Error guardando tokens:', error)
  }
}

/** Limpiar tokens del storage */
const clearTokens = (): void => {
  try {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
  } catch (error) {
    console.error('Error limpiando tokens:', error)
  }
}

/** Verificar si el token está expirado */
const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const exp = payload.exp * 1000 // Convertir a millisegundos
    return Date.now() >= exp
  } catch {
    return true
  }
}

// =============================================================================
// INTERCEPTORES DE REQUEST
// =============================================================================

/** Interceptor para agregar token de autorización */
apiClient.interceptors.request.use(
  (config) => {
    const token = getAccessToken()
    
    if (token && !isTokenExpired(token)) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Log de request en desarrollo
    if (import.meta.env.DEV) {
      console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    }
    
    return config
  },
  (error) => {
    console.error('Error en request interceptor:', error)
    return Promise.reject(error)
  }
)

// =============================================================================
// INTERCEPTORES DE RESPONSE
// =============================================================================

/** Flag para evitar bucles infinitos de refresh */
let isRefreshing = false
let failedQueue: any[] = []

/** Procesar cola de requests fallidos */
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  
  failedQueue = []
}

/** Interceptor para manejar responses y errores */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log de response exitoso en desarrollo
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    }
    
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any
    
    // Log de error en desarrollo
    if (import.meta.env.DEV) {
      console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error)
    }
    
    // Manejar error 401 (No autorizado)
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Si ya se está refrescando, agregar a la cola
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return apiClient(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      const refreshToken = getRefreshToken()
      
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/usuarios/refresh/`, {
            refresh: refreshToken
          })
          
          const { access } = response.data
          saveTokens(access, refreshToken)
          
          // Actualizar header del request original
          originalRequest.headers.Authorization = `Bearer ${access}`
          
          // Procesar cola de requests
          processQueue(null, access)
          
          return apiClient(originalRequest)
        } catch (refreshError) {
          // Error al refrescar token, limpiar storage y redireccionar
          processQueue(refreshError, null)
          clearTokens()
          
          // Redireccionar a login
          if (typeof window !== 'undefined') {
            window.location.href = '/login'
          }
          
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      } else {
        // No hay refresh token, limpiar y redireccionar
        clearTokens()
        
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
      }
    }
    
    // Manejar otros errores HTTP
    handleApiError(error)
    
    return Promise.reject(error)
  }
)

// =============================================================================
// MANEJO DE ERRORES
// =============================================================================

/** Manejar errores de la API */
const handleApiError = (error: AxiosError): void => {
  const status = error.response?.status
  const data = error.response?.data as any
  
  switch (status) {
    case 400:
      if (data?.errors) {
        // Errores de validación
        Object.values(data.errors).flat().forEach((msg: any) => {
          toast.error(msg)
        })
      } else {
        toast.error(data?.message || 'Datos inválidos')
      }
      break
      
    case 403:
      toast.error('No tienes permisos para realizar esta acción')
      break
      
    case 404:
      toast.error('Recurso no encontrado')
      break
      
    case 409:
      toast.error('El recurso ya existe o hay un conflicto')
      break
      
    case 422:
      toast.error('Datos de entrada inválidos')
      break
      
    case 429:
      toast.error('Demasiadas peticiones. Intenta más tarde')
      break
      
    case 500:
      toast.error('Error interno del servidor')
      break
      
    case 502:
    case 503:
    case 504:
      toast.error('Servicio no disponible temporalmente')
      break
      
    default:
      if (!navigator.onLine) {
        toast.error('Sin conexión a internet')
      } else {
        toast.error('Error de conexión')
      }
  }
}

// =============================================================================
// FUNCIONES AUXILIARES
// =============================================================================

/** Construir parámetros de query string */
const buildQueryParams = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams()
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value))
    }
  })
  
  return searchParams.toString()
}

/** Realizar petición GET */
const get = async <T>(url: string, params?: Record<string, any>): Promise<T> => {
  const queryString = params ? buildQueryParams(params) : ''
  const fullUrl = queryString ? `${url}?${queryString}` : url
  
  const response = await apiClient.get<T>(fullUrl)
  return response.data
}

/** Realizar petición POST */
const post = async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  const response = await apiClient.post<T>(url, data, config)
  return response.data
}

/** Realizar petición PUT */
const put = async <T>(url: string, data?: any): Promise<T> => {
  const response = await apiClient.put<T>(url, data)
  return response.data
}

/** Realizar petición PATCH */
const patch = async <T>(url: string, data?: any): Promise<T> => {
  const response = await apiClient.patch<T>(url, data)
  return response.data
}

/** Realizar petición DELETE */
const del = async <T>(url: string): Promise<T> => {
  const response = await apiClient.delete<T>(url)
  return response.data
}

// =============================================================================
// SERVICIOS DE AUTENTICACIÓN
// =============================================================================

export const authService = {
  /** Iniciar sesión */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await post<LoginResponse>('/usuarios/login/', credentials)
    
    // Guardar tokens
    saveTokens(response.access, response.refresh)
    
    toast.success('¡Bienvenido a FELICITA!')
    
    return response
  },
  
  /** Cerrar sesión */
  async logout(): Promise<void> {
    const refreshToken = getRefreshToken()
    
    try {
      if (refreshToken) {
        await post('/usuarios/logout/', { refresh: refreshToken })
      }
    } catch (error) {
      console.error('Error al cerrar sesión:', error)
    } finally {
      clearTokens()
      toast.success('Sesión cerrada correctamente')
    }
  },
  
  /** Obtener perfil del usuario */
  async getProfile(): Promise<Usuario> {
    return get<Usuario>('/usuarios/profile/')
  },
  
  /** Actualizar perfil */
  async updateProfile(data: Partial<Usuario>): Promise<Usuario> {
    const response = await put<Usuario>('/usuarios/profile/update/', data)
    toast.success('Perfil actualizado correctamente')
    return response
  },
  
  /** Cambiar contraseña */
  async changePassword(data: CambiarPasswordData): Promise<void> {
    await post('/usuarios/change-password/', data)
    toast.success('Contraseña cambiada correctamente')
  },
  
  /** Validar token actual */
  async validateToken(): Promise<{ valid: boolean; user: Usuario }> {
    return get('/usuarios/validate-token/')
  }
}

// =============================================================================
// SERVICIOS DE CLIENTES
// =============================================================================

export const clientesService = {
  /** Obtener lista de clientes */
  async getClientes(params?: ClienteFilters & PaginationParams): Promise<PaginatedResponse<Cliente>> {
    return get('/core/clientes/', params)
  },
  
  /** Obtener cliente por ID */
  async getCliente(id: string): Promise<Cliente> {
    return get(`/core/clientes/${id}/`)
  },
  
  /** Crear cliente */
  async createCliente(data: Partial<Cliente>): Promise<Cliente> {
    const response = await post<Cliente>('/core/clientes/', data)
    toast.success('Cliente creado correctamente')
    return response
  },
  
  /** Actualizar cliente */
  async updateCliente(id: string, data: Partial<Cliente>): Promise<Cliente> {
    const response = await put<Cliente>(`/core/clientes/${id}/`, data)
    toast.success('Cliente actualizado correctamente')
    return response
  },
  
  /** Eliminar cliente */
  async deleteCliente(id: string): Promise<void> {
    await del(`/core/clientes/${id}/`)
    toast.success('Cliente eliminado correctamente')
  },
  
  /** Buscar cliente por documento */
  async buscarPorDocumento(numero_documento: string): Promise<Cliente[]> {
    return get('/core/clientes/', { numero_documento })
  }
}

// =============================================================================
// SERVICIOS DE PRODUCTOS
// =============================================================================

export const productosService = {
  /** Obtener lista de productos */
  async getProductos(params?: ProductoFilters & PaginationParams): Promise<PaginatedResponse<Producto>> {
    return get('/core/productos/', params)
  },
  
  /** Obtener producto por ID */
  async getProducto(id: string): Promise<Producto> {
    return get(`/core/productos/${id}/`)
  },
  
  /** Crear producto */
  async createProducto(data: Partial<Producto>): Promise<Producto> {
    const response = await post<Producto>('/core/productos/', data)
    toast.success('Producto creado correctamente')
    return response
  },
  
  /** Actualizar producto */
  async updateProducto(id: string, data: Partial<Producto>): Promise<Producto> {
    const response = await put<Producto>(`/core/productos/${id}/`, data)
    toast.success('Producto actualizado correctamente')
    return response
  },
  
  /** Eliminar producto */
  async deleteProducto(id: string): Promise<void> {
    await del(`/core/productos/${id}/`)
    toast.success('Producto eliminado correctamente')
  },
  
  /** Buscar productos por código o nombre */
  async buscarProductos(query: string): Promise<Producto[]> {
    const response = await get<PaginatedResponse<Producto>>('/core/productos/', { 
      search: query,
      per_page: 20 
    })
    return response.results
  }
}

// =============================================================================
// SERVICIOS DE PROVEEDORES
// =============================================================================

export const proveedoresService = {
  /** Obtener lista de proveedores */
  async getProveedores(params?: PaginationParams): Promise<PaginatedResponse<Proveedor>> {
    return get('/core/proveedores/', params)
  },
  
  /** Obtener proveedor por ID */
  async getProveedor(id: string): Promise<Proveedor> {
    return get(`/core/proveedores/${id}/`)
  },
  
  /** Crear proveedor */
  async createProveedor(data: Partial<Proveedor>): Promise<Proveedor> {
    const response = await post<Proveedor>('/core/proveedores/', data)
    toast.success('Proveedor creado correctamente')
    return response
  },
  
  /** Actualizar proveedor */
  async updateProveedor(id: string, data: Partial<Proveedor>): Promise<Proveedor> {
    const response = await put<Proveedor>(`/core/proveedores/${id}/`, data)
    toast.success('Proveedor actualizado correctamente')
    return response
  },
  
  /** Eliminar proveedor */
  async deleteProveedor(id: string): Promise<void> {
    await del(`/core/proveedores/${id}/`)
    toast.success('Proveedor eliminado correctamente')
  }
}

// =============================================================================
// SERVICIOS DE FACTURACIÓN
// =============================================================================

export const facturacionService = {
  /** Obtener lista de facturas */
  async getFacturas(params?: FacturaFilters & PaginationParams): Promise<PaginatedResponse<Factura>> {
    return get('/facturacion/facturas/', params)
  },
  
  /** Obtener factura por ID */
  async getFactura(id: string): Promise<Factura> {
    return get(`/facturacion/facturas/${id}/`)
  },
  
  /** Crear factura */
  async createFactura(data: Partial<Factura>): Promise<Factura> {
    const response = await post<Factura>('/facturacion/facturas/', data)
    toast.success('Factura creada correctamente')
    return response
  },
  
  /** Actualizar factura */
  async updateFactura(id: string, data: Partial<Factura>): Promise<Factura> {
    const response = await put<Factura>(`/facturacion/facturas/${id}/`, data)
    toast.success('Factura actualizada correctamente')
    return response
  },
  
  /** Enviar factura a SUNAT */
  async enviarSunat(id: string): Promise<void> {
    await post(`/facturacion/facturas/${id}/enviar-sunat/`)
    toast.success('Factura enviada a SUNAT')
  },
  
  /** Descargar PDF */
  async descargarPdf(id: string): Promise<Blob> {
    const response = await apiClient.get(`/facturacion/facturas/${id}/pdf/`, {
      responseType: 'blob'
    })
    return response.data
  }
}

// =============================================================================
// SERVICIOS DE EMPRESA
// =============================================================================

export const empresaService = {
  /** Obtener datos de la empresa */
  async getEmpresa(): Promise<Empresa> {
    return get('/core/empresa/')
  },
  
  /** Actualizar datos de la empresa */
  async updateEmpresa(data: Partial<Empresa>): Promise<Empresa> {
    const response = await put<Empresa>('/core/empresa/', data)
    toast.success('Datos de empresa actualizados')
    return response
  }
}

// =============================================================================
// SERVICIOS DE REPORTES
// =============================================================================

export const reportesService = {
  /** Generar reporte de ventas */
  async reporteVentas(params: {
    fecha_desde: string
    fecha_hasta: string
    formato: 'PDF' | 'EXCEL'
  }): Promise<Blob> {
    const response = await apiClient.post('/reportes/ventas/', params, {
      responseType: 'blob'
    })
    return response.data
  },
  
  /** Dashboard de estadísticas */
  async getDashboardStats(): Promise<any> {
    return get('/reportes/dashboard/')
  }
}

// =============================================================================
// UTILIDADES ADICIONALES
// =============================================================================

/** Verificar conectividad con la API */
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    await get('/health/')
    return true
  } catch {
    return false
  }
}

/** Subir archivo */
export const uploadFile = async (file: File, endpoint: string): Promise<any> => {
  const formData = new FormData()
  formData.append('file', file)
  
  return post(endpoint, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// =============================================================================
// EXPORTACIÓN PRINCIPAL
// =============================================================================

const api = {
  // Servicios principales
  auth: authService,
  clientes: clientesService,
  productos: productosService,
  proveedores: proveedoresService,
  facturacion: facturacionService,
  empresa: empresaService,
  reportes: reportesService,
  
  // Métodos HTTP básicos
  get,
  post,
  put,
  patch,
  delete: del,
  
  // Utilidades
  checkHealth: checkApiHealth,
  uploadFile,
  
  // Gestión de tokens
  getAccessToken,
  clearTokens,
  saveTokens
}

export default api