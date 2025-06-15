
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contextos/AuthContext'
import { AppProvider } from './contextos/AppContext'
import ProtectedRoute from './componentes/comunes/ProtectedRoute'
import Layout from './componentes/comunes/Layout'
import Login from './paginas/Login'
import Dashboard from './paginas/Dashboard'
import PuntoDeVenta from './paginas/PuntoDeVenta'
import Facturacion from './paginas/Facturacion'
import Clientes from './paginas/Clientes'
import Productos from './paginas/Productos'
import Inventario from './paginas/Inventario'
import Reportes from './paginas/Reportes'
import Configuracion from './paginas/Configuracion'

function App() {
  return (
    <AuthProvider>
      <AppProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/punto-venta" element={<PuntoDeVenta />} />
                    <Route path="/facturacion" element={<Facturacion />} />
                    <Route path="/clientes" element={<Clientes />} />
                    <Route path="/productos" element={<Productos />} />
                    <Route path="/inventario" element={<Inventario />} />
                    <Route path="/reportes" element={<Reportes />} />
                    <Route path="/configuracion" element={<Configuracion />} />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AppProvider>
    </AuthProvider>
  )
}

export default App