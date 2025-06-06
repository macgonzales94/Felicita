"""
Utilidades para autenticación y seguridad en FELICITA
Sistema de Facturación Electrónica para Perú
"""

import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .models import Usuario, SesionUsuario, LogActividad, RolUsuario


logger = logging.getLogger('felicita')


# ==============================================
# UTILIDADES DE AUTENTICACIÓN
# ==============================================

def generar_password_temporal(longitud: int = 12) -> str:
    """
    Generar contraseña temporal segura
    """
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    password = ''.join(secrets.choice(caracteres) for _ in range(longitud))
    
    # Asegurar que tenga al menos un carácter de cada tipo
    if not any(c.islower() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_lowercase)
    if not any(c.isupper() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_uppercase)
    if not any(c.isdigit() for c in password):
        password = password[:-1] + secrets.choice(string.digits)
    
    return password


def validar_fortaleza_password(password: str) -> Dict[str, Any]:
    """
    Validar fortaleza de contraseña según estándares de FELICITA
    """
    errores = []
    fortaleza = 0
    
    # Longitud mínima
    if len(password) < 8:
        errores.append("La contraseña debe tener al menos 8 caracteres")
    else:
        fortaleza += 1
    
    # Al menos una minúscula
    if not any(c.islower() for c in password):
        errores.append("Debe contener al menos una letra minúscula")
    else:
        fortaleza += 1
    
    # Al menos una mayúscula
    if not any(c.isupper() for c in password):
        errores.append("Debe contener al menos una letra mayúscula")
    else:
        fortaleza += 1
    
    # Al menos un número
    if not any(c.isdigit() for c in password):
        errores.append("Debe contener al menos un número")
    else:
        fortaleza += 1
    
    # Al menos un carácter especial
    caracteres_especiales = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in caracteres_especiales for c in password):
        errores.append("Debe contener al menos un carácter especial")
    else:
        fortaleza += 1
    
    # Determinar nivel de fortaleza
    if fortaleza <= 2:
        nivel = "Débil"
    elif fortaleza <= 3:
        nivel = "Regular"
    elif fortaleza <= 4:
        nivel = "Buena"
    else:
        nivel = "Excelente"
    
    return {
        'valida': len(errores) == 0,
        'errores': errores,
        'fortaleza': fortaleza,
        'nivel': nivel,
        'porcentaje': (fortaleza / 5) * 100
    }


def crear_token_personalizado(usuario: Usuario) -> Dict[str, str]:
    """
    Crear tokens JWT personalizados para usuario
    """
    try:
        refresh = RefreshToken.for_user(usuario)
        access = refresh.access_token
        
        # Agregar claims personalizados
        access['empresa_id'] = usuario.empresa_id if usuario.empresa else None
        access['rol'] = usuario.rol
        access['permisos'] = usuario.permisos_especiales
        
        return {
            'access': str(access),
            'refresh': str(refresh),
            'expires_in': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        }
        
    except Exception as e:
        logger.error(f"Error creando token personalizado: {e}")
        raise


def verificar_token_valido(token: str) -> Dict[str, Any]:
    """
    Verificar si un token JWT es válido
    """
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        usuario = Usuario.objects.get(id=user_id)
        
        return {
            'valido': True,
            'usuario': usuario,
            'token_data': access_token.payload
        }
        
    except (InvalidToken, TokenError, Usuario.DoesNotExist):
        return {
            'valido': False,
            'usuario': None,
            'token_data': None
        }


def invalidar_todos_los_tokens_usuario(usuario: Usuario) -> None:
    """
    Invalidar todos los tokens de un usuario (cambio de password, etc.)
    """
    try:
        # Cerrar todas las sesiones activas
        SesionUsuario.objects.filter(usuario=usuario, activa=True).update(activa=False)
        
        # Agregar usuario a blacklist temporal en cache
        cache.set(f"usuario_blacklist:{usuario.id}", True, 3600)  # 1 hora
        
        logger.info(f"Tokens invalidados para usuario {usuario.username}")
        
    except Exception as e:
        logger.error(f"Error invalidando tokens: {e}")


# ==============================================
# UTILIDADES DE SESIONES
# ==============================================

def obtener_sesiones_activas_usuario(usuario: Usuario) -> List[SesionUsuario]:
    """
    Obtener sesiones activas de un usuario
    """
    return SesionUsuario.objects.filter(
        usuario=usuario,
        activa=True
    ).order_by('-fecha_ultimo_acceso')


def cerrar_sesiones_concurrentes(usuario: Usuario, sesion_actual: Optional[SesionUsuario] = None) -> int:
    """
    Cerrar sesiones concurrentes de un usuario (mantener solo una)
    """
    sesiones_activas = SesionUsuario.objects.filter(
        usuario=usuario,
        activa=True
    )
    
    if sesion_actual:
        sesiones_activas = sesiones_activas.exclude(id=sesion_actual.id)
    
    count = sesiones_activas.count()
    sesiones_activas.update(activa=False)
    
    return count


def limpiar_sesiones_expiradas() -> int:
    """
    Limpiar sesiones expiradas del sistema
    """
    timeout_minutos = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 120)
    tiempo_limite = timezone.now() - timedelta(minutes=timeout_minutos)
    
    sesiones_expiradas = SesionUsuario.objects.filter(
        activa=True,
        fecha_ultimo_acceso__lt=tiempo_limite
    )
    
    count = sesiones_expiradas.count()
    sesiones_expiradas.update(activa=False)
    
    return count


def obtener_estadisticas_sesiones() -> Dict[str, Any]:
    """
    Obtener estadísticas de sesiones del sistema
    """
    ahora = timezone.now()
    hace_24h = ahora - timedelta(hours=24)
    hace_7d = ahora - timedelta(days=7)
    
    return {
        'sesiones_activas_total': SesionUsuario.objects.filter(activa=True).count(),
        'sesiones_ultimas_24h': SesionUsuario.objects.filter(
            fecha_inicio__gte=hace_24h
        ).count(),
        'sesiones_ultimos_7d': SesionUsuario.objects.filter(
            fecha_inicio__gte=hace_7d
        ).count(),
        'usuarios_unicos_activos': SesionUsuario.objects.filter(
            activa=True
        ).values('usuario').distinct().count()
    }


# ==============================================
# UTILIDADES DE PERMISOS
# ==============================================

def verificar_permisos_usuario(usuario: Usuario, modulo: str, accion: str = 'ver') -> bool:
    """
    Verificar permisos de usuario para módulo y acción específica
    """
    if not usuario or not usuario.is_authenticated:
        return False
    
    # Superusuarios y administradores tienen acceso total
    if usuario.is_superuser or usuario.es_administrador():
        return True
    
    # Verificar permisos específicos
    return usuario.tiene_permiso(modulo, accion)


def obtener_permisos_usuario(usuario: Usuario) -> Dict[str, Dict[str, bool]]:
    """
    Obtener todos los permisos del usuario organizados por módulo
    """
    if not usuario or not usuario.is_authenticated:
        return {}
    
    if usuario.is_superuser or usuario.es_administrador():
        # Administradores tienen todos los permisos
        return {
            'facturacion': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
            'contabilidad': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
            'inventarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
            'productos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
            'clientes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
            'pos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
            'reportes': {'ver': True, 'exportar': True, 'ple': True},
            'configuraciones': {'ver': True, 'editar': True},
            'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True},
        }
    
    # Permisos según rol
    permisos_base = {
        RolUsuario.CONTADOR: {
            'facturacion': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
            'contabilidad': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
            'inventarios': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
            'productos': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
            'clientes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
            'pos': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
            'reportes': {'ver': True, 'exportar': True, 'ple': True},
            'configuraciones': {'ver': True, 'editar': False},
            'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
        },
        RolUsuario.VENDEDOR: {
            'facturacion': {'ver': True, 'crear': True, 'editar': False, 'eliminar': False},
            'contabilidad': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
            'inventarios': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
            'productos': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
            'clientes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
            'pos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
            'reportes': {'ver': True, 'exportar': False, 'ple': False},
            'configuraciones': {'ver': False, 'editar': False},
            'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
        },
        RolUsuario.CLIENTE: {
            'facturacion': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
            'contabilidad': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
            'inventarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
            'productos': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
            'clientes': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
            'pos': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
            'reportes': {'ver': False, 'exportar': False, 'ple': False},
            'configuraciones': {'ver': False, 'editar': False},
            'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False},
        }
    }
    
    # Obtener permisos base del rol
    permisos = permisos_base.get(usuario.rol, {})
    
    # Aplicar permisos especiales
    if usuario.permisos_especiales:
        for modulo, acciones in usuario.permisos_especiales.items():
            if modulo in permisos:
                permisos[modulo].update(acciones)
            else:
                permisos[modulo] = acciones
    
    return permisos


def actualizar_permisos_especiales(usuario: Usuario, modulo: str, permisos: Dict[str, bool]) -> None:
    """
    Actualizar permisos especiales de un usuario
    """
    if not usuario.permisos_especiales:
        usuario.permisos_especiales = {}
    
    usuario.permisos_especiales[modulo] = permisos
    usuario.save(update_fields=['permisos_especiales'])
    
    # Emitir signal de cambio de permisos
    from .signals import permiso_modificado
    permiso_modificado.send(
        sender=None,
        usuario_afectado=usuario,
        permiso_modificado=f"{modulo}: {permisos}",
        usuario_modificador=usuario  # Se puede pasar el usuario que hace el cambio
    )


# ==============================================
# UTILIDADES DE NOTIFICACIONES
# ==============================================

def enviar_notificacion_nuevo_usuario(usuario: Usuario, password_temporal: str = None) -> bool:
    """
    Enviar notificación de nuevo usuario creado
    """
    try:
        if not usuario.email:
            return False
        
        contexto = {
            'usuario': usuario,
            'password_temporal': password_temporal,
            'sistema_nombre': 'FELICITA',
            'empresa': usuario.empresa,
            'url_login': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000') + '/login'
        }
        
        asunto = f'Bienvenido a FELICITA - {usuario.empresa.razon_social if usuario.empresa else "Sistema"}'
        mensaje = render_to_string('emails/nuevo_usuario.html', contexto)
        
        resultado = send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email],
            html_message=mensaje,
            fail_silently=False
        )
        
        if resultado:
            LogActividad.registrar_actividad(
                usuario=usuario,
                accion='ENVIO_EMAIL_BIENVENIDA',
                modulo='NOTIFICACIONES',
                descripcion=f'Email de bienvenida enviado a {usuario.email}',
                direccion_ip='127.0.0.1'
            )
        
        return bool(resultado)
        
    except Exception as e:
        logger.error(f"Error enviando notificación nuevo usuario: {e}")
        return False


def enviar_notificacion_password_cambiado(usuario: Usuario) -> bool:
    """
    Enviar notificación de cambio de contraseña
    """
    try:
        if not usuario.email:
            return False
        
        contexto = {
            'usuario': usuario,
            'fecha_cambio': timezone.now(),
            'sistema_nombre': 'FELICITA'
        }
        
        asunto = 'FELICITA - Contraseña cambiada'
        mensaje = render_to_string('emails/password_cambiado.html', contexto)
        
        resultado = send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email],
            html_message=mensaje,
            fail_silently=False
        )
        
        return bool(resultado)
        
    except Exception as e:
        logger.error(f"Error enviando notificación cambio password: {e}")
        return False


# ==============================================
# UTILIDADES DE SEGURIDAD
# ==============================================

def detectar_actividad_sospechosa(usuario: Usuario) -> List[Dict[str, Any]]:
    """
    Detectar actividad sospechosa del usuario
    """
    alertas = []
    ahora = timezone.now()
    hace_24h = ahora - timedelta(hours=24)
    
    # Múltiples intentos de login fallidos
    intentos_fallidos = LogActividad.objects.filter(
        usuario=usuario,
        accion__contains='INTENTO_LOGIN_FALLIDO',
        fecha_creacion__gte=hace_24h
    ).count()
    
    if intentos_fallidos > 3:
        alertas.append({
            'tipo': 'INTENTOS_LOGIN_FALLIDOS',
            'descripcion': f'{intentos_fallidos} intentos fallidos en 24h',
            'severidad': 'MEDIA' if intentos_fallidos < 10 else 'ALTA'
        })
    
    # Múltiples sesiones desde diferentes IPs
    ips_distintas = SesionUsuario.objects.filter(
        usuario=usuario,
        fecha_inicio__gte=hace_24h
    ).values('direccion_ip').distinct().count()
    
    if ips_distintas > 3:
        alertas.append({
            'tipo': 'MULTIPLES_IPS',
            'descripcion': f'Sesiones desde {ips_distintas} IPs diferentes',
            'severidad': 'MEDIA'
        })
    
    # Operaciones críticas en horarios inusuales
    operaciones_nocturnas = LogActividad.objects.filter(
        usuario=usuario,
        accion__contains='CRITICA',
        fecha_creacion__gte=hace_24h,
        fecha_creacion__hour__lt=6  # Antes de las 6 AM
    ).count()
    
    if operaciones_nocturnas > 0:
        alertas.append({
            'tipo': 'OPERACIONES_NOCTURNAS',
            'descripcion': f'{operaciones_nocturnas} operaciones críticas fuera de horario',
            'severidad': 'ALTA'
        })
    
    return alertas


def bloquear_usuario_temporalmente(usuario: Usuario, minutos: int = 30, motivo: str = "") -> None:
    """
    Bloquear usuario temporalmente
    """
    cache.set(f"usuario_bloqueado:{usuario.id}", {
        'bloqueado_hasta': (timezone.now() + timedelta(minutes=minutos)).isoformat(),
        'motivo': motivo
    }, minutos * 60)
    
    # Cerrar todas las sesiones
    SesionUsuario.objects.filter(usuario=usuario, activa=True).update(activa=False)
    
    LogActividad.registrar_actividad(
        usuario=usuario,
        accion='BLOQUEO_TEMPORAL',
        modulo='SEGURIDAD',
        descripcion=f'Usuario bloqueado temporalmente por {minutos} minutos. Motivo: {motivo}',
        direccion_ip='127.0.0.1'
    )


def verificar_usuario_bloqueado(usuario: Usuario) -> Dict[str, Any]:
    """
    Verificar si un usuario está bloqueado temporalmente
    """
    bloqueo_info = cache.get(f"usuario_bloqueado:{usuario.id}")
    
    if bloqueo_info:
        bloqueado_hasta = datetime.fromisoformat(bloqueo_info['bloqueado_hasta'])
        if timezone.now() < bloqueado_hasta:
            return {
                'bloqueado': True,
                'hasta': bloqueado_hasta,
                'motivo': bloqueo_info.get('motivo', 'Actividad sospechosa')
            }
        else:
            # Bloqueo expirado, limpiar cache
            cache.delete(f"usuario_bloqueado:{usuario.id}")
    
    return {'bloqueado': False}


# ==============================================
# EXCEPTION HANDLER PERSONALIZADO
# ==============================================

def custom_exception_handler(exc, context):
    """
    Exception handler personalizado para APIs de FELICITA
    """
    # Obtener response base de DRF
    response = exception_handler(exc, context)
    
    if response is not None:
        # Personalizar formato de errores
        custom_response_data = {
            'error': True,
            'mensaje': 'Ha ocurrido un error',
            'detalles': response.data,
            'codigo_estado': response.status_code,
            'timestamp': timezone.now().isoformat()
        }
        
        # Mensajes personalizados según tipo de error
        if response.status_code == 401:
            custom_response_data['mensaje'] = 'No autorizado. Verifique sus credenciales.'
        elif response.status_code == 403:
            custom_response_data['mensaje'] = 'No tiene permisos para realizar esta acción.'
        elif response.status_code == 404:
            custom_response_data['mensaje'] = 'Recurso no encontrado.'
        elif response.status_code == 429:
            custom_response_data['mensaje'] = 'Demasiadas solicitudes. Intente más tarde.'
        elif response.status_code >= 500:
            custom_response_data['mensaje'] = 'Error interno del servidor.'
            # No mostrar detalles técnicos en producción
            if not settings.DEBUG:
                custom_response_data['detalles'] = 'Contacte al administrador del sistema'
        
        # Registrar errores en logs
        if response.status_code >= 400:
            request = context.get('request')
            usuario = getattr(request, 'user', None) if request else None
            
            logger.error(f"Error API {response.status_code}: {exc} - Usuario: {usuario}")
        
        response.data = custom_response_data
    
    return response


# ==============================================
# DECORADORES DE SEGURIDAD
# ==============================================

def requiere_empresa(func):
    """
    Decorador para verificar que el usuario tenga empresa asignada
    """
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'empresa') or not request.user.empresa:
            return Response({
                'error': 'Usuario debe tener empresa asignada'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return func(request, *args, **kwargs)
    
    return wrapper


def registrar_actividad_automatica(accion, modulo):
    """
    Decorador para registrar actividad automáticamente
    """
    def decorador(func):
        def wrapper(request, *args, **kwargs):
            # Ejecutar función original
            response = func(request, *args, **kwargs)
            
            # Registrar actividad si fue exitosa
            if hasattr(response, 'status_code') and 200 <= response.status_code < 300:
                if hasattr(request, 'user') and request.user.is_authenticated:
                    LogActividad.registrar_actividad(
                        usuario=request.user,
                        accion=accion,
                        modulo=modulo,
                        descripcion=f'{accion} realizada via API',
                        direccion_ip=request.META.get('REMOTE_ADDR', '127.0.0.1')
                    )
            
            return response
        
        return wrapper
    return decorador