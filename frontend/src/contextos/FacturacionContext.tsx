/**
 * CONTEXTO DE FACTURACIÓN - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Contexto React para manejo global del estado de facturación
 */

import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import { 
  Factura, 
  Boleta, 
  NotaCredito, 
  SerieComprobante,
  ConfiguracionFacturacion,
  FiltrosFactura,
  CrearFacturaRequest,
  CrearBoletaRequest,
  CrearNotaCreditoRequest,
  EstadoSunatResponse,
  ItemComprobanteRequest,
  CalculoTotalesPOS,
  ValidacionNumeracion,
  ContextoFacturacion
} from '../types/factura';

import * as facturacionService from '../servicios/facturas';

// =============================================================================
// TIPOS PARA EL REDUCER
// =============================================================================

interface EstadoFacturacion {
  // Datos
  facturas: Factura[];
  boletas: Boleta[];
  notasCredito: NotaCredito[];
  series: SerieComprobante[];
  configuracion: ConfiguracionFacturacion | null;
  
  // Paginación
  totalFacturas: number;
  totalBoletas: number;
  totalNotasCredito: number;
  paginaActualFacturas: number;
  paginaActualBoletas: number;
  paginaActualNotasCredito: number;
  
  // Estados de carga
  cargandoFacturas: boolean;
  cargandoBoletas: boolean;
  cargandoNotasCredito: boolean;
  cargandoSeries: boolean;
  cargandoConfiguracion: boolean;
  
  // Errores
  errorFacturas: string | null;
  errorBoletas: string | null;
  errorNotasCredito: string | null;
  errorSeries: string | null;
  errorConfiguracion: string | null;
  
  // Filtros activos
  filtrosFacturas: FiltrosFactura | null;
  filtrosBoletas: FiltrosFactura | null;
  filtrosNotasCredito: FiltrosFactura | null;
  
  // Cache
  ultimaActualizacion: Date | null;
}

type AccionFacturacion =
  // Acciones de facturas
  | { type: 'CARGAR_FACTURAS_INICIO' }
  | { type: 'CARGAR_FACTURAS_EXITO'; payload: { facturas: Factura[]; total: number; pagina: number } }
  | { type: 'CARGAR_FACTURAS_ERROR'; payload: string }
  | { type: 'AGREGAR_FACTURA'; payload: Factura }
  | { type: 'ACTUALIZAR_FACTURA'; payload: Factura }
  | { type: 'ELIMINAR_FACTURA'; payload: number }
  
  // Acciones de boletas
  | { type: 'CARGAR_BOLETAS_INICIO' }
  | { type: 'CARGAR_BOLETAS_EXITO'; payload: { boletas: Boleta[]; total: number; pagina: number } }
  | { type: 'CARGAR_BOLETAS_ERROR'; payload: string }
  | { type: 'AGREGAR_BOLETA'; payload: Boleta }
  | { type: 'ACTUALIZAR_BOLETA'; payload: Boleta }
  | { type: 'ELIMINAR_BOLETA'; payload: number }
  
  // Acciones de notas de crédito
  | { type: 'CARGAR_NOTAS_CREDITO_INICIO' }
  | { type: 'CARGAR_NOTAS_CREDITO_EXITO'; payload: { notasCredito: NotaCredito[]; total: number; pagina: number } }
  | { type: 'CARGAR_NOTAS_CREDITO_ERROR'; payload: string }
  | { type: 'AGREGAR_NOTA_CREDITO'; payload: NotaCredito }
  | { type: 'ACTUALIZAR_NOTA_CREDITO'; payload: NotaCredito }
  | { type: 'ELIMINAR_NOTA_CREDITO'; payload: number }
  
  // Acciones de series
  | { type: 'CARGAR_SERIES_INICIO' }
  | { type: 'CARGAR_SERIES_EXITO'; payload: SerieComprobante[] }
  | { type: 'CARGAR_SERIES_ERROR'; payload: string }
  | { type: 'AGREGAR_SERIE'; payload: SerieComprobante }
  | { type: 'ACTUALIZAR_SERIE'; payload: SerieComprobante }
  
  // Acciones de configuración
  | { type: 'CARGAR_CONFIGURACION_INICIO' }
  | { type: 'CARGAR_CONFIGURACION_EXITO'; payload: ConfiguracionFacturacion }
  | { type: 'CARGAR_CONFIGURACION_ERROR'; payload: string }
  
  // Acciones de filtros
  | { type: 'ESTABLECER_FILTROS_FACTURAS'; payload: FiltrosFactura }
  | { type: 'ESTABLECER_FILTROS_BOLETAS'; payload: FiltrosFactura }
  | { type: 'ESTABLECER_FILTROS_NOTAS_CREDITO'; payload: FiltrosFactura }
  | { type: 'LIMPIAR_FILTROS' }
  
  // Acciones de cache
  | { type: 'ACTUALIZAR_CACHE' }
  | { type: 'LIMPIAR_CACHE' }
  | { type: 'REINICIAR_ESTADO' };

// =============================================================================
// ESTADO INICIAL
// =============================================================================

const estadoInicial: EstadoFacturacion = {
  // Datos
  facturas: [],
  boletas: [],
  notasCredito: [],
  series: [],
  configuracion: null,
  
  // Paginación
  totalFacturas: 0,
  totalBoletas: 0,
  totalNotasCredito: 0,
  paginaActualFacturas: 1,
  paginaActualBoletas: 1,
  paginaActualNotasCredito: 1,
  
  // Estados de carga
  cargandoFacturas: false,
  cargandoBoletas: false,
  cargandoNotasCredito: false,
  cargandoSeries: false,
  cargandoConfiguracion: false,
  
  // Errores
  errorFacturas: null,
  errorBoletas: null,
  errorNotasCredito: null,
  errorSeries: null,
  errorConfiguracion: null,
  
  // Filtros
  filtrosFacturas: null,
  filtrosBoletas: null,
  filtrosNotasCredito: null,
  
  // Cache
  ultimaActualizacion: null,
};

// =============================================================================
// REDUCER
// =============================================================================

const facturacionReducer = (estado: EstadoFacturacion, accion: AccionFacturacion): EstadoFacturacion => {
  switch (accion.type) {
    // Facturas
    case 'CARGAR_FACTURAS_INICIO':
      return {
        ...estado,
        cargandoFacturas: true,
        errorFacturas: null,
      };
    
    case 'CARGAR_FACTURAS_EXITO':
      return {
        ...estado,
        cargandoFacturas: false,
        facturas: accion.payload.facturas,
        totalFacturas: accion.payload.total,
        paginaActualFacturas: accion.payload.pagina,
        errorFacturas: null,
        ultimaActualizacion: new Date(),
      };
    
    case 'CARGAR_FACTURAS_ERROR':
      return {
        ...estado,
        cargandoFacturas: false,
        errorFacturas: accion.payload,
      };
    
    case 'AGREGAR_FACTURA':
      return {
        ...estado,
        facturas: [accion.payload, ...estado.facturas],
        totalFacturas: estado.totalFacturas + 1,
      };
    
    case 'ACTUALIZAR_FACTURA':
      return {
        ...estado,
        facturas: estado.facturas.map(factura =>
          factura.id === accion.payload.id ? accion.payload : factura
        ),
      };
    
    case 'ELIMINAR_FACTURA':
      return {
        ...estado,
        facturas: estado.facturas.filter(factura => factura.id !== accion.payload),
        totalFacturas: estado.totalFacturas - 1,
      };
    
    // Boletas
    case 'CARGAR_BOLETAS_INICIO':
      return {
        ...estado,
        cargandoBoletas: true,
        errorBoletas: null,
      };
    
    case 'CARGAR_BOLETAS_EXITO':
      return {
        ...estado,
        cargandoBoletas: false,
        boletas: accion.payload.boletas,
        totalBoletas: accion.payload.total,
        paginaActualBoletas: accion.payload.pagina,
        errorBoletas: null,
        ultimaActualizacion: new Date(),
      };
    
    case 'CARGAR_BOLETAS_ERROR':
      return {
        ...estado,
        cargandoBoletas: false,
        errorBoletas: accion.payload,
      };
    
    case 'AGREGAR_BOLETA':
      return {
        ...estado,
        boletas: [accion.payload, ...estado.boletas],
        totalBoletas: estado.totalBoletas + 1,
      };
    
    case 'ACTUALIZAR_BOLETA':
      return {
        ...estado,
        boletas: estado.boletas.map(boleta =>
          boleta.id === accion.payload.id ? accion.payload : boleta
        ),
      };
    
    case 'ELIMINAR_BOLETA':
      return {
        ...estado,
        boletas: estado.boletas.filter(boleta => boleta.id !== accion.payload),
        totalBoletas: estado.totalBoletas - 1,
      };
    
    // Notas de crédito
    case 'CARGAR_NOTAS_CREDITO_INICIO':
      return {
        ...estado,
        cargandoNotasCredito: true,
        errorNotasCredito: null,
      };
    
    case 'CARGAR_NOTAS_CREDITO_EXITO':
      return {
        ...estado,
        cargandoNotasCredito: false,
        notasCredito: accion.payload.notasCredito,
        totalNotasCredito: accion.payload.total,
        paginaActualNotasCredito: accion.payload.pagina,
        errorNotasCredito: null,
        ultimaActualizacion: new Date(),
      };
    
    case 'CARGAR_NOTAS_CREDITO_ERROR':
      return {
        ...estado,
        cargandoNotasCredito: false,
        errorNotasCredito: accion.payload,
      };
    
    case 'AGREGAR_NOTA_CREDITO':
      return {
        ...estado,
        notasCredito: [accion.payload, ...estado.notasCredito],
        totalNotasCredito: estado.totalNotasCredito + 1,
      };
    
    case 'ACTUALIZAR_NOTA_CREDITO':
      return {
        ...estado,
        notasCredito: estado.notasCredito.map(nota =>
          nota.id === accion.payload.id ? accion.payload : nota
        ),
      };
    
    case 'ELIMINAR_NOTA_CREDITO':
      return {
        ...estado,
        notasCredito: estado.notasCredito.filter(nota => nota.id !== accion.payload),
        totalNotasCredito: estado.totalNotasCredito - 1,
      };
    
    // Series
    case 'CARGAR_SERIES_INICIO':
      return {
        ...estado,
        cargandoSeries: true,
        errorSeries: null,
      };
    
    case 'CARGAR_SERIES_EXITO':
      return {
        ...estado,
        cargandoSeries: false,
        series: accion.payload,
        errorSeries: null,
      };
    
    case 'CARGAR_SERIES_ERROR':
      return {
        ...estado,
        cargandoSeries: false,
        errorSeries: accion.payload,
      };
    
    case 'AGREGAR_SERIE':
      return {
        ...estado,
        series: [...estado.series, accion.payload],
      };
    
    case 'ACTUALIZAR_SERIE':
      return {
        ...estado,
        series: estado.series.map(serie =>
          serie.id === accion.payload.id ? accion.payload : serie
        ),
      };
    
    // Configuración
    case 'CARGAR_CONFIGURACION_INICIO':
      return {
        ...estado,
        cargandoConfiguracion: true,
        errorConfiguracion: null,
      };
    
    case 'CARGAR_CONFIGURACION_EXITO':
      return {
        ...estado,
        cargandoConfiguracion: false,
        configuracion: accion.payload,
        errorConfiguracion: null,
      };
    
    case 'CARGAR_CONFIGURACION_ERROR':
      return {
        ...estado,
        cargandoConfiguracion: false,
        errorConfiguracion: accion.payload,
      };
    
    // Filtros
    case 'ESTABLECER_FILTROS_FACTURAS':
      return {
        ...estado,
        filtrosFacturas: accion.payload,
      };
    
    case 'ESTABLECER_FILTROS_BOLETAS':
      return {
        ...estado,
        filtrosBoletas: accion.payload,
      };
    
    case 'ESTABLECER_FILTROS_NOTAS_CREDITO':
      return {
        ...estado,
        filtrosNotasCredito: accion.payload,
      };
    
    case 'LIMPIAR_FILTROS':
      return {
        ...estado,
        filtrosFacturas: null,
        filtrosBoletas: null,
        filtrosNotasCredito: null,
      };
    
    // Cache
    case 'ACTUALIZAR_CACHE':
      return {
        ...estado,
        ultimaActualizacion: new Date(),
      };
    
    case 'LIMPIAR_CACHE':
      return {
        ...estado,
        facturas: [],
        boletas: [],
        notasCredito: [],
        ultimaActualizacion: null,
      };
    
    case 'REINICIAR_ESTADO':
      return estadoInicial;
    
    default:
      return estado;
  }
};

// =============================================================================
// CONTEXTO
// =============================================================================

const FacturacionContext = createContext<ContextoFacturacion | undefined>(undefined);

// =============================================================================
// HOOK PERSONALIZADO
// =============================================================================

export const useFacturacion = (): ContextoFacturacion => {
  const contexto = useContext(FacturacionContext);
  if (!contexto) {
    throw new Error('useFacturacion debe usarse dentro de un FacturacionProvider');
  }
  return contexto;
};

// =============================================================================
// PROVIDER
// =============================================================================

interface FacturacionProviderProps {
  children: React.ReactNode;
}

export const FacturacionProvider: React.FC<FacturacionProviderProps> = ({ children }) => {
  const [estado, dispatch] = useReducer(facturacionReducer, estadoInicial);

  // =============================================================================
  // FUNCIONES DE CARGA
  // =============================================================================

  const cargarFacturas = useCallback(async (filtros?: FiltrosFactura) => {
    try {
      dispatch({ type: 'CARGAR_FACTURAS_INICIO' });
      
      if (filtros) {
        dispatch({ type: 'ESTABLECER_FILTROS_FACTURAS', payload: filtros });
      }
      
      const respuesta = await facturacionService.obtenerFacturas(filtros || estado.filtrosFacturas || undefined);
      
      dispatch({
        type: 'CARGAR_FACTURAS_EXITO',
        payload: {
          facturas: respuesta.results,
          total: respuesta.count,
          pagina: filtros?.page || 1,
        },
      });
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : 'Error al cargar facturas';
      dispatch({ type: 'CARGAR_FACTURAS_ERROR', payload: mensaje });
    }
  }, [estado.filtrosFacturas]);

  const cargarBoletas = useCallback(async (filtros?: FiltrosFactura) => {
    try {
      dispatch({ type: 'CARGAR_BOLETAS_INICIO' });
      
      if (filtros) {
        dispatch({ type: 'ESTABLECER_FILTROS_BOLETAS', payload: filtros });
      }
      
      const respuesta = await facturacionService.obtenerBoletas(filtros || estado.filtrosBoletas || undefined);
      
      dispatch({
        type: 'CARGAR_BOLETAS_EXITO',
        payload: {
          boletas: respuesta.results,
          total: respuesta.count,
          pagina: filtros?.page || 1,
        },
      });
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : 'Error al cargar boletas';
      dispatch({ type: 'CARGAR_BOLETAS_ERROR', payload: mensaje });
    }
  }, [estado.filtrosBoletas]);

  const cargarNotasCredito = useCallback(async (filtros?: FiltrosFactura) => {
    try {
      dispatch({ type: 'CARGAR_NOTAS_CREDITO_INICIO' });
      
      if (filtros) {
        dispatch({ type: 'ESTABLECER_FILTROS_NOTAS_CREDITO', payload: filtros });
      }
      
      const respuesta = await facturacionService.obtenerNotasCredito(filtros || estado.filtrosNotasCredito || undefined);
      
      dispatch({
        type: 'CARGAR_NOTAS_CREDITO_EXITO',
        payload: {
          notasCredito: respuesta.results,
          total: respuesta.count,
          pagina: filtros?.page || 1,
        },
      });
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : 'Error al cargar notas de crédito';
      dispatch({ type: 'CARGAR_NOTAS_CREDITO_ERROR', payload: mensaje });
    }
  }, [estado.filtrosNotasCredito]);

  const cargarSeries = useCallback(async () => {
    try {
      dispatch({ type: 'CARGAR_SERIES_INICIO' });
      const series = await facturacionService.obtenerSeries();
      dispatch({ type: 'CARGAR_SERIES_EXITO', payload: series });
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : 'Error al cargar series';
      dispatch({ type: 'CARGAR_SERIES_ERROR', payload: mensaje });
    }
  }, []);

  // =============================================================================
  // FUNCIONES DE CREACIÓN
  // =============================================================================

  const crearFactura = useCallback(async (datos: CrearFacturaRequest): Promise<Factura> => {
    try {
      const nuevaFactura = await facturacionService.crearFactura(datos);
      dispatch({ type: 'AGREGAR_FACTURA', payload: nuevaFactura });
      return nuevaFactura;
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : 'Error al crear factura';
      throw new Error(mensaje);
    }
  }, []);

  const crearBoleta = useCallback(async (datos: CrearBoletaRequest): Promise<Boleta> => {
    try {
      const nuevaBoleta = await facturacionService.crearBoleta(datos);
      dispatch({ type: 'AGREGAR_BOLETA', payload: nuevaBoleta });
      return nuevaBoleta;
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : 'Error al crear boleta';
      throw new Error(mensaje);
    }
  }, []);

  const crearNotaCredito = useCallback(async (datos: CrearNotaCreditoRequest): Promise<NotaCredito> => {
    try {
      const nuevaNotaCredito = await facturacionService.crearNotaCredito(datos);
      dispatch({ type: 'AGREGAR_NOTA_CREDITO', payload: nuevaNotaCredito });
      return nuevaNotaCredito;
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : 'Error al crear nota de crédito';
      throw new Error(mensaje);
    }
  }, []);

  // =============================================================================
  // FUNCIONES DE INTEGRACIÓN SUNAT
  // =============================================================================

  const enviarSunat = useCallback(async (id: number, tipo: 'factura' | 'boleta' | 'nota_credito') => {
    try {
      let resultado;
      switch (tipo) {
        case 'factura':
          resultado = await facturacionService.enviarFacturaSunat(id);
          const facturaActualizada = await facturacionService.obtenerFacturaPorId(id);
          dispatch({ type: 'ACTUALIZAR_FACTURA', payload: facturaActualizada });
          break;
        case 'boleta':
          resultado = await facturacionService.enviarBoletaSunat(id);
          // Actualizar boleta en el estado
          break;
        case 'nota_credito':
          // Implementar envío de nota de crédito
          break;
      }
      return resultado;
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : 'Error al enviar a SUNAT';
      throw new Error(mensaje);
    }
  }, []);

  const consultarEstado = useCallback(async (id: number, tipo: 'factura' | 'boleta' | 'nota_credito'): Promise<EstadoSunatResponse> => {
    try {
      const resultado = await facturacionService.consultarEstadoFactura(id);
      
      // Actualizar el comprobante en el estado local
      switch (tipo) {
        case 'factura':
          const facturaActualizada = await facturacionService.obtenerFacturaPorId(id);
          dispatch({ type: 'ACTUALIZAR_FACTURA', payload: facturaActualizada });
          break;
        case 'boleta':
          // Implementar actualización de boleta
          break;
        case 'nota_credito':
          // Implementar actualización de nota de crédito
          break;
      }
      
      return resultado;
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : 'Error al consultar estado';
      throw new Error(mensaje);
    }
  }, []);

  const anularComprobante = useCallback(async (id: number, tipo: 'factura' | 'boleta' | 'nota_credito', motivo: string) => {
    try {
      const resultado = await facturacionService.anularFactura(id, motivo);
      
      // Actualizar el comprobante en el estado local
      switch (tipo) {
        case 'factura':
          const facturaActualizada = await facturacionService.obtenerFacturaPorId(id);
          dispatch({ type: 'ACTUALIZAR_FACTURA', payload: facturaActualizada });
          break;
        case 'boleta':
          // Implementar actualización de boleta
          break;
        case 'nota_credito':
          // Implementar actualización de nota de crédito
          break;
      }
      
      return resultado;
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : 'Error al anular comprobante';
      throw new Error(mensaje);
    }
  }, []);

  // =============================================================================
  // FUNCIONES UTILITARIAS
  // =============================================================================

  const calcularTotales = useCallback((items: ItemComprobanteRequest[], descuentoGlobal: number = 0): CalculoTotalesPOS => {
    let subtotal = 0;
    const itemsCalculados = [];

    for (const item of items) {
      const subtotalItem = item.cantidad * item.precio_unitario - (item.descuento || 0);
      const igvItem = subtotalItem * 0.18; // IGV 18%
      const totalItem = subtotalItem + igvItem;

      subtotal += subtotalItem;
      itemsCalculados.push({
        subtotal: Number(subtotalItem.toFixed(2)),
        igv: Number(igvItem.toFixed(2)),
        total: Number(totalItem.toFixed(2)),
      });
    }

    // Aplicar descuento global
    subtotal -= descuentoGlobal;
    const igv = subtotal * 0.18;
    const total = subtotal + igv;

    return {
      subtotal: Number(subtotal.toFixed(2)),
      igv: Number(igv.toFixed(2)),
      total: Number(total.toFixed(2)),
      items_calculados: itemsCalculados,
    };
  }, []);

  const validarNumeracion = useCallback(async (serie: string, numero: number, tipo: string): Promise<ValidacionNumeracion> => {
    try {
      return await facturacionService.validarNumeracion(serie, numero, tipo);
    } catch (error) {
      const mensaje = error instanceof Error ? error.message : 'Error al validar numeración';
      throw new Error(mensaje);
    }
  }, []);

  const limpiarCache = useCallback(() => {
    dispatch({ type: 'LIMPIAR_CACHE' });
  }, []);

  // =============================================================================
  // EFECTOS
  // =============================================================================

  // Cargar datos iniciales
  useEffect(() => {
    cargarSeries();
  }, [cargarSeries]);

  // Auto-refrescar cada 5 minutos
  useEffect(() => {
    const intervalo = setInterval(() => {
      if (estado.ultimaActualizacion) {
        const tiempoTranscurrido = Date.now() - estado.ultimaActualizacion.getTime();
        if (tiempoTranscurrido > 5 * 60 * 1000) { // 5 minutos
          dispatch({ type: 'ACTUALIZAR_CACHE' });
        }
      }
    }, 60000); // Verificar cada minuto

    return () => clearInterval(intervalo);
  }, [estado.ultimaActualizacion]);

  // =============================================================================
  // VALOR DEL CONTEXTO
  // =============================================================================

  const valorContexto: ContextoFacturacion = {
    // Estado
    facturas: estado.facturas,
    boletas: estado.boletas,
    notasCredito: estado.notasCredito,
    series: estado.series,
    configuracion: estado.configuracion,
    
    // Estados de carga
    cargandoFacturas: estado.cargandoFacturas,
    cargandoBoletas: estado.cargandoBoletas,
    cargandoNotasCredito: estado.cargandoNotasCredito,
    
    // Errores
    errorFacturas: estado.errorFacturas,
    errorBoletas: estado.errorBoletas,
    errorNotasCredito: estado.errorNotasCredito,
    
    // Acciones
    cargarFacturas,
    cargarBoletas,
    cargarNotasCredito,
    crearFactura,
    crearBoleta,
    crearNotaCredito,
    enviarSunat,
    consultarEstado,
    anularComprobante,
    
    // Utilidades
    calcularTotales,
    validarNumeracion,
    limpiarCache,
  };

  return (
    <FacturacionContext.Provider value={valorContexto}>
      {children}
    </FacturacionContext.Provider>
  );
};

// =============================================================================
// EXPORT DEFAULT
// =============================================================================

export default FacturacionProvider;