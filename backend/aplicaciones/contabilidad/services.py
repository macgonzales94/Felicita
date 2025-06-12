"""
SERVICES DE CONTABILIDAD - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Servicios para generación automática de asientos contables según PCGE
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from typing import Dict, List, Optional
import logging
from datetime import date, datetime

from .models import (
    PlanCuentas, AsientoContable, DetalleAsiento, PeriodoContable,
    CuentaPorCobrar, CuentaPorPagar, LibroMayor, BalanceComprobacion
)
from aplicaciones.core.models import Empresa
from aplicaciones.facturacion.models import Factura, Boleta, NotaCredito

logger = logging.getLogger('felicita.contabilidad')


# =============================================================================
# EXCEPCIONES PERSONALIZADAS
# =============================================================================
class ContabilidadError(Exception):
    """Error base para contabilidad"""
    pass


class AsientoDescuadradoError(ContabilidadError):
    """Error cuando el asiento no cuadra (debe != haber)"""
    pass


class CuentaNoEncontradaError(ContabilidadError):
    """Error cuando no se encuentra una cuenta contable"""
    pass


class PeriodoInactivoError(ContabilidadError):
    """Error cuando se intenta operar en un período inactivo"""
    pass


# =============================================================================
# SERVICIO PRINCIPAL DE CONTABILIDAD
# =============================================================================
class ContabilidadService:
    """
    Servicio para manejo completo de contabilidad automática según PCGE
    """
    
    def __init__(self, empresa_id: int = None):
        """
        Inicializar servicio de contabilidad
        
        Args:
            empresa_id: ID de la empresa (opcional)
        """
        self.empresa_id = empresa_id
        self.periodo_actual = self._obtener_periodo_actual()
        logger.debug(f"ContabilidadService inicializado para empresa {empresa_id}")
    
    # =============================================================================
    # MÉTODOS PÚBLICOS - ASIENTOS AUTOMÁTICOS
    # =============================================================================
    
    @transaction.atomic
    def generar_asiento_venta(
        self,
        comprobante,
        es_nota_credito: bool = False
    ) -> AsientoContable:
        """
        Generar asiento contable automático para ventas
        
        Asiento tipo para ventas:
        DEBE: 12 Cuentas por Cobrar Comerciales (total)
        HABER: 70 Ventas (subtotal)
        HABER: 40 Tributos por Pagar - IGV (igv)
        
        Args:
            comprobante: Instancia de Factura, Boleta o NotaCredito
            es_nota_credito: Si es nota de crédito (invierte el asiento)
            
        Returns:
            AsientoContable: El asiento generado
        """
        logger.info(f"Generando asiento de venta para {comprobante.numero_completo}")
        
        # Validar período activo
        self._validar_periodo_activo(comprobante.fecha_emision)
        
        # Obtener cuentas contables
        cuenta_por_cobrar = self._obtener_cuenta_por_codigo('12111')  # Facturas por cobrar
        cuenta_ventas = self._obtener_cuenta_por_codigo('70111')      # Venta de mercaderías
        cuenta_igv = self._obtener_cuenta_por_codigo('40111')         # IGV por pagar
        
        # Determinar concepto y multiplicador
        if es_nota_credito:
            concepto = f"Nota de Crédito {comprobante.numero_completo}"
            multiplicador = -1  # Invertir el asiento
        else:
            tipo_comp = "Factura" if isinstance(comprobante, Factura) else "Boleta"
            concepto = f"{tipo_comp} {comprobante.numero_completo} - {comprobante.cliente.razon_social}"
            multiplicador = 1
        
        # Crear asiento contable
        asiento = AsientoContable.objects.create(
            empresa_id=self.empresa_id,
            numero_asiento=self._generar_numero_asiento(),
            fecha_asiento=comprobante.fecha_emision,
            tipo_asiento='VENTA',
            concepto=concepto,
            documento_referencia=comprobante.numero_completo,
            periodo=self.periodo_actual,
            moneda=comprobante.moneda,
            tipo_cambio=comprobante.tipo_cambio,
            total_debe=comprobante.total * multiplicador if multiplicador == 1 else Decimal('0'),
            total_haber=comprobante.total * abs(multiplicador) if multiplicador == -1 else Decimal('0'),
            usuario_creacion_id=getattr(comprobante, 'usuario_creacion_id', None)
        )
        
        # Detalles del asiento
        detalles = []
        
        if not es_nota_credito:
            # Asiento normal de venta
            # DEBE: Cuentas por Cobrar
            detalles.append({
                'cuenta': cuenta_por_cobrar,
                'debe': comprobante.total,
                'haber': Decimal('0'),
                'concepto': f"Por venta según {comprobante.numero_completo}"
            })
            
            # HABER: Ventas
            detalles.append({
                'cuenta': cuenta_ventas,
                'debe': Decimal('0'),
                'haber': comprobante.subtotal,
                'concepto': f"Venta de mercaderías según {comprobante.numero_completo}"
            })
            
            # HABER: IGV por Pagar
            if comprobante.igv > 0:
                detalles.append({
                    'cuenta': cuenta_igv,
                    'debe': Decimal('0'),
                    'haber': comprobante.igv,
                    'concepto': f"IGV por pagar según {comprobante.numero_completo}"
                })
        else:
            # Asiento de nota de crédito (inverso)
            # HABER: Cuentas por Cobrar
            detalles.append({
                'cuenta': cuenta_por_cobrar,
                'debe': Decimal('0'),
                'haber': comprobante.total,
                'concepto': f"Por anulación según {comprobante.numero_completo}"
            })
            
            # DEBE: Ventas
            detalles.append({
                'cuenta': cuenta_ventas,
                'debe': comprobante.subtotal,
                'haber': Decimal('0'),
                'concepto': f"Anulación venta según {comprobante.numero_completo}"
            })
            
            # DEBE: IGV por Pagar
            if comprobante.igv > 0:
                detalles.append({
                    'cuenta': cuenta_igv,
                    'debe': comprobante.igv,
                    'haber': Decimal('0'),
                    'concepto': f"Anulación IGV según {comprobante.numero_completo}"
                })
        
        # Crear detalles del asiento
        self._crear_detalles_asiento(asiento, detalles)
        
        # Validar que el asiento cuadre
        self._validar_asiento_cuadrado(asiento)
        
        # Marcar asiento como contabilizado
        asiento.estado = 'CONTABILIZADO'
        asiento.save()
        
        # Generar cuenta por cobrar si es venta
        if not es_nota_credito and isinstance(comprobante, (Factura, Boleta)):
            self._generar_cuenta_por_cobrar(comprobante, asiento)
        elif es_nota_credito:
            self._aplicar_nota_credito_cuenta_cobrar(comprobante, asiento)
        
        # Actualizar libro mayor
        self._actualizar_libro_mayor(asiento)
        
        logger.info(f"Asiento de venta generado exitosamente - ID: {asiento.id}")
        
        return asiento
    
    @transaction.atomic
    def generar_asiento_compra(
        self,
        factura_compra,
        cuentas_detalle: List[Dict] = None
    ) -> AsientoContable:
        """
        Generar asiento contable para compras
        
        Asiento tipo para compras:
        DEBE: 60 Compras (subtotal)
        DEBE: 40 IGV por Acreditar (igv)
        HABER: 42 Cuentas por Pagar (total)
        
        Args:
            factura_compra: Datos de la factura de compra
            cuentas_detalle: Detalle de cuentas personalizadas
            
        Returns:
            AsientoContable: El asiento generado
        """
        logger.info(f"Generando asiento de compra para factura {factura_compra.get('numero')}")
        
        # Validar período activo
        fecha_compra = factura_compra.get('fecha_emision')
        if isinstance(fecha_compra, str):
            fecha_compra = datetime.strptime(fecha_compra, '%Y-%m-%d').date()
        
        self._validar_periodo_activo(fecha_compra)
        
        # Obtener cuentas contables
        cuenta_compras = self._obtener_cuenta_por_codigo('60111')     # Mercaderías
        cuenta_igv_acreditar = self._obtener_cuenta_por_codigo('40119')  # IGV por acreditar
        cuenta_por_pagar = self._obtener_cuenta_por_codigo('42111')   # Facturas por pagar
        
        # Crear asiento contable
        concepto = f"Compra según factura {factura_compra.get('numero')} - {factura_compra.get('proveedor_nombre')}"
        
        asiento = AsientoContable.objects.create(
            empresa_id=self.empresa_id,
            numero_asiento=self._generar_numero_asiento(),
            fecha_asiento=fecha_compra,
            tipo_asiento='COMPRA',
            concepto=concepto,
            documento_referencia=factura_compra.get('numero'),
            periodo=self.periodo_actual,
            moneda=factura_compra.get('moneda', 'PEN'),
            tipo_cambio=Decimal(str(factura_compra.get('tipo_cambio', 1.0))),
            total_debe=Decimal(str(factura_compra.get('total'))),
            total_haber=Decimal(str(factura_compra.get('total'))),
            usuario_creacion_id=factura_compra.get('usuario_id')
        )
        
        # Detalles del asiento
        detalles = []
        
        # DEBE: Compras
        if cuentas_detalle:
            # Usar cuentas personalizadas
            for detalle in cuentas_detalle:
                cuenta = self._obtener_cuenta_por_codigo(detalle['codigo_cuenta'])
                detalles.append({
                    'cuenta': cuenta,
                    'debe': Decimal(str(detalle['importe'])),
                    'haber': Decimal('0'),
                    'concepto': detalle.get('concepto', f"Compra según factura {factura_compra.get('numero')}")
                })
        else:
            # Usar cuenta de compras general
            detalles.append({
                'cuenta': cuenta_compras,
                'debe': Decimal(str(factura_compra.get('subtotal'))),
                'haber': Decimal('0'),
                'concepto': f"Compra de mercaderías según factura {factura_compra.get('numero')}"
            })
        
        # DEBE: IGV por Acreditar
        igv = Decimal(str(factura_compra.get('igv', 0)))
        if igv > 0:
            detalles.append({
                'cuenta': cuenta_igv_acreditar,
                'debe': igv,
                'haber': Decimal('0'),
                'concepto': f"IGV por acreditar según factura {factura_compra.get('numero')}"
            })
        
        # HABER: Cuentas por Pagar
        detalles.append({
            'cuenta': cuenta_por_pagar,
            'debe': Decimal('0'),
            'haber': Decimal(str(factura_compra.get('total'))),
            'concepto': f"Por compra según factura {factura_compra.get('numero')}"
        })
        
        # Crear detalles del asiento
        self._crear_detalles_asiento(asiento, detalles)
        
        # Validar que el asiento cuadre
        self._validar_asiento_cuadrado(asiento)
        
        # Marcar asiento como contabilizado
        asiento.estado = 'CONTABILIZADO'
        asiento.save()
        
        # Generar cuenta por pagar
        self._generar_cuenta_por_pagar(factura_compra, asiento)
        
        # Actualizar libro mayor
        self._actualizar_libro_mayor(asiento)
        
        logger.info(f"Asiento de compra generado exitosamente - ID: {asiento.id}")
        
        return asiento
    
    @transaction.atomic
    def generar_asiento_pago(
        self,
        pago_data: Dict
    ) -> AsientoContable:
        """
        Generar asiento contable para pagos
        
        Asiento tipo para pago a proveedor:
        DEBE: 42 Cuentas por Pagar
        HABER: 10 Efectivo y Equivalentes
        
        Args:
            pago_data: Datos del pago
            
        Returns:
            AsientoContable: El asiento generado
        """
        logger.info(f"Generando asiento de pago por {pago_data.get('monto')}")
        
        # Validar período activo
        fecha_pago = pago_data.get('fecha_pago')
        if isinstance(fecha_pago, str):
            fecha_pago = datetime.strptime(fecha_pago, '%Y-%m-%d').date()
        
        self._validar_periodo_activo(fecha_pago)
        
        # Obtener cuentas contables
        cuenta_por_pagar = self._obtener_cuenta_por_codigo('42111')   # Facturas por pagar
        
        # Determinar cuenta de efectivo según medio de pago
        medio_pago = pago_data.get('medio_pago', 'EFECTIVO')
        if medio_pago == 'EFECTIVO':
            cuenta_efectivo = self._obtener_cuenta_por_codigo('10111')  # Caja
        elif medio_pago == 'BANCO':
            cuenta_efectivo = self._obtener_cuenta_por_codigo('10411')  # Cuentas corrientes
        else:
            cuenta_efectivo = self._obtener_cuenta_por_codigo('10111')  # Por defecto caja
        
        # Crear asiento contable
        concepto = f"Pago a {pago_data.get('proveedor_nombre')} - {pago_data.get('documento_referencia', '')}"
        
        asiento = AsientoContable.objects.create(
            empresa_id=self.empresa_id,
            numero_asiento=self._generar_numero_asiento(),
            fecha_asiento=fecha_pago,
            tipo_asiento='PAGO',
            concepto=concepto,
            documento_referencia=pago_data.get('documento_referencia', ''),
            periodo=self.periodo_actual,
            moneda=pago_data.get('moneda', 'PEN'),
            tipo_cambio=Decimal(str(pago_data.get('tipo_cambio', 1.0))),
            total_debe=Decimal(str(pago_data.get('monto'))),
            total_haber=Decimal(str(pago_data.get('monto'))),
            usuario_creacion_id=pago_data.get('usuario_id')
        )
        
        # Detalles del asiento
        detalles = [
            {
                'cuenta': cuenta_por_pagar,
                'debe': Decimal(str(pago_data.get('monto'))),
                'haber': Decimal('0'),
                'concepto': f"Pago a {pago_data.get('proveedor_nombre')}"
            },
            {
                'cuenta': cuenta_efectivo,
                'debe': Decimal('0'),
                'haber': Decimal(str(pago_data.get('monto'))),
                'concepto': f"Pago por {medio_pago.lower()}"
            }
        ]
        
        # Crear detalles del asiento
        self._crear_detalles_asiento(asiento, detalles)
        
        # Validar que el asiento cuadre
        self._validar_asiento_cuadrado(asiento)
        
        # Marcar asiento como contabilizado
        asiento.estado = 'CONTABILIZADO'
        asiento.save()
        
        # Actualizar cuenta por pagar
        self._actualizar_cuenta_por_pagar(pago_data, asiento)
        
        # Actualizar libro mayor
        self._actualizar_libro_mayor(asiento)
        
        logger.info(f"Asiento de pago generado exitosamente - ID: {asiento.id}")
        
        return asiento
    
    @transaction.atomic
    def generar_asiento_cobro(
        self,
        cobro_data: Dict
    ) -> AsientoContable:
        """
        Generar asiento contable para cobros
        
        Asiento tipo para cobro a cliente:
        DEBE: 10 Efectivo y Equivalentes
        HABER: 12 Cuentas por Cobrar
        
        Args:
            cobro_data: Datos del cobro
            
        Returns:
            AsientoContable: El asiento generado
        """
        logger.info(f"Generando asiento de cobro por {cobro_data.get('monto')}")
        
        # Validar período activo
        fecha_cobro = cobro_data.get('fecha_cobro')
        if isinstance(fecha_cobro, str):
            fecha_cobro = datetime.strptime(fecha_cobro, '%Y-%m-%d').date()
        
        self._validar_periodo_activo(fecha_cobro)
        
        # Obtener cuentas contables
        cuenta_por_cobrar = self._obtener_cuenta_por_codigo('12111')  # Facturas por cobrar
        
        # Determinar cuenta de efectivo según medio de cobro
        medio_cobro = cobro_data.get('medio_cobro', 'EFECTIVO')
        if medio_cobro == 'EFECTIVO':
            cuenta_efectivo = self._obtener_cuenta_por_codigo('10111')  # Caja
        elif medio_cobro == 'BANCO':
            cuenta_efectivo = self._obtener_cuenta_por_codigo('10411')  # Cuentas corrientes
        else:
            cuenta_efectivo = self._obtener_cuenta_por_codigo('10111')  # Por defecto caja
        
        # Crear asiento contable
        concepto = f"Cobro de {cobro_data.get('cliente_nombre')} - {cobro_data.get('documento_referencia', '')}"
        
        asiento = AsientoContable.objects.create(
            empresa_id=self.empresa_id,
            numero_asiento=self._generar_numero_asiento(),
            fecha_asiento=fecha_cobro,
            tipo_asiento='COBRO',
            concepto=concepto,
            documento_referencia=cobro_data.get('documento_referencia', ''),
            periodo=self.periodo_actual,
            moneda=cobro_data.get('moneda', 'PEN'),
            tipo_cambio=Decimal(str(cobro_data.get('tipo_cambio', 1.0))),
            total_debe=Decimal(str(cobro_data.get('monto'))),
            total_haber=Decimal(str(cobro_data.get('monto'))),
            usuario_creacion_id=cobro_data.get('usuario_id')
        )
        
        # Detalles del asiento
        detalles = [
            {
                'cuenta': cuenta_efectivo,
                'debe': Decimal(str(cobro_data.get('monto'))),
                'haber': Decimal('0'),
                'concepto': f"Cobro por {medio_cobro.lower()}"
            },
            {
                'cuenta': cuenta_por_cobrar,
                'debe': Decimal('0'),
                'haber': Decimal(str(cobro_data.get('monto'))),
                'concepto': f"Cobro de {cobro_data.get('cliente_nombre')}"
            }
        ]
        
        # Crear detalles del asiento
        self._crear_detalles_asiento(asiento, detalles)
        
        # Validar que el asiento cuadre
        self._validar_asiento_cuadrado(asiento)
        
        # Marcar asiento como contabilizado
        asiento.estado = 'CONTABILIZADO'
        asiento.save()
        
        # Actualizar cuenta por cobrar
        self._actualizar_cuenta_por_cobrar(cobro_data, asiento)
        
        # Actualizar libro mayor
        self._actualizar_libro_mayor(asiento)
        
        logger.info(f"Asiento de cobro generado exitosamente - ID: {asiento.id}")
        
        return asiento
    
    # =============================================================================
    # MÉTODOS DE CONSULTA Y REPORTES
    # =============================================================================
    
    def generar_balance_comprobacion(
        self,
        fecha_desde: date,
        fecha_hasta: date,
        nivel_cuenta: int = 2
    ) -> Dict:
        """
        Generar balance de comprobación
        
        Args:
            fecha_desde: Fecha de inicio
            fecha_hasta: Fecha de fin
            nivel_cuenta: Nivel de cuenta a mostrar (2, 3, 4, etc.)
            
        Returns:
            Dict: Balance de comprobación
        """
        logger.info(f"Generando balance de comprobación desde {fecha_desde} hasta {fecha_hasta}")
        
        # Obtener movimientos del período
        movimientos = DetalleAsiento.objects.filter(
            asiento__fecha_asiento__range=[fecha_desde, fecha_hasta],
            asiento__estado='CONTABILIZADO'
        ).select_related('cuenta', 'asiento')
        
        # Agrupar por cuenta
        cuentas_balance = {}
        
        for movimiento in movimientos:
            codigo_cuenta = movimiento.cuenta.codigo_cuenta[:nivel_cuenta + 1]
            
            if codigo_cuenta not in cuentas_balance:
                cuenta_padre = PlanCuentas.objects.filter(
                    codigo_cuenta=codigo_cuenta
                ).first()
                
                cuentas_balance[codigo_cuenta] = {
                    'codigo': codigo_cuenta,
                    'nombre': cuenta_padre.nombre_cuenta if cuenta_padre else 'Sin nombre',
                    'saldo_inicial': Decimal('0'),
                    'debe': Decimal('0'),
                    'haber': Decimal('0'),
                    'saldo_final': Decimal('0')
                }
            
            cuentas_balance[codigo_cuenta]['debe'] += movimiento.debe
            cuentas_balance[codigo_cuenta]['haber'] += movimiento.haber
        
        # Calcular saldos finales
        total_debe = Decimal('0')
        total_haber = Decimal('0')
        
        for cuenta in cuentas_balance.values():
            cuenta['saldo_final'] = cuenta['debe'] - cuenta['haber']
            total_debe += cuenta['debe']
            total_haber += cuenta['haber']
        
        # Ordenar por código de cuenta
        cuentas_ordenadas = sorted(cuentas_balance.values(), key=lambda x: x['codigo'])
        
        return {
            'periodo': {
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta
            },
            'cuentas': cuentas_ordenadas,
            'totales': {
                'total_debe': total_debe,
                'total_haber': total_haber,
                'diferencia': total_debe - total_haber
            },
            'cuadrado': total_debe == total_haber
        }
    
    def generar_estado_resultados(
        self,
        fecha_desde: date,
        fecha_hasta: date
    ) -> Dict:
        """
        Generar estado de resultados básico
        
        Args:
            fecha_desde: Fecha de inicio
            fecha_hasta: Fecha de fin
            
        Returns:
            Dict: Estado de resultados
        """
        logger.info(f"Generando estado de resultados desde {fecha_desde} hasta {fecha_hasta}")
        
        # Consultar movimientos por grupos de cuentas
        movimientos = DetalleAsiento.objects.filter(
            asiento__fecha_asiento__range=[fecha_desde, fecha_hasta],
            asiento__estado='CONTABILIZADO'
        ).select_related('cuenta')
        
        # Inicializar totales
        ventas_netas = Decimal('0')
        costo_ventas = Decimal('0')
        gastos_operativos = Decimal('0')
        gastos_financieros = Decimal('0')
        otros_ingresos = Decimal('0')
        
        # Procesar movimientos por tipo de cuenta
        for movimiento in movimientos:
            codigo = movimiento.cuenta.codigo_cuenta
            
            # Ventas (70)
            if codigo.startswith('70'):
                ventas_netas += movimiento.haber - movimiento.debe
            
            # Costo de ventas (69)
            elif codigo.startswith('69'):
                costo_ventas += movimiento.debe - movimiento.haber
            
            # Gastos operativos (63, 64, 65, 66, 67)
            elif codigo.startswith(('63', '64', '65', '66', '67')):
                gastos_operativos += movimiento.debe - movimiento.haber
            
            # Gastos financieros (67)
            elif codigo.startswith('67'):
                gastos_financieros += movimiento.debe - movimiento.haber
            
            # Otros ingresos (75, 76, 77)
            elif codigo.startswith(('75', '76', '77')):
                otros_ingresos += movimiento.haber - movimiento.debe
        
        # Calcular resultados
        utilidad_bruta = ventas_netas - costo_ventas
        utilidad_operativa = utilidad_bruta - gastos_operativos
        utilidad_antes_impuestos = utilidad_operativa - gastos_financieros + otros_ingresos
        
        # Impuesto a la renta (estimado al 29.5%)
        impuesto_renta = utilidad_antes_impuestos * Decimal('0.295') if utilidad_antes_impuestos > 0 else Decimal('0')
        utilidad_neta = utilidad_antes_impuestos - impuesto_renta
        
        return {
            'periodo': {
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta
            },
            'ingresos': {
                'ventas_netas': ventas_netas,
                'otros_ingresos': otros_ingresos,
                'total_ingresos': ventas_netas + otros_ingresos
            },
            'costos_gastos': {
                'costo_ventas': costo_ventas,
                'gastos_operativos': gastos_operativos,
                'gastos_financieros': gastos_financieros,
                'total_costos_gastos': costo_ventas + gastos_operativos + gastos_financieros
            },
            'resultados': {
                'utilidad_bruta': utilidad_bruta,
                'utilidad_operativa': utilidad_operativa,
                'utilidad_antes_impuestos': utilidad_antes_impuestos,
                'impuesto_renta': impuesto_renta,
                'utilidad_neta': utilidad_neta
            },
            'ratios': {
                'margen_bruto': (utilidad_bruta / ventas_netas * 100) if ventas_netas > 0 else Decimal('0'),
                'margen_operativo': (utilidad_operativa / ventas_netas * 100) if ventas_netas > 0 else Decimal('0'),
                'margen_neto': (utilidad_neta / ventas_netas * 100) if ventas_netas > 0 else Decimal('0')
            }
        }
    
    # =============================================================================
    # MÉTODOS PRIVADOS
    # =============================================================================
    
    def _obtener_periodo_actual(self) -> PeriodoContable:
        """Obtener el período contable actual"""
        try:
            return PeriodoContable.objects.get(
                año=date.today().year,
                activo=True
            )
        except PeriodoContable.DoesNotExist:
            # Crear período automáticamente si no existe
            return PeriodoContable.objects.create(
                año=date.today().year,
                fecha_inicio=date(date.today().year, 1, 1),
                fecha_fin=date(date.today().year, 12, 31),
                activo=True
            )
    
    def _validar_periodo_activo(self, fecha: date):
        """Validar que la fecha esté en un período activo"""
        if not self.periodo_actual.activo:
            raise PeriodoInactivoError("El período contable no está activo")
        
        if not (self.periodo_actual.fecha_inicio <= fecha <= self.periodo_actual.fecha_fin):
            raise PeriodoInactivoError(f"La fecha {fecha} no está en el período contable activo")
    
    def _obtener_cuenta_por_codigo(self, codigo: str) -> PlanCuentas:
        """Obtener cuenta contable por código"""
        try:
            return PlanCuentas.objects.get(codigo_cuenta=codigo)
        except PlanCuentas.DoesNotExist:
            raise CuentaNoEncontradaError(f"No se encontró la cuenta con código {codigo}")
    
    def _generar_numero_asiento(self) -> str:
        """Generar número correlativo de asiento"""
        ultimo_asiento = AsientoContable.objects.filter(
            periodo=self.periodo_actual
        ).order_by('-numero_asiento').first()
        
        if ultimo_asiento:
            try:
                numero = int(ultimo_asiento.numero_asiento.split('-')[-1]) + 1
            except (ValueError, IndexError):
                numero = 1
        else:
            numero = 1
        
        return f"AS-{self.periodo_actual.año}-{numero:06d}"
    
    def _crear_detalles_asiento(self, asiento: AsientoContable, detalles: List[Dict]):
        """Crear detalles del asiento contable"""
        for detalle in detalles:
            DetalleAsiento.objects.create(
                asiento=asiento,
                cuenta=detalle['cuenta'],
                debe=detalle['debe'],
                haber=detalle['haber'],
                concepto=detalle['concepto'],
                moneda=asiento.moneda,
                tipo_cambio=asiento.tipo_cambio
            )
    
    def _validar_asiento_cuadrado(self, asiento: AsientoContable):
        """Validar que el asiento cuadre"""
        detalles = asiento.detalles.all()
        
        total_debe = sum(detalle.debe for detalle in detalles)
        total_haber = sum(detalle.haber for detalle in detalles)
        
        if total_debe != total_haber:
            raise AsientoDescuadradoError(
                f"El asiento no cuadra. Debe: {total_debe}, Haber: {total_haber}"
            )
        
        # Actualizar totales del asiento
        asiento.total_debe = total_debe
        asiento.total_haber = total_haber
        asiento.save()
    
    def _generar_cuenta_por_cobrar(self, comprobante, asiento: AsientoContable):
        """Generar cuenta por cobrar automática"""
        CuentaPorCobrar.objects.create(
            cliente=comprobante.cliente,
            tipo_documento=comprobante._meta.verbose_name,
            numero_documento=comprobante.numero_completo,
            fecha_emision=comprobante.fecha_emision,
            fecha_vencimiento=comprobante.fecha_vencimiento or comprobante.fecha_emision,
            monto_original=comprobante.total,
            monto_pendiente=comprobante.total,
            moneda=comprobante.moneda,
            asiento=asiento,
            estado='PENDIENTE'
        )
    
    def _aplicar_nota_credito_cuenta_cobrar(self, nota_credito, asiento: AsientoContable):
        """Aplicar nota de crédito a cuenta por cobrar"""
        # Buscar cuenta por cobrar del documento modificado
        cuenta_cobrar = CuentaPorCobrar.objects.filter(
            numero_documento=f"{nota_credito.documento_modificado_serie}-{nota_credito.documento_modificado_numero:08d}",
            estado='PENDIENTE'
        ).first()
        
        if cuenta_cobrar:
            # Aplicar el monto de la nota de crédito
            cuenta_cobrar.monto_pendiente -= nota_credito.total
            
            if cuenta_cobrar.monto_pendiente <= 0:
                cuenta_cobrar.estado = 'CANCELADO'
                cuenta_cobrar.fecha_cancelacion = timezone.now().date()
            
            cuenta_cobrar.save()
    
    def _generar_cuenta_por_pagar(self, factura_compra: Dict, asiento: AsientoContable):
        """Generar cuenta por pagar automática"""
        fecha_vencimiento = factura_compra.get('fecha_vencimiento')
        if isinstance(fecha_vencimiento, str):
            fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
        elif not fecha_vencimiento:
            fecha_vencimiento = asiento.fecha_asiento
        
        CuentaPorPagar.objects.create(
            proveedor_nombre=factura_compra.get('proveedor_nombre'),
            proveedor_documento=factura_compra.get('proveedor_ruc'),
            tipo_documento='FACTURA',
            numero_documento=factura_compra.get('numero'),
            fecha_emision=asiento.fecha_asiento,
            fecha_vencimiento=fecha_vencimiento,
            monto_original=Decimal(str(factura_compra.get('total'))),
            monto_pendiente=Decimal(str(factura_compra.get('total'))),
            moneda=factura_compra.get('moneda', 'PEN'),
            asiento=asiento,
            estado='PENDIENTE'
        )
    
    def _actualizar_cuenta_por_pagar(self, pago_data: Dict, asiento: AsientoContable):
        """Actualizar cuenta por pagar con pago"""
        cuenta_pagar = CuentaPorPagar.objects.filter(
            numero_documento=pago_data.get('documento_referencia'),
            estado='PENDIENTE'
        ).first()
        
        if cuenta_pagar:
            monto_pago = Decimal(str(pago_data.get('monto')))
            cuenta_pagar.monto_pendiente -= monto_pago
            
            if cuenta_pagar.monto_pendiente <= 0:
                cuenta_pagar.estado = 'CANCELADO'
                cuenta_pagar.fecha_cancelacion = timezone.now().date()
            
            cuenta_pagar.save()
    
    def _actualizar_cuenta_por_cobrar(self, cobro_data: Dict, asiento: AsientoContable):
        """Actualizar cuenta por cobrar con cobro"""
        cuenta_cobrar = CuentaPorCobrar.objects.filter(
            numero_documento=cobro_data.get('documento_referencia'),
            estado='PENDIENTE'
        ).first()
        
        if cuenta_cobrar:
            monto_cobro = Decimal(str(cobro_data.get('monto')))
            cuenta_cobrar.monto_pendiente -= monto_cobro
            
            if cuenta_cobrar.monto_pendiente <= 0:
                cuenta_cobrar.estado = 'CANCELADO'
                cuenta_cobrar.fecha_cancelacion = timezone.now().date()
            
            cuenta_cobrar.save()
    
    def _actualizar_libro_mayor(self, asiento: AsientoContable):
        """Actualizar libro mayor con los movimientos del asiento"""
        for detalle in asiento.detalles.all():
            # Buscar o crear entrada en libro mayor
            libro_mayor, created = LibroMayor.objects.get_or_create(
                cuenta=detalle.cuenta,
                periodo=asiento.periodo,
                defaults={
                    'saldo_inicial': Decimal('0'),
                    'total_debe': Decimal('0'),
                    'total_haber': Decimal('0'),
                    'saldo_final': Decimal('0')
                }
            )
            
            # Actualizar totales
            libro_mayor.total_debe += detalle.debe
            libro_mayor.total_haber += detalle.haber
            libro_mayor.saldo_final = libro_mayor.saldo_inicial + libro_mayor.total_debe - libro_mayor.total_haber
            libro_mayor.save()


# =============================================================================
# FUNCIONES DE CONVENIENCIA
# =============================================================================
def generar_asiento_venta(comprobante, es_nota_credito: bool = False) -> AsientoContable:
    """
    Función de conveniencia para generar asiento de venta
    
    Args:
        comprobante: Instancia del comprobante
        es_nota_credito: Si es nota de crédito
        
    Returns:
        AsientoContable: El asiento generado
    """
    try:
        service = ContabilidadService()
        return service.generar_asiento_venta(comprobante, es_nota_credito)
    except Exception as e:
        logger.error(f"Error al generar asiento de venta: {e}")
        raise


def generar_asiento_compra(factura_compra: Dict) -> AsientoContable:
    """
    Función de conveniencia para generar asiento de compra
    
    Args:
        factura_compra: Datos de la factura de compra
        
    Returns:
        AsientoContable: El asiento generado
    """
    try:
        service = ContabilidadService()
        return service.generar_asiento_compra(factura_compra)
    except Exception as e:
        logger.error(f"Error al generar asiento de compra: {e}")
        raise


def obtener_balance_comprobacion(fecha_desde: date, fecha_hasta: date) -> Dict:
    """
    Función de conveniencia para obtener balance de comprobación
    
    Args:
        fecha_desde: Fecha de inicio
        fecha_hasta: Fecha de fin
        
    Returns:
        Dict: Balance de comprobación
    """
    try:
        service = ContabilidadService()
        return service.generar_balance_comprobacion(fecha_desde, fecha_hasta)
    except Exception as e:
        logger.error(f"Error al generar balance de comprobación: {e}")
        raise


def obtener_estado_resultados(fecha_desde: date, fecha_hasta: date) -> Dict:
    """
    Función de conveniencia para obtener estado de resultados
    
    Args:
        fecha_desde: Fecha de inicio
        fecha_hasta: Fecha de fin
        
    Returns:
        Dict: Estado de resultados
    """
    try:
        service = ContabilidadService()
        return service.generar_estado_resultados(fecha_desde, fecha_hasta)
    except Exception as e:
        logger.error(f"Error al generar estado de resultados: {e}")
        raise