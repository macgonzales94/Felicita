import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  ShoppingCart,
  FileText,
  Users,
  Package,
  BarChart3,
  Settings,
  Box,
} from 'lucide-react'

interface SidebarProps {
  isOpen: boolean
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Punto de Venta', href: '/punto-venta', icon: ShoppingCart },
  { name: 'Facturación', href: '/facturacion', icon: FileText },
  { name: 'Clientes', href: '/clientes', icon: Users },
  { name: 'Productos', href: '/productos', icon: Package },
  { name: 'Inventario', href: '/inventario', icon: Box },
  { name: 'Reportes', href: '/reportes', icon: BarChart3 },
  { name: 'Configuración', href: '/configuracion', icon: Settings },
]

export default function Sidebar({ isOpen }: SidebarProps) {
  return (
    <aside className={`fixed left-0 top-16 h-full bg-white shadow-lg transition-all duration-300 z-30 ${
      isOpen ? 'w-64' : 'w-16'
    }`}>
      <nav className="p-4 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`
              }
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {isOpen && <span className="font-medium">{item.name}</span>}
            </NavLink>
          )
        })}
      </nav>
    </aside>
  )
}