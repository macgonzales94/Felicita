import { Navigate } from 'react-router-dom'
import { useAuth } from '../../contextos/AuthContext'
import Cargando from './Cargando'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { usuario, isLoading } = useAuth()

  if (isLoading) {
    return <Cargando />
  }

  if (!usuario) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
