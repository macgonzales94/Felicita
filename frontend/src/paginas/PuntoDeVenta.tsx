/**
 * PUNTO DE VENTA - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Interfaz optimizada para ventas rápidas con integración SUNAT
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Search, ShoppingCart, Plus, Minus, Trash2, User, Calculator, CreditCard, Printer, AlertCircle, CheckCircle } from 'lucide-react';
import { useFacturacion } from '../contextos/FacturacionContext';
import { useAuth } from '../hooks/useAuth';
import { 
  ItemPOS, 
  VentaPOS, 
  MedioPago, 
  Cliente,
  Producto,
  TipoComprobante
} from '../types';
import * as facturacionService from '../servicios/facturas';

// =============================================================================
// INTERFACES Y TIPOS
// =============================================================================

interface EstadoPOS {
  clienteSeleccionado: Cliente | null;
  busquedaCliente: string;
  busquedaProducto: string;
  tipoComprobante: 'factura' | 'boleta';
  items: ItemPOS[];
  subtotal: number;
  descuentoGlobal: number;
  igv: number;
  total: number;
  medioPago: MedioPago;
  observaciones: string;
  procesandoVenta: boolean;
  ventaCompletada: boolean;
  numeroComprobante: string | null;
  errores: string[];
}

interface ResultadoBusquedaCliente {
  id: number;
  numero_documento: string;
  razon_social: string;
  tipo_documento: string;
}

interface ResultadoBusquedaProducto {
  id: number;
  codigo_producto: string;
  descripcion: string;
  precio_venta: number;
  stock_disponible: number;
  activo: boolean;
}

// =============================================================================
// COMPONENTE PRINCIPAL
// =============================================================================

const PuntoDeVenta: React.FC = () => {
  const { calcularTotales, series } = useFacturacion();
  const { usuario } = useAuth();
  
  // Referencias
  const busquedaClienteRef = useRef<HTMLInputElement>(null);
  const busquedaProductoRef = useRef<HTMLInputElement>(null);
  
  // Estado principal
  const [estado, setEstado] = useState<EstadoPOS>({
    clienteSeleccionado: null,
    busquedaCliente: '',
    busquedaProducto: '',
    tipoComprobante: 'boleta',
    items: [],
    subtotal: 0,
    descuentoGlobal: 0,
    igv: 0,
    total: 0,
    medioPago: MedioPago.EFECTIVO,
    observaciones: '',
    procesandoVenta: false,
    ventaCompletada: false,
    numeroComprobante: null,
    errores: [],
  });
  
  // Estados auxiliares
  const [clientesEncontrados, setClientesEncontrados] = useState<ResultadoBusquedaCliente[]>([]);
  const [productosEncontrados, setProductosEncontrados] = useState<ResultadoBusquedaProducto[]>([]);
  const [mostrarBusquedaClientes, setMostrarBusquedaClientes] = useState(false);
  const [mostrarBusquedaProductos, setMostrarBusquedaProductos] = useState(false);
  const [mostrarCalculadora, setMostrarCalculadora] = useState(false);

  // =============================================================================
  // EFECTOS
  // =============================================================================

  // Recalcular totales cuando cambian los items o descuento
  useEffect(() => {
    if (estado.items.length > 0) {
      const itemsParaCalculo = estado.items.map(item => ({
        producto_id: item.producto_id,
        descripcion: item.descripcion,
        cantidad: item.cantidad,
        precio_unitario: item.precio_unitario,
        descuento: item.descuento,
      }));
      
      const totales = calcularTotales(itemsParaCalculo, estado.descuentoGlobal);
      
      setEstado(prev => ({
        ...prev,
        subtotal: totales.subtotal,
        igv: totales.igv,
        total: totales.total,
        items: prev.items.map((item, index) => ({
          ...item,
          subtotal: totales.items_calculados[index].subtotal,
          igv: totales.items_calculados[index].igv,
          total: totales.items_calculados[index].total,
        })),
      }));
    } else {
      setEstado(prev => ({
        ...prev,
        subtotal: 0,
        igv: 0,
        total: 0,
      }));
    }
  }, [estado.items.length, estado.descuentoGlobal, calcularTotales]);

  // Focus automático en búsqueda de productos
  useEffect(() => {
    if (!estado.ventaCompletada && busquedaProductoRef.current) {
      busquedaProductoRef.current.focus();
    }
  }, [estado.ventaCompletada]);

  // =============================================================================
  // FUNCIONES DE BÚSQUEDA
  // =============================================================================

  const buscarClientes = useCallback(async (consulta: string) => {
    if (consulta.length < 3) {
      setClientesEncontrados([]);
      return;
    }
    
    try {
      const resultados = await facturacionService.buscarClientePOS(consulta);
      setClientesEncontrados(resultados);
      setMostrarBusquedaClientes(true);
    } catch (error) {
      console.error('Error al buscar clientes:', error);
      setClientesEncontrados([]);
    }
  }, []);

  const buscarProductos = useCallback(async (consulta: string) => {
    if (consulta.length < 2) {
      setProductosEncontrados([]);
      return;
    }
    
    try {
      const resultados = await facturacionService.buscarProductoPOS(consulta);
      setProductosEncontrados(resultados.filter(p => p.activo && p.stock_disponible > 0));
      setMostrarBusquedaProductos(true);
    } catch (error) {
      console.error('Error al buscar productos:', error);
      setProductosEncontrados([]);
    }
  }, []);

  // =============================================================================
  // FUNCIONES DE MANEJO DE ESTADO
  // =============================================================================

  const seleccionarCliente = useCallback((cliente: ResultadoBusquedaCliente) => {
    const clienteCompleto: Cliente = {
      id: cliente.id,
      numero_documento: cliente.numero_documento,
      razon_social: cliente.razon_social,
      tipo_documento: cliente.tipo_documento as any,
      direccion: '',
      email: '',
      telefono: '',
      activo: true,
      created_at: '',
      updated_at: '',
    };
    
    setEstado(prev => ({
      ...prev,
      clienteSeleccionado: clienteCompleto,
      busquedaCliente: cliente.razon_social,
      // Validar tipo de comprobante según cliente
      tipoComprobante: cliente.tipo_documento === 'RUC' ? 'factura' : 'boleta',
    }));
    
    setMostrarBusquedaClientes(false);
    setClientesEncontrados([]);
  }, []);

  const agregarProducto = useCallback((producto: ResultadoBusquedaProducto) => {
    const itemExistente = estado.items.find(item => item.producto_id === producto.id);
    
    if (itemExistente) {
      // Incrementar cantidad si ya existe
      actualizarCantidadItem(itemExistente.producto_id, itemExistente.cantidad + 1);
    } else {
      // Agregar nuevo item
      const nuevoItem: ItemPOS = {
        producto_id: producto.id,
        producto: {
          id: producto.id,
          codigo_producto: producto.codigo_producto,
          descripcion: producto.descripcion,
          precio_venta: producto.precio_venta,
          stock_disponible: producto.stock_disponible,
          activo: producto.activo,
        } as Producto,
        descripcion: producto.descripcion,
        cantidad: 1,
        precio_unitario: producto.precio_venta,
        descuento: 0,
        subtotal: 0, // Se calculará automáticamente
        igv: 0,      // Se calculará automáticamente
        total: 0,    // Se calculará automáticamente
      };
      
      setEstado(prev => ({
        ...prev,
        items: [...prev.items, nuevoItem],
        busquedaProducto: '',
      }));
    }
    
    setMostrarBusquedaProductos(false);
    setProductosEncontrados([]);
    
    // Volver a enfocar la búsqueda de productos
    if (busquedaProductoRef.current) {
      busquedaProductoRef.current.focus();
    }
  }, [estado.items]);

  const actualizarCantidadItem = useCallback((productoId: number, nuevaCantidad: number) => {
    if (nuevaCantidad <= 0) {
      eliminarItem(productoId);
      return;
    }
    
    setEstado(prev => ({
      ...prev,
      items: prev.items.map(item =>
        item.producto_id === productoId
          ? { ...item, cantidad: nuevaCantidad }
          : item
      ),
    }));
  }, []);

  const actualizarPrecioItem = useCallback((productoId: number, nuevoPrecio: number) => {
    setEstado(prev => ({
      ...prev,
      items: prev.items.map(item =>
        item.producto_id === productoId
          ? { ...item, precio_unitario: Math.max(0, nuevoPrecio) }
          : item
      ),
    }));
  }, []);

  const actualizarDescuentoItem = useCallback((productoId: number, nuevoDescuento: number) => {
    setEstado(prev => ({
      ...prev,
      items: prev.items.map(item =>
        item.producto_id === productoId
          ? { ...item, descuento: Math.max(0, nuevoDescuento) }
          : item
      ),
    }));
  }, []);

  const eliminarItem = useCallback((productoId: number) => {
    setEstado(prev => ({
      ...prev,
      items: prev.items.filter(item => item.producto_id !== productoId),
    }));
  }, []);

  const limpiarVenta = useCallback(() => {
    setEstado({
      clienteSeleccionado: null,
      busquedaCliente: '',
      busquedaProducto: '',
      tipoComprobante: 'boleta',
      items: [],
      subtotal: 0,
      descuentoGlobal: 0,
      igv: 0,
      total: 0,
      medioPago: MedioPago.EFECTIVO,
      observaciones: '',
      procesandoVenta: false,
      ventaCompletada: false,
      numeroComprobante: null,
      errores: [],
    });
    
    setClientesEncontrados([]);
    setProductosEncontrados([]);
    setMostrarBusquedaClientes(false);
    setMostrarBusquedaProductos(false);
  }, []);

  // =============================================================================
  // FUNCIÓN DE PROCESAMIENTO DE VENTA
  // =============================================================================

  const procesarVenta = useCallback(async () => {
    // Validaciones previas
    const erroresValidacion: string[] = [];
    
    if (!estado.clienteSeleccionado) {
      erroresValidacion.push('Debe seleccionar un cliente');
    }
    
    if (estado.items.length === 0) {
      erroresValidacion.push('Debe agregar al menos un producto');
    }
    
    if (estado.tipoComprobante === 'factura' && estado.clienteSeleccionado?.tipo_documento !== 'RUC') {
      erroresValidacion.push('Las facturas requieren un cliente con RUC');
    }
    
    if (estado.tipoComprobante === 'boleta' && estado.clienteSeleccionado?.tipo_documento === 'RUC') {
      erroresValidacion.push('Para clientes con RUC se debe emitir factura');
    }
    
    if (erroresValidacion.length > 0) {
      setEstado(prev => ({ ...prev, errores: erroresValidacion }));
      return;
    }
    
    setEstado(prev => ({ 
      ...prev, 
      procesandoVenta: true, 
      errores: [] 
    }));
    
    try {
      // Preparar datos de la venta
      const datosVenta = {
        tipo_comprobante: estado.tipoComprobante,
        cliente_id: estado.clienteSeleccionado!.id,
        items: estado.items.map(item => ({
          producto_id: item.producto_id,
          cantidad: item.cantidad,
          precio_unitario: item.precio_unitario,
          descuento: item.descuento,
        })),
        medio_pago: estado.medioPago,
        observaciones: estado.observaciones || undefined,
      };
      
      // Crear venta
      const ventaCreada = await facturacionService.crearVentaPOS(datosVenta);
      
      // Actualizar estado con el resultado
      setEstado(prev => ({
        ...prev,
        procesandoVenta: false,
        ventaCompletada: true,
        numeroComprobante: ventaCreada.numero_completo,
      }));
      
      // Mostrar mensaje de éxito
      setTimeout(() => {
        limpiarVenta();
      }, 3000);
      
    } catch (error) {
      console.error('Error al procesar venta:', error);
      const mensajeError = error instanceof Error ? error.message : 'Error al procesar la venta';
      
      setEstado(prev => ({
        ...prev,
        procesandoVenta: false,
        errores: [mensajeError],
      }));
    }
  }, [estado, limpiarVenta]);

  // =============================================================================
  // MANEJADORES DE EVENTOS
  // =============================================================================

  const manejarBusquedaCliente = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const valor = e.target.value;
    setEstado(prev => ({ ...prev, busquedaCliente: valor }));
    
    if (valor.length >= 3) {
      buscarClientes(valor);
    } else {
      setClientesEncontrados([]);
      setMostrarBusquedaClientes(false);
    }
  }, [buscarClientes]);

  const manejarBusquedaProducto = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const valor = e.target.value;
    setEstado(prev => ({ ...prev, busquedaProducto: valor }));
    
    if (valor.length >= 2) {
      buscarProductos(valor);
    } else {
      setProductosEncontrados([]);
      setMostrarBusquedaProductos(false);
    }
  }, [buscarProductos]);

  const manejarTeclaProducto = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && productosEncontrados.length > 0) {
      agregarProducto(productosEncontrados[0]);
    } else if (e.key === 'Escape') {
      setMostrarBusquedaProductos(false);
      setProductosEncontrados([]);
    }
  }, [productosEncontrados, agregarProducto]);

  // =============================================================================
  // RENDER
  // =============================================================================

  if (estado.ventaCompletada) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md w-full">
          <div className="mb-6">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">¡Venta Completada!</h2>
            <p className="text-gray-600">
              Comprobante generado exitosamente
            </p>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg mb-6">
            <div className="text-sm text-gray-600 mb-1">Número de Comprobante</div>
            <div className="text-xl font-mono font-bold text-gray-900">
              {estado.numeroComprobante}
            </div>
          </div>
          
          <div className="space-y-3">
            <button
              onClick={limpiarVenta}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Nueva Venta
            </button>
            
            <button
              onClick={() => window.print()}
              className="w-full bg-gray-600 text-white py-3 px-4 rounded-lg hover:bg-gray-700 transition-colors font-medium flex items-center justify-center gap-2"
            >
              <Printer className="w-4 h-4" />
              Imprimir
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Punto de Venta</h1>
              <p className="text-gray-600">Sistema FELICITA - Facturación Electrónica</p>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm text-gray-600">Usuario</div>
                <div className="font-medium">{usuario?.username}</div>
              </div>
              
              <button
                onClick={limpiarVenta}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
              >
                Limpiar
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Panel Principal - Productos */}
          <div className="lg:col-span-2 space-y-6">
            {/* Búsqueda de Cliente */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <User className="w-5 h-5" />
                Cliente
              </h3>
              
              <div className="relative">
                <input
                  ref={busquedaClienteRef}
                  type="text"
                  placeholder="Buscar cliente por nombre o documento..."
                  value={estado.busquedaCliente}
                  onChange={manejarBusquedaCliente}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                
                {/* Resultados de búsqueda de clientes */}
                {mostrarBusquedaClientes && clientesEncontrados.length > 0 && (
                  <div className="absolute z-10 w-full bg-white border border-gray-300 rounded-lg mt-1 shadow-lg">
                    {clientesEncontrados.map((cliente) => (
                      <button
                        key={cliente.id}
                        onClick={() => seleccionarCliente(cliente)}
                        className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                      >
                        <div className="font-medium">{cliente.razon_social}</div>
                        <div className="text-sm text-gray-600">
                          {cliente.tipo_documento}: {cliente.numero_documento}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Cliente seleccionado */}
              {estado.clienteSeleccionado && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-blue-900">
                        {estado.clienteSeleccionado.razon_social}
                      </div>
                      <div className="text-sm text-blue-700">
                        {estado.clienteSeleccionado.tipo_documento}: {estado.clienteSeleccionado.numero_documento}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        estado.tipoComprobante === 'factura' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {estado.tipoComprobante === 'factura' ? 'Factura' : 'Boleta'}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Búsqueda de Productos */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Search className="w-5 h-5" />
                Productos
              </h3>
              
              <div className="relative">
                <input
                  ref={busquedaProductoRef}
                  type="text"
                  placeholder="Buscar producto por código o descripción..."
                  value={estado.busquedaProducto}
                  onChange={manejarBusquedaProducto}
                  onKeyDown={manejarTeclaProducto}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                
                {/* Resultados de búsqueda de productos */}
                {mostrarBusquedaProductos && productosEncontrados.length > 0 && (
                  <div className="absolute z-10 w-full bg-white border border-gray-300 rounded-lg mt-1 shadow-lg max-h-60 overflow-y-auto">
                    {productosEncontrados.map((producto) => (
                      <button
                        key={producto.id}
                        onClick={() => agregarProducto(producto)}
                        className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">{producto.descripcion}</div>
                            <div className="text-sm text-gray-600">
                              Código: {producto.codigo_producto} | Stock: {producto.stock_disponible}
                            </div>
                          </div>
                          <div className="text-lg font-bold text-green-600">
                            S/ {producto.precio_venta.toFixed(2)}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Lista de Items */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <ShoppingCart className="w-5 h-5" />
                Items de Venta ({estado.items.length})
              </h3>
              
              {estado.items.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <ShoppingCart className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No hay productos agregados</p>
                  <p className="text-sm">Busque y seleccione productos para agregar</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {estado.items.map((item) => (
                    <div key={item.producto_id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex-1">
                          <div className="font-medium">{item.descripcion}</div>
                          <div className="text-sm text-gray-600">
                            Código: {item.producto?.codigo_producto}
                          </div>
                        </div>
                        
                        <button
                          onClick={() => eliminarItem(item.producto_id)}
                          className="text-red-600 hover:text-red-800 p-1"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      
                      <div className="grid grid-cols-4 gap-4 items-center">
                        {/* Cantidad */}
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Cantidad</label>
                          <div className="flex items-center border border-gray-300 rounded">
                            <button
                              onClick={() => actualizarCantidadItem(item.producto_id, item.cantidad - 1)}
                              className="p-1 hover:bg-gray-100"
                            >
                              <Minus className="w-4 h-4" />
                            </button>
                            <input
                              type="number"
                              value={item.cantidad}
                              onChange={(e) => actualizarCantidadItem(item.producto_id, Number(e.target.value))}
                              className="w-full text-center border-0 py-1 focus:ring-0"
                              min="1"
                            />
                            <button
                              onClick={() => actualizarCantidadItem(item.producto_id, item.cantidad + 1)}
                              className="p-1 hover:bg-gray-100"
                            >
                              <Plus className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        
                        {/* Precio Unitario */}
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Precio Unit.</label>
                          <input
                            type="number"
                            value={item.precio_unitario}
                            onChange={(e) => actualizarPrecioItem(item.producto_id, Number(e.target.value))}
                            className="w-full border border-gray-300 rounded px-2 py-1"
                            step="0.01"
                            min="0"
                          />
                        </div>
                        
                        {/* Descuento */}
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Descuento</label>
                          <input
                            type="number"
                            value={item.descuento}
                            onChange={(e) => actualizarDescuentoItem(item.producto_id, Number(e.target.value))}
                            className="w-full border border-gray-300 rounded px-2 py-1"
                            step="0.01"
                            min="0"
                          />
                        </div>
                        
                        {/* Total */}
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Total</label>
                          <div className="font-bold text-lg">
                            S/ {item.total.toFixed(2)}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Panel Lateral - Resumen y Pago */}
          <div className="space-y-6">
            {/* Resumen de Totales */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Calculator className="w-5 h-5" />
                Resumen de Venta
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal:</span>
                  <span className="font-medium">S/ {estado.subtotal.toFixed(2)}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Descuento Global:</span>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      value={estado.descuentoGlobal}
                      onChange={(e) => setEstado(prev => ({ ...prev, descuentoGlobal: Number(e.target.value) }))}
                      className="w-20 text-right border border-gray-300 rounded px-2 py-1"
                      step="0.01"
                      min="0"
                    />
                  </div>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">IGV (18%):</span>
                  <span className="font-medium">S/ {estado.igv.toFixed(2)}</span>
                </div>
                
                <div className="border-t pt-3">
                  <div className="flex justify-between text-xl font-bold">
                    <span>Total:</span>
                    <span className="text-blue-600">S/ {estado.total.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Configuración de Pago */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <CreditCard className="w-5 h-5" />
                Medio de Pago
              </h3>
              
              <div className="space-y-3">
                <select
                  value={estado.medioPago}
                  onChange={(e) => setEstado(prev => ({ ...prev, medioPago: e.target.value as MedioPago }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value={MedioPago.EFECTIVO}>Efectivo</option>
                  <option value={MedioPago.TRANSFERENCIA}>Transferencia</option>
                  <option value={MedioPago.TARJETA}>Tarjeta</option>
                  <option value={MedioPago.CHEQUE}>Cheque</option>
                </select>
                
                <textarea
                  placeholder="Observaciones (opcional)"
                  value={estado.observaciones}
                  onChange={(e) => setEstado(prev => ({ ...prev, observaciones: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                />
              </div>
            </div>

            {/* Errores */}
            {estado.errores.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center gap-2 text-red-800 mb-2">
                  <AlertCircle className="w-5 h-5" />
                  <span className="font-medium">Errores de validación:</span>
                </div>
                <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
                  {estado.errores.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Botón de Venta */}
            <button
              onClick={procesarVenta}
              disabled={estado.procesandoVenta || estado.items.length === 0 || !estado.clienteSeleccionado}
              className="w-full bg-green-600 text-white py-4 px-6 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold text-lg flex items-center justify-center gap-2"
            >
              {estado.procesandoVenta ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Procesando...
                </>
              ) : (
                <>
                  <CreditCard className="w-5 h-5" />
                  Procesar Venta
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PuntoDeVenta;