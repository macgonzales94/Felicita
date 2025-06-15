import { useEffect, useState } from 'react'
import { DollarSign, Users, Package, FileText } from 'lucide-react'

interface KPI {
  titulo: string
  valor: string
  cambio: string
  icono: React.ComponentType<any>
  color: string
}

export default function Dashboard() {
  const [kpis] = useState<KPI[]>([
    {
      titulo: 'Ventas del Día',
      valor: 'S/ 12,450.00',
      cambio: '+8.2%',
      icono: DollarSign,
      color: 'bg-green-500'
    },
    {
      titulo: 'Clientes Activos',
      valor: '1,234',
      cambio: '+3.1%',
      icono: Users,
      color: 'bg-blue-500'
    },
    {
      titulo: 'Productos Stock Bajo',
      valor: '12',
      cambio: '-2.4%',
      icono: Package,
      color: 'bg-yellow-500'
    },
    {
      titulo: 'Facturas del Mes',
      valor: '456',
      cambio: '+12.3%',
      icono: FileText,
      color: 'bg-purple-500'
    }
  ])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Resumen de actividades del sistema</p>
      </div>

      {/* KPIs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpis.map((kpi, index) => {
          const Icon = kpi.icono
          return (
            <div key={index} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{kpi.titulo}</p>
                  <p className="text-2xl font-bold text-gray-900">{kpi.valor}</p>
                  <p className="text-sm text-green-600">{kpi.cambio}</p>
                </div>
                <div className={`p-3 rounded-full ${kpi.color}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Contenido adicional del dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Ventas Recientes</h3>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b">
                <div>
                  <p className="font-medium">Factura F001-00{i}</p>
                  <p className="text-sm text-gray-600">Cliente {i}</p>
                </div>
                <span className="text-green-600 font-medium">S/ 1,250.00</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Productos Más Vendidos</h3>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b">
                <div>
                  <p className="font-medium">Producto {i}</p>
                  <p className="text-sm text-gray-600">Código: PROD00{i}</p>
                </div>
                <span className="text-blue-600 font-medium">{i * 15} unidades</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
