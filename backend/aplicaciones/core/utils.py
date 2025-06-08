"""
UTILS CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Funciones auxiliares y utilidades para todo el sistema
"""

import re
import uuid
import hashlib
import random
import string
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Union, Optional, Dict, Any, List
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
import requests
import logging

logger = logging.getLogger('felicita.core')


# =============================================================================
# VALIDACIONES DOCUMENTOS PERÚ
# =============================================================================
def validar_ruc(ruc: str) -> bool:
    """
    Validar RUC peruano (11 dígitos)
    Implementa algoritmo oficial de SUNAT
    """
    if not ruc or not isinstance(ruc, str):
        return False
    
    # Limpiar RUC
    ruc = ruc.strip().replace('-', '').replace(' ', '')
    
    # Verificar que sea solo números y tenga 11 dígitos
    if not ruc.isdigit() or len(ruc) != 11:
        return False
    
    # Tipos de RUC válidos (primer dígito)
    tipos_validos = ['1', '2']  # 10: DNI, 20: RUC empresa
    if ruc[:2] not in ['10', '20', '15', '17']:
        return False
    
    # Algoritmo de validación
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = 0
    
    for i in range(10):
        suma += int(ruc[i]) * factores[i]
    
    resto = suma % 11
    digito_verificador = 11 - resto if resto >= 2 else resto
    
    return int(ruc[10]) == digito_verificador


def validar_dni(dni: str) -> bool:
    """
    Validar DNI peruano (8 dígitos)
    """
    if not dni or not isinstance(dni, str):
        return False
    
    # Limpiar DNI
    dni = dni.strip().replace('-', '').replace(' ', '')
    
    # Verificar que sea solo números y tenga 8 dígitos
    if not dni.isdigit() or len(dni) != 8:
        return False
    
    # Verificar que no sea un número obviamente inválido
    if dni == '00000000' or dni == '11111111':
        return False
    
    return True


def validar_numero_documento(numero: str, tipo_documento: str) -> bool:
    """
    Validar número de documento según su tipo
    """
    if not numero or not tipo_documento:
        return False
    
    numero = numero.strip()
    
    if tipo_documento == 'DNI':
        return validar_dni(numero)
    elif tipo_documento == 'RUC':
        return validar_ruc(numero)
    elif tipo_documento == 'CARNET_EXTRANJERIA':
        # Carnet de extranjería: 9 dígitos
        return numero.isdigit() and len(numero) == 9
    elif tipo_documento == 'PASAPORTE':
        # Pasaporte: entre 6 y 12 caracteres alfanuméricos
        return re.match(r'^[A-Z0-9]{6,12}$', numero.upper()) is not None
    
    return False


# =============================================================================
# CONSULTAS APIS EXTERNAS
# =============================================================================
def consultar_ruc_sunat(ruc: str) -> Optional[Dict[str, Any]]:
    """
    Consultar datos de RUC en SUNAT (simulado)
    En producción se conectaría a API real de SUNAT
    """
    if not validar_ruc(ruc):
        return None
    
    # Datos simulados para desarrollo
    datos_simulados = {
        '20100070970': {
            'ruc': '20100070970',
            'razon_social': 'SUPERMERCADOS PERUANOS SOCIEDAD ANONIMA',
            'nombre_comercial': 'PLAZA VEA',
            'estado': 'ACTIVO',
            'condicion': 'HABIDO',
            'direccion': 'AV. ARGENTINA NRO. 3093',
            'distrito': 'LIMA',
            'provincia': 'LIMA',
            'departamento': 'LIMA',
            'ubigeo': '150101'
        },
        '20131312955': {
            'ruc': '20131312955',
            'razon_social': 'CENCOSUD RETAIL PERU S.A.',
            'nombre_comercial': 'METRO',
            'estado': 'ACTIVO',
            'condicion': 'HABIDO',
            'direccion': 'AV. AVIACION NRO. 5405',
            'distrito': 'SAN BORJA',
            'provincia': 'LIMA',
            'departamento': 'LIMA',
            'ubigeo': '150141'
        }
    }
    
    return datos_simulados.get(ruc)


def consultar_dni_reniec(dni: str) -> Optional[Dict[str, Any]]:
    """
    Consultar datos de DNI en RENIEC (simulado)
    En producción se conectaría a API real de RENIEC
    """
    if not validar_dni(dni):
        return None
    
    # Datos simulados para desarrollo
    datos_simulados = {
        '12345678': {
            'dni': '12345678',
            'nombres': 'JUAN CARLOS',
            'apellido_paterno': 'PEREZ',
            'apellido_materno': 'GARCIA',
            'estado_civil': 'SOLTERO',
            'fecha_nacimiento': '1990-05-15'
        },
        '87654321': {
            'dni': '87654321',
            'nombres': 'MARIA ELENA',
            'apellido_paterno': 'RODRIGUEZ',
            'apellido_materno': 'LOPEZ',
            'estado_civil': 'CASADA',
            'fecha_nacimiento': '1985-12-20'
        }
    }
    
    return datos_simulados.get(dni)


# =============================================================================
# UTILIDADES FINANCIERAS
# =============================================================================
def calcular_igv(monto_base: Union[Decimal, float], tasa_igv: float = 0.18) -> Decimal:
    """
    Calcular IGV sobre un monto base
    """
    if not isinstance(monto_base, Decimal):
        monto_base = Decimal(str(monto_base))
    
    igv = monto_base * Decimal(str(tasa_igv))
    return igv.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_total_con_igv(monto_base: Union[Decimal, float], tasa_igv: float = 0.18) -> Decimal:
    """
    Calcular total incluyendo IGV
    """
    if not isinstance(monto_base, Decimal):
        monto_base = Decimal(str(monto_base))
    
    igv = calcular_igv(monto_base, tasa_igv)
    total = monto_base + igv
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_base_sin_igv(monto_con_igv: Union[Decimal, float], tasa_igv: float = 0.18) -> Decimal:
    """
    Calcular monto base sin IGV a partir de monto con IGV
    """
    if not isinstance(monto_con_igv, Decimal):
        monto_con_igv = Decimal(str(monto_con_igv))
    
    factor = Decimal('1') + Decimal(str(tasa_igv))
    monto_base = monto_con_igv / factor
    return monto_base.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def redondear_moneda(monto: Union[Decimal, float]) -> Decimal:
    """
    Redondear monto a 2 decimales para moneda
    """
    if not isinstance(monto, Decimal):
        monto = Decimal(str(monto))
    
    return monto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def convertir_numero_a_letras(numero: Union[int, float, Decimal]) -> str:
    """
    Convertir número a letras (para facturas)
    """
    # Implementación básica - en producción usar librería como num2words
    if not isinstance(numero, (int, float, Decimal)):
        return ""
    
    # Por ahora retorna formato simple
    return f"{numero:.2f} SOLES"


# =============================================================================
# UTILIDADES DE FECHAS
# =============================================================================
def obtener_fecha_actual() -> date:
    """
    Obtener fecha actual del sistema
    """
    return timezone.now().date()


def obtener_datetime_actual() -> datetime:
    """
    Obtener datetime actual del sistema
    """
    return timezone.now()


def formatear_fecha_peru(fecha: Union[date, datetime]) -> str:
    """
    Formatear fecha al formato peruano (DD/MM/YYYY)
    """
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    
    return fecha.strftime('%d/%m/%Y')


def formatear_datetime_peru(dt: datetime) -> str:
    """
    Formatear datetime al formato peruano (DD/MM/YYYY HH:MM)
    """
    return dt.strftime('%d/%m/%Y %H:%M')


def validar_fecha_formato(fecha_str: str, formato: str = '%Y-%m-%d') -> bool:
    """
    Validar si una fecha string tiene el formato correcto
    """
    try:
        datetime.strptime(fecha_str, formato)
        return True
    except ValueError:
        return False


def calcular_edad(fecha_nacimiento: date) -> int:
    """
    Calcular edad en años
    """
    hoy = obtener_fecha_actual()
    edad = hoy.year - fecha_nacimiento.year
    
    # Ajustar si aún no ha cumplido años este año
    if hoy.month < fecha_nacimiento.month or \
       (hoy.month == fecha_nacimiento.month and hoy.day < fecha_nacimiento.day):
        edad -= 1
    
    return edad


# =============================================================================
# UTILIDADES DE STRINGS
# =============================================================================
def limpiar_texto(texto: str) -> str:
    """
    Limpiar texto eliminando caracteres especiales y espacios extra
    """
    if not texto:
        return ""
    
    # Eliminar espacios extra
    texto = re.sub(r'\s+', ' ', texto.strip())
    
    # Eliminar caracteres especiales problemáticos
    texto = re.sub(r'[^\w\s\-.,()áéíóúÁÉÍÓÚñÑ]', '', texto)
    
    return texto


def normalizar_email(email: str) -> str:
    """
    Normalizar email a minúsculas y sin espacios
    """
    if not email:
        return ""
    
    return email.strip().lower()


def generar_codigo_unico(prefijo: str = "", longitud: int = 8) -> str:
    """
    Generar código único alfanumérico
    """
    caracteres = string.ascii_uppercase + string.digits
    codigo = ''.join(random.choices(caracteres, k=longitud))
    
    if prefijo:
        return f"{prefijo}-{codigo}"
    
    return codigo


def validar_email_formato(email: str) -> bool:
    """
    Validar formato de email
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
    return re.match(patron, email) is not None


def validar_telefono_peru(telefono: str) -> bool:
    """
    Validar número de teléfono peruano
    """
    if not telefono:
        return False
    
    # Limpiar número
    telefono = re.sub(r'\D', '', telefono)
    
    # Formatos válidos:
    # Celular: 9 dígitos (empezando con 9)
    # Fijo Lima: 7 dígitos (empezando con 1-9)
    # Fijo provincia: 6 dígitos
    
    if len(telefono) == 9 and telefono.startswith('9'):
        return True
    elif len(telefono) == 7 and telefono[0] in '123456789':
        return True
    elif len(telefono) == 6:
        return True
    
    return False


# =============================================================================
# UTILIDADES DE ARCHIVOS
# =============================================================================
def validar_extension_archivo(nombre_archivo: str, extensiones_permitidas: List[str]) -> bool:
    """
    Validar extensión de archivo
    """
    if not nombre_archivo:
        return False
    
    extension = nombre_archivo.lower().split('.')[-1]
    return extension in [ext.lower() for ext in extensiones_permitidas]


def generar_nombre_archivo_unico(nombre_original: str) -> str:
    """
    Generar nombre único para archivo
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre, extension = nombre_original.rsplit('.', 1) if '.' in nombre_original else (nombre_original, '')
    
    nombre_limpio = re.sub(r'[^\w\-_.]', '_', nombre)
    codigo_unico = generar_codigo_unico("", 6)
    
    if extension:
        return f"{nombre_limpio}_{timestamp}_{codigo_unico}.{extension}"
    else:
        return f"{nombre_limpio}_{timestamp}_{codigo_unico}"


def calcular_hash_archivo(archivo_path: str) -> str:
    """
    Calcular hash MD5 de un archivo
    """
    hash_md5 = hashlib.md5()
    try:
        with open(archivo_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except FileNotFoundError:
        return ""


# =============================================================================
# UTILIDADES DE VALIDACIÓN
# =============================================================================
def validar_rango_numero(numero: Union[int, float], minimo: Union[int, float], maximo: Union[int, float]) -> bool:
    """
    Validar que un número esté en un rango específico
    """
    return minimo <= numero <= maximo


def validar_longitud_texto(texto: str, minimo: int = 0, maximo: int = None) -> bool:
    """
    Validar longitud de texto
    """
    if not texto:
        texto = ""
    
    longitud = len(texto)
    
    if longitud < minimo:
        return False
    
    if maximo is not None and longitud > maximo:
        return False
    
    return True


def es_numero_valido(valor: str) -> bool:
    """
    Verificar si un string representa un número válido
    """
    try:
        float(valor)
        return True
    except (ValueError, TypeError):
        return False


# =============================================================================
# UTILIDADES DE UBIGEO PERÚ
# =============================================================================
def obtener_ubigeo_lima() -> str:
    """
    Obtener código de ubigeo de Lima
    """
    return "150101"  # Lima, Lima, Lima


def validar_ubigeo(ubigeo: str) -> bool:
    """
    Validar formato de ubigeo peruano (6 dígitos)
    """
    if not ubigeo:
        return False
    
    return ubigeo.isdigit() and len(ubigeo) == 6


def obtener_departamento_por_ubigeo(ubigeo: str) -> str:
    """
    Obtener nombre del departamento por código de ubigeo
    """
    if not validar_ubigeo(ubigeo):
        return ""
    
    # Primeros 2 dígitos son el código del departamento
    codigo_departamento = ubigeo[:2]
    
    departamentos = {
        '01': 'AMAZONAS',
        '02': 'ANCASH',
        '03': 'APURIMAC',
        '04': 'AREQUIPA',
        '05': 'AYACUCHO',
        '06': 'CAJAMARCA',
        '07': 'CALLAO',
        '08': 'CUSCO',
        '09': 'HUANCAVELICA',
        '10': 'HUANUCO',
        '11': 'ICA',
        '12': 'JUNIN',
        '13': 'LA LIBERTAD',
        '14': 'LAMBAYEQUE',
        '15': 'LIMA',
        '16': 'LORETO',
        '17': 'MADRE DE DIOS',
        '18': 'MOQUEGUA',
        '19': 'PASCO',
        '20': 'PIURA',
        '21': 'PUNO',
        '22': 'SAN MARTIN',
        '23': 'TACNA',
        '24': 'TUMBES',
        '25': 'UCAYALI'
    }
    
    return departamentos.get(codigo_departamento, "")


# =============================================================================
# UTILIDADES DE LOGGING Y DEBUG
# =============================================================================
def log_actividad_usuario(usuario, accion: str, modulo: str, descripcion: str = "", ip_address: str = ""):
    """
    Registrar actividad del usuario en el log
    """
    try:
        from aplicaciones.usuarios.models import LogActividadUsuario
        
        LogActividadUsuario.objects.create(
            usuario=usuario,
            accion=accion,
            modulo=modulo,
            descripcion=descripcion,
            ip_address=ip_address
        )
    except Exception as e:
        logger.error(f"Error al registrar log de actividad: {e}")


def generar_id_transaccion() -> str:
    """
    Generar ID único para transacciones
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    codigo = generar_codigo_unico("", 6)
    return f"TXN-{timestamp}-{codigo}"


def validar_json_estructura(data: Dict, campos_requeridos: List[str]) -> tuple[bool, List[str]]:
    """
    Validar que un diccionario tenga los campos requeridos
    """
    campos_faltantes = []
    
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None:
            campos_faltantes.append(campo)
    
    return len(campos_faltantes) == 0, campos_faltantes


# =============================================================================
# UTILIDADES DE CONFIGURACIÓN
# =============================================================================
def obtener_configuracion(clave: str, valor_por_defecto: Any = None) -> Any:
    """
    Obtener valor de configuración del sistema
    """
    return getattr(settings, clave, valor_por_defecto)


def es_ambiente_desarrollo() -> bool:
    """
    Verificar si estamos en ambiente de desarrollo
    """
    return obtener_configuracion('DEBUG', False)


def es_ambiente_produccion() -> bool:
    """
    Verificar si estamos en ambiente de producción
    """
    return not es_ambiente_desarrollo()


# =============================================================================
# UTILIDADES DE FACTURACIÓN ELECTRÓNICA
# =============================================================================
def generar_numero_serie_factura(tipo_documento: str = "01") -> str:
    """
    Generar número de serie para documentos electrónicos
    Formato: LNNN (L=letra, N=número)
    """
    # F001, F002, etc. para facturas
    # B001, B002, etc. para boletas
    
    prefijos = {
        "01": "F",  # Factura
        "03": "B",  # Boleta
        "07": "N",  # Nota de crédito
        "08": "D"   # Nota de débito
    }
    
    prefijo = prefijos.get(tipo_documento, "F")
    numero = random.randint(1, 999)
    
    return f"{prefijo}{numero:03d}"


def validar_numero_correlativo(correlativo: str) -> bool:
    """
    Validar formato de número correlativo (máximo 8 dígitos)
    """
    if not correlativo:
        return False
    
    return correlativo.isdigit() and 1 <= len(correlativo) <= 8


def formatear_numero_documento(serie: str, correlativo: Union[str, int]) -> str:
    """
    Formatear número completo de documento (serie-correlativo)
    """
    if isinstance(correlativo, int):
        correlativo = str(correlativo)
    
    return f"{serie}-{correlativo.zfill(8)}"


# =============================================================================
# UTILIDADES DE CONVERSIÓN
# =============================================================================
def convertir_texto_a_decimal(texto: str) -> Optional[Decimal]:
    """
    Convertir texto a Decimal de forma segura
    """
    if not texto:
        return None
    
    try:
        # Limpiar texto
        texto = texto.strip().replace(',', '.')
        return Decimal(texto)
    except (ValueError, TypeError):
        return None


def convertir_texto_a_entero(texto: str) -> Optional[int]:
    """
    Convertir texto a entero de forma segura
    """
    if not texto:
        return None
    
    try:
        return int(texto.strip())
    except (ValueError, TypeError):
        return None


def convertir_booleano_a_texto(valor: bool) -> str:
    """
    Convertir booleano a texto en español
    """
    return "Sí" if valor else "No"


# =============================================================================
# UTILIDADES DE PAGINACIÓN
# =============================================================================
def calcular_paginacion(total_items: int, items_por_pagina: int, pagina_actual: int) -> Dict[str, Any]:
    """
    Calcular información de paginación
    """
    if items_por_pagina <= 0:
        items_por_pagina = 10
    
    if pagina_actual <= 0:
        pagina_actual = 1
    
    total_paginas = (total_items + items_por_pagina - 1) // items_por_pagina
    
    if pagina_actual > total_paginas:
        pagina_actual = total_paginas if total_paginas > 0 else 1
    
    inicio = (pagina_actual - 1) * items_por_pagina
    fin = min(inicio + items_por_pagina, total_items)
    
    return {
        'total_items': total_items,
        'items_por_pagina': items_por_pagina,
        'pagina_actual': pagina_actual,
        'total_paginas': total_paginas,
        'inicio': inicio,
        'fin': fin,
        'tiene_siguiente': pagina_actual < total_paginas,
        'tiene_anterior': pagina_actual > 1
    }