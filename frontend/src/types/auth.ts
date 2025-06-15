export interface Usuario {
  id: number
  username: string
  email: string
  nombre_completo: string
  rol: string
  empresa_id?: number
  empresa_nombre?: string
  permisos: string[]
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  usuario: Usuario
}