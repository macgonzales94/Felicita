"""
SERVICIO NUBEFACT - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Integración completa con API de Nubefact para emisión de comprobantes electrónicos
"""

import requests
import json
import logging
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger('felicita.nubefact')


# =============================================================================
# EXCEPCIONES PERSONALIZADAS
# =============================================================================
class NubefactError(Exception):
    """Error base para Nubefact"""
    pass


class NubefactConnectionError(NubefactError):
    """Error de conexión con Nubefact"""
    pass


class NubefactValidationError(NubefactError):
    """Error de validación de datos"""
    pass


class NubefactSunatError(NubefactError):
    """Error devuelto por SUNAT"""
    pass


# =============================================================================
# SERVICIO PRINCIPAL NUBEFACT
# =============================================================================
class NubefactService:
    """
    Servicio para integración completa con Nubefact
    """
    
    def __init__(self):
        """Inicializar configuración de Nubefact"""
        self.config = settings.NUBEFACT_CONFIG
        self.base_url = self._get_base_url()
        self.token = self.config.get('token')
        self.ruc = self.config.get('ruc')
        self.timeout = self.config.get('timeout_conexion', 30)
        self.max_reintentos = self.config.get('max_reintentos', 3)
        
        # Headers por defecto
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'FELICITA/1.0'
        }
        
        logger.info(f"NubefactService inicializado - Modo: {self.config.get('modo')}")
    
    def _get_base_url(self) -> str:
        """Obtener URL base según ambiente"""
        if self.config.get('modo') == 'demo':
            return self.config.get('demo_url', 'https://demo.nubefact.com/api/v1/')
        return self.config.get('base_url', 'https://api.nubefact.com/api/v1/')
    
    def _hacer_request(self, method: str, endpoint: str, data: dict = None, retry_count: int = 0) -> dict:
        """
        Realizar request HTTP con reintentos automáticos
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Request {method} a {url}")
            
            if self.config.get('log_requests', False):
                logger.debug(f"Request data: {json.dumps(data, indent=2) if data else 'None'}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            
            # Log de response
            if self.config.get('log_responses', False):
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response data: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            
            # Verificar si Nubefact devolvió error
            if isinstance(result, dict) and result.get('errors'):
                error_msg = f"Error Nubefact: {result['errors']}"
                logger.error(error_msg)
                raise NubefactValidationError(error_msg)
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout en request a {url}")
            if retry_count < self.max_reintentos:
                logger.info(f"Reintentando... {retry_count + 1}/{self.max_reintentos}")
                return self._hacer_request(method, endpoint, data, retry_count + 1)
            raise NubefactConnectionError("Timeout en conexión con Nubefact")
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión: {e}")
            if retry_count < self.max_reintentos:
                logger.info(f"Reintentando... {retry_count + 1}/{self.max_reintentos}")
                return self._hacer_request(method, endpoint, data, retry_count + 1)
            raise NubefactConnectionError(f"Error de conexión: {e}")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP {response.status_code}: {response.text}")
            
            if response.status_code >= 500:
                # Error del servidor, reintentar
                if retry_count < self.max_reintentos:
                    logger.info(f"Reintentando... {retry_count + 1}/{self.max_reintentos}")
                    return self._hacer_request(method, endpoint, data, retry_count + 1)
            
            raise NubefactError(f"Error HTTP {response.status_code}: {response.text}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar JSON: {e}")
            raise NubefactError(f"Respuesta inválida de Nubefact: {e}")
    
    # =============================================================================
    # MÉTODOS PÚBLICOS - EMISIÓN DE COMPROBANTES
    # =============================================================================
    
    def emitir_factura(self, factura_data: dict) -> dict:
        """
        Emitir factura a través de Nubefact
        """
        logger.info(f"Emitiendo factura {factura_data.get('serie', '')}-{factura_data.get('numero', '')}")
        
        # Validar datos requeridos
        self._validar_datos_factura(factura_data)
        
        # Transformar datos al formato Nubefact
        nubefact_data = self._transformar_factura_a_nubefact(factura_data)
        
        # Enviar a Nubefact
        try:
            response = self._hacer_request('POST', 'issue/invoice', nubefact_data)
            
            logger.info(f"Factura emitida exitosamente: {response.get('invoice_id')}")
            
            # Procesar respuesta
            return self._procesar_respuesta_emision(response, 'factura')
            
        except Exception as e:
            logger.error(f"Error al emitir factura: {e}")
            raise
    
    def emitir_boleta(self, boleta_data: dict) -> dict:
        """
        Emitir boleta de venta a través de Nubefact
        """
        logger.info(f"Emitiendo boleta {boleta_data.get('serie', '')}-{boleta_data.get('numero', '')}")
        
        # Validar datos requeridos
        self._validar_datos_boleta(boleta_data)
        
        # Transformar datos al formato Nubefact
        nubefact_data = self._transformar_boleta_a_nubefact(boleta_data)
        
        # Enviar a Nubefact
        try:
            response = self._hacer_request('POST', 'issue/bill', nubefact_data)
            
            logger.info(f"Boleta emitida exitosamente: {response.get('invoice_id')}")
            
            return self._procesar_respuesta_emision(response, 'boleta')
            
        except Exception as e:
            logger.error(f"Error al emitir boleta: {e}")
            raise
    
    def emitir_nota_credito(self, nota_data: dict) -> dict:
        """
        Emitir nota de crédito a través de Nubefact
        """
        logger.info(f"Emitiendo nota de crédito {nota_data.get('serie', '')}-{nota_data.get('numero', '')}")
        
        # Validar datos requeridos
        self._validar_datos_nota_credito(nota_data)
        
        # Transformar datos al formato Nubefact
        nubefact_data = self._transformar_nota_credito_a_nubefact(nota_data)
        
        # Enviar a Nubefact
        try:
            response = self._hacer_request('POST', 'issue/credit_note', nubefact_data)
            
            logger.info(f"Nota de crédito emitida exitosamente: {response.get('invoice_id')}")
            
            return self._procesar_respuesta_emision(response, 'nota_credito')
            
        except Exception as e:
            logger.error(f"Error al emitir nota de crédito: {e}")
            raise
    
    def comunicacion_baja(self, documentos: List[dict]) -> dict:
        """
        Enviar comunicación de baja de documentos
        """
        logger.info(f"Enviando comunicación de baja para {len(documentos)} documentos")
        
        # Transformar datos para comunicación de baja
        baja_data = self._transformar_comunicacion_baja(documentos)
        
        try:
            response = self._hacer_request('POST', 'issue/void', baja_data)
            
            logger.info(f"Comunicación de baja enviada exitosamente: {response.get('ticket')}")
            
            return {
                'success': True,
                'ticket': response.get('ticket'),
                'fecha_envio': timezone.now(),
                'response_data': response
            }
            
        except Exception as e:
            logger.error(f"Error en comunicación de baja: {e}")
            raise
    
    # =============================================================================
    # MÉTODOS DE CONSULTA
    # =============================================================================
    
    def consultar_estado(self, invoice_id: str) -> dict:
        """
        Consultar estado de comprobante en SUNAT
        """
        logger.info(f"Consultando estado de comprobante: {invoice_id}")
        
        try:
            response = self._hacer_request('GET', f'query/status/{invoice_id}')
            
            return {
                'invoice_id': invoice_id,
                'estado_sunat': response.get('sunat_status'),
                'codigo_respuesta': response.get('sunat_code'),
                'mensaje_sunat': response.get('sunat_message'),
                'fecha_consulta': timezone.now(),
                'response_data': response
            }
            
        except Exception as e:
            logger.error(f"Error al consultar estado: {e}")
            raise
    
    def consultar_ticket(self, ticket: str) -> dict:
        """
        Consultar estado de ticket (para comunicaciones de baja)
        """
        logger.info(f"Consultando ticket: {ticket}")
        
        try:
            response = self._hacer_request('GET', f'query/ticket/{ticket}')
            
            return {
                'ticket': ticket,
                'estado': response.get('status'),
                'procesado': response.get('processed', False),
                'fecha_consulta': timezone.now(),
                'response_data': response
            }
            
        except Exception as e:
            logger.error(f"Error al consultar ticket: {e}")
            raise
    
    def descargar_xml(self, invoice_id: str) -> Optional[str]:
        """
        Descargar XML de comprobante
        """
        logger.info(f"Descargando XML: {invoice_id}")
        
        try:
            response = self._hacer_request('GET', f'download/xml/{invoice_id}')
            return response.get('xml_content')
            
        except Exception as e:
            logger.error(f"Error al descargar XML: {e}")
            return None
    
    def descargar_pdf(self, invoice_id: str) -> Optional[str]:
        """
        Descargar PDF de comprobante
        """
        logger.info(f"Descargando PDF: {invoice_id}")
        
        try:
            response = self._hacer_request('GET', f'download/pdf/{invoice_id}')
            return response.get('pdf_url')
            
        except Exception as e:
            logger.error(f"Error al descargar PDF: {e}")
            return None
    
    # =============================================================================
    # MÉTODOS PRIVADOS - TRANSFORMACIÓN DE DATOS
    # =============================================================================
    
    def _transformar_factura_a_nubefact(self, factura_data: dict) -> dict:
        """
        Transformar datos de factura al formato Nubefact
        """
        return {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": 1,  # Factura
            "serie": factura_data['serie'],
            "numero": factura_data['numero'],
            "sunat_transaction": 1,
            "cliente_tipo_de_documento": self._mapear_tipo_documento(factura_data['cliente']['tipo_documento']),
            "cliente_numero_de_documento": factura_data['cliente']['numero_documento'],
            "cliente_denominacion": factura_data['cliente']['razon_social'],
            "cliente_direccion": factura_data['cliente']['direccion'],
            "cliente_email": factura_data['cliente'].get('email', ''),
            "fecha_de_emision": factura_data['fecha_emision'],
            "fecha_de_vencimiento": factura_data.get('fecha_vencimiento', factura_data['fecha_emision']),
            "moneda": factura_data.get('moneda', 'PEN'),
            "tipo_de_cambio": float(factura_data.get('tipo_cambio', 1.0)),
            "porcentaje_de_igv": 18.00,
            "descuento_global": float(factura_data.get('descuento_global', 0)),
            "total_descuento": float(factura_data.get('descuento_global', 0)),
            "total_anticipo": 0.00,
            "total_gravada": float(factura_data['subtotal']),
            "total_inafecta": 0.00,
            "total_exonerada": 0.00,
            "total_igv": float(factura_data['igv']),
            "total_gratuita": 0.00,
            "total_otros_cargos": 0.00,
            "total": float(factura_data['total']),
            "enviar_automaticamente_a_la_sunat": True,
            "enviar_automaticamente_al_cliente": False,
            "codigo_unico": factura_data.get('codigo_unico', ''),
            "condiciones_de_pago": factura_data.get('condicion_pago', 'Contado'),
            "medio_de_pago": factura_data.get('medio_pago', 'Efectivo'),
            "items": [self._transformar_item_factura(item) for item in factura_data['items']]
        }
    
    def _transformar_boleta_a_nubefact(self, boleta_data: dict) -> dict:
        """
        Transformar datos de boleta al formato Nubefact
        """
        nubefact_data = self._transformar_factura_a_nubefact(boleta_data)
        nubefact_data["tipo_de_comprobante"] = 2  # Boleta
        return nubefact_data
    
    def _transformar_nota_credito_a_nubefact(self, nota_data: dict) -> dict:
        """
        Transformar datos de nota de crédito al formato Nubefact
        """
        return {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": 3,  # Nota de crédito
            "serie": nota_data['serie'],
            "numero": nota_data['numero'],
            "sunat_transaction": 1,
            "cliente_tipo_de_documento": self._mapear_tipo_documento(nota_data['cliente']['tipo_documento']),
            "cliente_numero_de_documento": nota_data['cliente']['numero_documento'],
            "cliente_denominacion": nota_data['cliente']['razon_social'],
            "cliente_direccion": nota_data['cliente']['direccion'],
            "fecha_de_emision": nota_data['fecha_emision'],
            "moneda": nota_data.get('moneda', 'PEN'),
            "tipo_de_cambio": float(nota_data.get('tipo_cambio', 1.0)),
            "porcentaje_de_igv": 18.00,
            "total_gravada": float(nota_data['subtotal']),
            "total_igv": float(nota_data['igv']),
            "total": float(nota_data['total']),
            "codigo_tipo_de_nota_de_credito": nota_data['codigo_motivo'],
            "descripcion_motivo": nota_data['descripcion_motivo'],
            "documento_que_se_modifica_tipo": nota_data['tipo_documento_modificado'],
            "documento_que_se_modifica_serie": nota_data['serie_documento_modificado'],
            "documento_que_se_modifica_numero": nota_data['numero_documento_modificado'],
            "enviar_automaticamente_a_la_sunat": True,
            "items": [self._transformar_item_factura(item) for item in nota_data['items']]
        }
    
    def _transformar_item_factura(self, item: dict) -> dict:
        """
        Transformar item de factura al formato Nubefact
        """
        return {
            "unidad_de_medida": item.get('unidad_medida', 'NIU'),
            "codigo": item['producto']['codigo'],
            "descripcion": item['descripcion'],
            "cantidad": float(item['cantidad']),
            "valor_unitario": float(item['precio_unitario']),
            "precio_unitario": float(item['precio_unitario']),
            "descuento": float(item.get('descuento', 0)),
            "subtotal": float(item['subtotal']),
            "tipo_de_igv": int(item.get('tipo_afectacion_igv', 1)),
            "igv": float(item['igv']),
            "total": float(item['total']),
            "anticipo_regularizacion": False,
            "anticipo_documento_serie": "",
            "anticipo_documento_numero": ""
        }
    
    def _transformar_comunicacion_baja(self, documentos: List[dict]) -> dict:
        """
        Transformar datos para comunicación de baja
        """
        fecha_baja = date.today().strftime('%Y-%m-%d')
        
        return {
            "operacion": "generar_comunicacion_de_baja",
            "fecha_de_emision": fecha_baja,
            "fecha_de_comunicacion": fecha_baja,
            "documentos": [
                {
                    "tipo_de_comprobante": doc['tipo_comprobante'],
                    "serie": doc['serie'],
                    "numero": doc['numero'],
                    "motivo": doc.get('motivo', 'Anulación por error'),
                    "codigo_motivo": doc.get('codigo_motivo', '01')
                }
                for doc in documentos
            ]
        }
    
    # =============================================================================
    # MÉTODOS DE VALIDACIÓN
    # =============================================================================
    
    def _validar_datos_factura(self, factura_data: dict) -> None:
        """
        Validar datos requeridos para factura
        """
        campos_requeridos = ['serie', 'numero', 'cliente', 'fecha_emision', 'items', 'subtotal', 'igv', 'total']
        
        for campo in campos_requeridos:
            if campo not in factura_data:
                raise NubefactValidationError(f"Campo requerido faltante: {campo}")
        
        # Validar cliente
        campos_cliente = ['tipo_documento', 'numero_documento', 'razon_social', 'direccion']
        for campo in campos_cliente:
            if campo not in factura_data['cliente']:
                raise NubefactValidationError(f"Campo de cliente requerido: {campo}")
        
        # Validar items
        if not factura_data['items']:
            raise NubefactValidationError("La factura debe tener al menos un item")
        
        # Validar totales
        self._validar_totales(factura_data)
    
    def _validar_datos_boleta(self, boleta_data: dict) -> None:
        """
        Validar datos requeridos para boleta
        """
        self._validar_datos_factura(boleta_data)  # Mismas validaciones que factura
    
    def _validar_datos_nota_credito(self, nota_data: dict) -> None:
        """
        Validar datos requeridos para nota de crédito
        """
        self._validar_datos_factura(nota_data)
        
        campos_adicionales = ['codigo_motivo', 'descripcion_motivo', 'tipo_documento_modificado', 
                             'serie_documento_modificado', 'numero_documento_modificado']
        
        for campo in campos_adicionales:
            if campo not in nota_data:
                raise NubefactValidationError(f"Campo requerido para nota de crédito: {campo}")
    
    def _validar_totales(self, data: dict) -> None:
        """
        Validar que los totales sean consistentes
        """
        subtotal = Decimal(str(data['subtotal']))
        igv = Decimal(str(data['igv']))
        total = Decimal(str(data['total']))
        descuento = Decimal(str(data.get('descuento_global', 0)))
        
        total_calculado = subtotal + igv - descuento
        
        if abs(total - total_calculado) > Decimal('0.01'):
            raise NubefactValidationError(f"Inconsistencia en totales: {total} != {total_calculado}")
        
        # Validar IGV (18%)
        igv_calculado = subtotal * Decimal('0.18')
        if abs(igv - igv_calculado) > Decimal('0.01'):
            raise NubefactValidationError(f"IGV incorrecto: {igv} != {igv_calculado}")
    
    # =============================================================================
    # MÉTODOS AUXILIARES
    # =============================================================================
    
    def _mapear_tipo_documento(self, tipo_documento: str) -> int:
        """
        Mapear tipo de documento a código Nubefact
        """
        mapeo = {
            'DNI': 1,
            'RUC': 6,
            'CE': 4,
            'PASSPORT': 7,
            'OTROS': 0
        }
        return mapeo.get(tipo_documento, 0)
    
    def _procesar_respuesta_emision(self, response: dict, tipo_comprobante: str) -> dict:
        """
        Procesar respuesta de emisión de comprobante
        """
        return {
            'success': True,
            'invoice_id': response.get('invoice_id'),
            'external_id': response.get('external_id'),
            'numero_completo': f"{response.get('serie', '')}-{response.get('numero', '')}",
            'estado_sunat': response.get('sunat_status', 'PENDIENTE'),
            'codigo_respuesta': response.get('sunat_code'),
            'mensaje_sunat': response.get('sunat_message'),
            'hash_documento': response.get('hash'),
            'fecha_emision': timezone.now(),
            'pdf_url': response.get('pdf_url'),
            'xml_url': response.get('xml_url'),
            'response_data': response,
            'tipo_comprobante': tipo_comprobante
        }
    
    def ping(self) -> bool:
        """
        Verificar conectividad con Nubefact
        """
        try:
            response = self._hacer_request('GET', 'ping')
            return response.get('status') == 'ok'
        except Exception as e:
            logger.error(f"Error en ping a Nubefact: {e}")
            return False


# =============================================================================
# INSTANCIA GLOBAL DEL SERVICIO
# =============================================================================
nubefact_service = NubefactService()


# =============================================================================
# FUNCIONES DE CONVENIENCIA
# =============================================================================
def emitir_factura_nubefact(factura_data: dict) -> dict:
    """Función de conveniencia para emitir factura"""
    return nubefact_service.emitir_factura(factura_data)


def emitir_boleta_nubefact(boleta_data: dict) -> dict:
    """Función de conveniencia para emitir boleta"""
    return nubefact_service.emitir_boleta(boleta_data)


def consultar_estado_nubefact(invoice_id: str) -> dict:
    """Función de conveniencia para consultar estado"""
    return nubefact_service.consultar_estado(invoice_id)


def verificar_conectividad_nubefact() -> bool:
    """Función de conveniencia para verificar conectividad"""
    return nubefact_service.ping()