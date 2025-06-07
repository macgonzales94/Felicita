"""
UTILS CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Utilidades y funciones auxiliares del módulo core
"""

import re
import requests
import json
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger('felicita.core')


# =============================================================================
# VALIDACIONES PERÚ
# =============================================================================
def validar_ruc_algoritmo(ruc):
    """
    Validar RUC usando el algoritmo oficial de SUNAT
    
    Args:
        ruc (str): Número de RUC a validar
        
    Returns:
        bool: True si el RUC es válido, False en caso contrario
    """
    if not ruc or len(ruc) != 11 or not ruc.isdigit():
        return False
    
    try:
        # Factores de multiplicación para cada posición
        factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        
        # Calcular suma ponderada
        suma = sum(int(ruc[i]) * factores[i] for i in range(10))
        
        # Calcular resto
        resto = suma % 11
        
        # Calcular dígito verificador
        digito_verificador = 11 - resto if resto >= 2 else resto
        
        # Comparar con el último dígito del RUC
        return digito_verificador == int(ruc[10])
        
    except (ValueError, IndexError):
        return False


def validar_dni_algoritmo(dni):
    """
    Validar DNI peruano (verificación básica de formato)
    
    Args:
        dni (str): Número de DNI a validar
        
    Returns:
        bool: True si el DNI tiene formato válido
    """
    if not dni or len(dni) != 8 or not dni.isdigit():
        return False
    
    # DNI no puede empezar con 0
    if dni.startswith('0'):
        return False
    
    return True


def validar_ruc_sunat(ruc):
    """
    Consultar RUC en SUNAT a través de API externa
    
    Args:
        ruc (str): Número de RUC a consultar
        
    Returns:
        dict: Datos del RUC si existe, None si no existe o hay error
    """
    if not validar_ruc_algoritmo(ruc):
        return None
    
    # Verificar cache primero
    cache_key = f"ruc_sunat_{ruc}"
    datos_cached = cache.get(cache_key)
    if datos_cached:
        return datos_cached
    
    try:
        # Configurar API de consulta
        api_url = getattr(settings, 'SUNAT_API_URL', None)
        api_token = getattr(settings, 'SUNAT_API_TOKEN', None)
        
        if not api_url or not api_token:
            logger.warning("API de SUNAT no configurada")
            return None
        
        # Realizar consulta
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{api_url}?numero={ruc}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            datos = response.json()
            
            # Formatear respuesta
            resultado = {
                'ruc': ruc,
                'razon_social': datos.get('razonSocial', ''),
                'nombre_comercial': datos.get('nombreComercial', ''),
                'estado': datos.get('estado', ''),
                'condicion': datos.get('condicion', ''),
                'direccion': datos.get('direccion', ''),
                'ubigeo': datos.get('ubigeo', ''),
                'tipo_contribuyente': datos.get('tipoContribuyente', ''),
                'fecha_inscripcion': datos.get('fechaInscripcion', ''),
                'fecha_inicio_actividades': datos.get('fechaInicioActividades', ''),
                'actividades_economicas': datos.get('actividadEconomica', []),
                'comprobantes_pago': datos.get('comprobantesPago', []),
                'consulta_timestamp': timezone.now().isoformat()
            }
            
            # Guardar en cache por 24 horas
            cache.set(cache_key, resultado, timeout=86400)
            
            return resultado
        
        elif response.status_code == 404:
            logger.info(f"RUC {ruc} no encontrado en SUNAT")
            return None
        
        else:
            logger.error(f"Error consultando RUC {ruc} en SUNAT: {response.status_code}")
            return None
            
    except requests.RequestException as e:
        logger.error(f"Error de conexión consultando RUC {ruc}: {e}")
        return None
    
    except Exception as e:
        logger.error(f"Error inesperado consultando RUC {ruc}: {e}")
        return None


def validar_dni_reniec(dni):
    """
    Consultar DNI en RENIEC a través de API externa
    
    Args:
        dni (str): Número de DNI a consultar
        
    Returns:
        dict: Datos del DNI si existe, None si no existe o hay error
    """
    if not validar_dni_algoritmo(dni):
        return None
    
    # Verificar cache primero
    cache_key = f"dni_reniec_{dni}"
    datos_cached = cache.get(cache_key)
    if datos_cached:
        return datos_cached
    
    try:
        # Configurar API de consulta
        api_url = getattr(settings, 'RENIEC_API_URL', None)
        api_token = getattr(settings, 'RENIEC_API_TOKEN', None)
        
        if not api_url or not api_token:
            logger.warning("API de RENIEC no configurada")
            return None
        
        # Realizar consulta
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{api_url}?numero={dni}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            datos = response.json()
            
            # Formatear respuesta
            resultado = {
                'dni': dni,
                'nombres': datos.get('nombres', ''),
                'apellido_paterno': datos.get('apellidoPaterno', ''),
                'apellido_materno': datos.get('apellidoMaterno', ''),
                'nombre_completo': f"{datos.get('nombres', '')} {datos.get('apellidoPaterno', '')} {datos.get('apellidoMaterno', '')}".strip(),
                'consulta_timestamp': timezone.now().isoformat()
            }
            
            # Guardar en cache por 7 días
            cache.set(cache_key, resultado, timeout=604800)
            
            return resultado
        
        elif response.status_code == 404:
            logger.info(f"DNI {dni} no encontrado en RENIEC")
            return None
        
        else:
            logger.error(f"Error consultando DNI {dni} en RENIEC: {response.status_code}")
            return None
            
    except requests.RequestException as e:
        logger.error(f"Error de conexión consultando DNI {dni}: {e}")
        return None
    
    except Exception as e:
        logger.error(f"Error inesperado consultando DNI {dni}: {e}")
        return None


# =============================================================================
# UTILIDADES DE FORMATO
# =============================================================================
def formatear_ruc(ruc):
    """
    Formatear RUC para visualización
    
    Args:
        ruc (str): RUC sin formato
        
    Returns:
        str: RUC formateado (XX-XXXXXXXX-X)
    """
    if not ruc or len(ruc) != 11:
        return ruc
    
    return f"{ruc[:2]}-{ruc[2:10]}-{ruc[10]}"


def formatear_dni(dni):
    """
    Formatear DNI para visualización
    
    Args:
        dni (str): DNI sin formato
        
    Returns:
        str: DNI formateado (XXXX-XXXX)
    """
    if not dni or len(dni) != 8:
        return dni
    
    return f"{dni[:4]}-{dni[4:]}"


def formatear_telefono(telefono):
    """
    Formatear teléfono peruano
    
    Args:
        telefono (str): Teléfono sin formato
        
    Returns:
        str: Teléfono formateado
    """
    if not telefono:
        return telefono
    
    # Limpiar teléfono
    telefono_limpio = re.sub(r'[^\d]', '', telefono)
    
    # Formatear según longitud
    if len(telefono_limpio) == 9:  # Celular
        return f"{telefono_limpio[:3]}-{telefono_limpio[3:6]}-{telefono_limpio[6:]}"
    elif len(telefono_limpio) == 7:  # Fijo Lima
        return f"{telefono_limpio[:3]}-{telefono_limpio[3:]}"
    elif len(telefono_limpio) == 8:  # Fijo provincia
        return f"{telefono_limpio[:2]}-{telefono_limpio[2:6]}-{telefono_limpio[6:]}"
    
    return telefono


def formatear_moneda(monto, simbolo="S/", decimales=2):
    """
    Formatear monto como moneda peruana
    
    Args:
        monto (float|Decimal): Monto a formatear
        simbolo (str): Símbolo de moneda
        decimales (int): Número de decimales
        
    Returns:
        str: Monto formateado
    """
    if monto is None:
        return f"{simbolo} 0.00"
    
    try:
        # Convertir a Decimal para precisión
        if not isinstance(monto, Decimal):
            monto = Decimal(str(monto))
        
        # Redondear a los decimales especificados
        factor = Decimal(10) ** decimales
        monto_redondeado = monto.quantize(Decimal(1) / factor, rounding=ROUND_HALF_UP)
        
        # Formatear con separadores de miles
        formato = f"{{:,.{decimales}f}}"
        monto_formateado = formato.format(float(monto_redondeado))
        
        return f"{simbolo} {monto_formateado}"
        
    except (ValueError, TypeError):
        return f"{simbolo} 0.00"


def formatear_porcentaje(valor, decimales=2):
    """
    Formatear valor como porcentaje
    
    Args:
        valor (float|Decimal): Valor a formatear
        decimales (int): Número de decimales
        
    Returns:
        str: Porcentaje formateado
    """
    if valor is None:
        return "0.00%"
    
    try:
        if not isinstance(valor, Decimal):
            valor = Decimal(str(valor))
        
        formato = f"{{:.{decimales}f}}"
        return formato.format(float(valor)) + "%"
        
    except (ValueError, TypeError):
        return "0.00%"


# =============================================================================
# UTILIDADES DE CÁLCULO
# =============================================================================
def calcular_igv(monto_base, porcentaje_igv=None):
    """
    Calcular IGV de un monto base
    
    Args:
        monto_base (Decimal): Monto base sin IGV
        porcentaje_igv (Decimal): Porcentaje de IGV (default: 18%)
        
    Returns:
        Decimal: Monto del IGV
    """
    if porcentaje_igv is None:
        porcentaje_igv = Decimal('18.00')
    
    if not isinstance(monto_base, Decimal):
        monto_base = Decimal(str(monto_base))
    
    if not isinstance(porcentaje_igv, Decimal):
        porcentaje_igv = Decimal(str(porcentaje_igv))
    
    igv = monto_base * (porcentaje_igv / Decimal('100'))
    return igv.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_precio_con_igv(precio_sin_igv, porcentaje_igv=None):
    """
    Calcular precio con IGV incluido
    
    Args:
        precio_sin_igv (Decimal): Precio sin IGV
        porcentaje_igv (Decimal): Porcentaje de IGV
        
    Returns:
        Decimal: Precio con IGV incluido
    """
    igv = calcular_igv(precio_sin_igv, porcentaje_igv)
    precio_con_igv = precio_sin_igv + igv
    return precio_con_igv.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_precio_sin_igv(precio_con_igv, porcentaje_igv=None):
    """
    Calcular precio sin IGV desde precio con IGV
    
    Args:
        precio_con_igv (Decimal): Precio con IGV incluido
        porcentaje_igv (Decimal): Porcentaje de IGV
        
    Returns:
        Decimal: Precio sin IGV
    """
    if porcentaje_igv is None:
        porcentaje_igv = Decimal('18.00')
    
    if not isinstance(precio_con_igv, Decimal):
        precio_con_igv = Decimal(str(precio_con_igv))
    
    if not isinstance(porcentaje_igv, Decimal):
        porcentaje_igv = Decimal(str(porcentaje_igv))
    
    factor = Decimal('1') + (porcentaje_igv / Decimal('100'))
    precio_sin_igv = precio_con_igv / factor
    
    return precio_sin_igv.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_descuento(precio_base, porcentaje_descuento):
    """
    Calcular monto de descuento
    
    Args:
        precio_base (Decimal): Precio base
        porcentaje_descuento (Decimal): Porcentaje de descuento
        
    Returns:
        Decimal: Monto del descuento
    """
    if not isinstance(precio_base, Decimal):
        precio_base = Decimal(str(precio_base))
    
    if not isinstance(porcentaje_descuento, Decimal):
        porcentaje_descuento = Decimal(str(porcentaje_descuento))
    
    descuento = precio_base * (porcentaje_descuento / Decimal('100'))
    return descuento.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


# =============================================================================
# UTILIDADES DE FECHA
# =============================================================================
def obtener_fecha_hora_peru():
    """
    Obtener fecha y hora actual en zona horaria de Perú
    
    Returns:
        datetime: Fecha y hora en Perú
    """
    import pytz
    
    zona_peru = pytz.timezone('America/Lima')
    return timezone.now().astimezone(zona_peru)


def formatear_fecha_peru(fecha, formato=None):
    """
    Formatear fecha según estándar peruano
    
    Args:
        fecha (datetime): Fecha a formatear
        formato (str): Formato personalizado
        
    Returns:
        str: Fecha formateada
    """
    if not fecha:
        return ""
    
    if formato is None:
        formato = "%d/%m/%Y"
    
    return fecha.strftime(formato)


def formatear_fecha_hora_peru(fecha_hora, formato=None):
    """
    Formatear fecha y hora según estándar peruano
    
    Args:
        fecha_hora (datetime): Fecha y hora a formatear
        formato (str): Formato personalizado
        
    Returns:
        str: Fecha y hora formateada
    """
    if not fecha_hora:
        return ""
    
    if formato is None:
        formato = "%d/%m/%Y %H:%M"
    
    return fecha_hora.strftime(formato)


# =============================================================================
# UTILIDADES DE CÓDIGO
# =============================================================================
def generar_codigo_producto(categoria_codigo=None, secuencial=None):
    """
    Generar código de producto automático
    
    Args:
        categoria_codigo (str): Código de categoría
        secuencial (int): Número secuencial
        
    Returns:
        str: Código de producto generado
    """
    if categoria_codigo and secuencial:
        return f"{categoria_codigo}{secuencial:04d}"
    
    # Si no se proporcionan parámetros, generar basado en timestamp
    timestamp = int(timezone.now().timestamp())
    return f"PROD{timestamp}"


def generar_codigo_cliente(tipo_documento="CLI", secuencial=None):
    """
    Generar código de cliente automático
    
    Args:
        tipo_documento (str): Tipo de documento
        secuencial (int): Número secuencial
        
    Returns:
        str: Código de cliente generado
    """
    if secuencial:
        return f"{tipo_documento}{secuencial:06d}"
    
    # Si no se proporciona secuencial, usar timestamp
    timestamp = int(timezone.now().timestamp())
    return f"{tipo_documento}{timestamp}"


# =============================================================================
# UTILIDADES DE VALIDACIÓN DE DATOS
# =============================================================================
def limpiar_texto(texto):
    """
    Limpiar texto removiendo caracteres especiales
    
    Args:
        texto (str): Texto a limpiar
        
    Returns:
        str: Texto limpio
    """
    if not texto:
        return ""
    
    # Remover caracteres especiales pero conservar acentos
    texto_limpio = re.sub(r'[^\w\s\-\.áéíóúüñÁÉÍÓÚÜÑ]', '', texto)
    
    # Normalizar espacios
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    
    return texto_limpio.strip()


def normalizar_email(email):
    """
    Normalizar dirección de email
    
    Args:
        email (str): Email a normalizar
        
    Returns:
        str: Email normalizado
    """
    if not email:
        return ""
    
    # Convertir a minúsculas y limpiar espacios
    email_normalizado = email.lower().strip()
    
    # Validar formato básico
    if '@' not in email_normalizado or '.' not in email_normalizado:
        return email_normalizado
    
    return email_normalizado


def validar_email_formato(email):
    """
    Validar formato de email
    
    Args:
        email (str): Email a validar
        
    Returns:
        bool: True si el formato es válido
    """
    if not email:
        return False
    
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))


# =============================================================================
# UTILIDADES DE CONVERSIÓN
# =============================================================================
def convertir_a_decimal(valor, decimales=2):
    """
    Convertir valor a Decimal con precisión especificada
    
    Args:
        valor: Valor a convertir
        decimales (int): Número de decimales
        
    Returns:
        Decimal: Valor convertido
    """
    if valor is None:
        return Decimal('0')
    
    try:
        if isinstance(valor, Decimal):
            return valor.quantize(Decimal(10) ** -decimales, rounding=ROUND_HALF_UP)
        
        decimal_valor = Decimal(str(valor))
        return decimal_valor.quantize(Decimal(10) ** -decimales, rounding=ROUND_HALF_UP)
        
    except (ValueError, TypeError):
        return Decimal('0')


def convertir_a_entero(valor):
    """
    Convertir valor a entero de forma segura
    
    Args:
        valor: Valor a convertir
        
    Returns:
        int: Valor convertido
    """
    if valor is None:
        return 0
    
    try:
        return int(float(valor))
    except (ValueError, TypeError):
        return 0


# =============================================================================
# UTILIDADES DE LOGGING
# =============================================================================
def log_actividad_usuario(usuario, accion, modulo, descripcion, objeto_id=None):
    """
    Registrar actividad de usuario para auditoría
    
    Args:
        usuario: Usuario que realiza la acción
        accion (str): Tipo de acción
        modulo (str): Módulo donde se realiza la acción
        descripcion (str): Descripción de la acción
        objeto_id (str): ID del objeto afectado
    """
    try:
        from aplicaciones.usuarios.models import LogActividadUsuario
        
        LogActividadUsuario.objects.create(
            usuario=usuario,
            accion=accion,
            modulo=modulo,
            descripcion=descripcion,
            objeto_id=str(objeto_id) if objeto_id else "",
            ip_address=getattr(usuario, '_ip_address', '127.0.0.1'),
            datos_adicionales={}
        )
        
    except Exception as e:
        logger.error(f"Error registrando actividad de usuario: {e}")


# =============================================================================
# UTILIDADES DE CACHÉ
# =============================================================================
def limpiar_cache_modelo(modelo_nombre):
    """
    Limpiar cache relacionado con un modelo específico
    
    Args:
        modelo_nombre (str): Nombre del modelo
    """
    try:
        # Obtener claves de cache relacionadas
        pattern = f"{modelo_nombre}_*"
        
        # En Redis se puede usar pattern, en otros backends hay que iterar
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
        else:
            # Implementación alternativa para otros backends
            logger.info(f"Cache pattern delete no disponible para {modelo_nombre}")
            
    except Exception as e:
        logger.error(f"Error limpiando cache para {modelo_nombre}: {e}")


def obtener_configuracion_cache(clave, valor_defecto=None, timeout=3600):
    """
    Obtener configuración con cache
    
    Args:
        clave (str): Clave de configuración
        valor_defecto: Valor por defecto
        timeout (int): Tiempo de cache en segundos
        
    Returns:
        Valor de configuración
    """
    cache_key = f"config_{clave}"
    valor = cache.get(cache_key)
    
    if valor is None:
        try:
            from .models import ConfiguracionSistema
            config = ConfiguracionSistema.objects.get(clave=clave)
            valor = config.valor
            cache.set(cache_key, valor, timeout=timeout)
        except Exception:
            valor = valor_defecto
    
    return valor