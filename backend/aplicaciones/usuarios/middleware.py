"""
Middleware de seguridad para FELICITA
Sistema de Facturación Electrónica para Perú
"""

import logging
import time
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import logout
from rest_framework import status
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import SesionUsuario, LogActividad


logger = logging.getLogger('felicita')


class SeguridadFelicitaMiddleware:
    """
    Middleware principal de seguridad para FELICITA
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Configuraciones de seguridad
        self.max_intentos_login = getattr(settings, 'MAX_INTENTOS_LOGIN', 5)
        self.tiempo_bloqueo_minutos = getattr(settings, 'TIEMPO_BLOQUEO_MINUTOS', 15)
        self.timeout_sesion_minutos = getattr(settings, 'TIMEOUT_SESION_MINUTOS', 120)
    
    def __call__(self, request):
        """
        Procesar request y aplicar validaciones de seguridad
        """
        # Registrar tiempo de inicio para métricas
        inicio_request = time.time()
        
        # Obtener información del cliente
        direccion_ip = self.obtener_ip_cliente(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Agregar información al request
        request.direccion_ip = direccion_ip
        request.user_agent = user_agent
        
        # Verificar bloqueos por IP
        if self.verificar_ip_bloqueada(direccion_ip):
            return JsonResponse({
                'error': 'Dirección IP bloqueada temporalmente',
                'codigo': 'IP_BLOQUEADA'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Verificar rate limiting global
        if self.verificar_rate_limiting(request):
            return JsonResponse({
                'error': 'Demasiadas solicitudes. Intente más tarde.',
                'codigo': 'RATE_LIMIT_EXCEDIDO'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Procesar response
        response = self.get_response(request)
        
        # Post-procesamiento de seguridad
        self.post_procesar_response(request, response, inicio_request)
        
        return response
    
    def obtener_ip_cliente(self, request):
        """
        Obtener IP real del cliente considerando proxies
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        return ip
    
    def verificar_ip_bloqueada(self, direccion_ip):
        """
        Verificar si la IP está bloqueada por intentos fallidos
        """
        clave_bloqueo = f"ip_bloqueada:{direccion_ip}"
        return cache.get(clave_bloqueo, False)
    
    def verificar_rate_limiting(self, request):
        """
        Verificar rate limiting global por IP
        """
        if not getattr(settings, 'RATELIMIT_ENABLE', True):
            return False
        
        direccion_ip = request.direccion_ip
        clave_rate_limit = f"rate_limit:{direccion_ip}"
        
        # Obtener contador actual
        contador = cache.get(clave_rate_limit, 0)
        limite_por_minuto = getattr(settings, 'RATELIMIT_PER_MINUTE', 60)
        
        if contador >= limite_por_minuto:
            return True
        
        # Incrementar contador
        cache.set(clave_rate_limit, contador + 1, 60)  # TTL de 1 minuto
        
        return False
    
    def post_procesar_response(self, request, response, inicio_request):
        """
        Post-procesamiento después de generar response
        """
        # Calcular tiempo de respuesta
        tiempo_respuesta = time.time() - inicio_request
        
        # Agregar headers de seguridad
        self.agregar_headers_seguridad(response)
        
        # Registrar métricas si es necesario
        if tiempo_respuesta > 2.0:  # Respuestas lentas > 2 segundos
            logger.warning(f"Respuesta lenta: {request.path} - {tiempo_respuesta:.2f}s")
        
        # Actualizar última actividad de sesión si hay usuario autenticado
        if hasattr(request, 'user') and request.user.is_authenticated:
            self.actualizar_actividad_sesion(request)
    
    def agregar_headers_seguridad(self, response):
        """
        Agregar headers de seguridad a la respuesta
        """
        # Headers básicos de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy básico
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self';"
        )
        
        # Header personalizado de FELICITA
        response['X-Powered-By'] = 'FELICITA-1.0'
    
    def actualizar_actividad_sesion(self, request):
        """
        Actualizar última actividad de la sesión del usuario
        """
        try:
            sesion = SesionUsuario.objects.filter(
                usuario=request.user,
                direccion_ip=request.direccion_ip,
                activa=True
            ).first()
            
            if sesion:
                sesion.actualizar_ultimo_acceso()
        except Exception as e:
            logger.error(f"Error actualizando sesión: {e}")


class AutenticacionJWTMiddleware:
    """
    Middleware para manejo avanzado de autenticación JWT
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Verificar y validar tokens JWT
        """
        # Verificar token JWT si está presente
        self.verificar_token_jwt(request)
        
        # Verificar timeout de sesión
        self.verificar_timeout_sesion(request)
        
        response = self.get_response(request)
        
        return response
    
    def verificar_token_jwt(self, request):
        """
        Verificar validez del token JWT
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                # Verificar token
                UntypedToken(token)
                
                # Verificar que la sesión sigue activa
                if hasattr(request, 'user') and request.user.is_authenticated:
                    sesion_activa = SesionUsuario.objects.filter(
                        usuario=request.user,
                        token_session=token,
                        activa=True
                    ).exists()
                    
                    if not sesion_activa:
                        # Token válido pero sesión cerrada
                        logout(request)
                        
            except (InvalidToken, TokenError):
                # Token inválido o expirado
                if hasattr(request, 'user') and request.user.is_authenticated:
                    logout(request)
    
    def verificar_timeout_sesion(self, request):
        """
        Verificar timeout de sesión basado en última actividad
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                sesion = SesionUsuario.objects.filter(
                    usuario=request.user,
                    direccion_ip=request.direccion_ip,
                    activa=True
                ).first()
                
                if sesion:
                    timeout_minutos = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 120)
                    tiempo_limite = timezone.now() - timezone.timedelta(minutes=timeout_minutos)
                    
                    if sesion.fecha_ultimo_acceso < tiempo_limite:
                        # Sesión expirada por timeout
                        sesion.cerrar_sesion()
                        logout(request)
                        
                        # Registrar logout por timeout
                        LogActividad.registrar_actividad(
                            usuario=request.user,
                            accion='LOGOUT_TIMEOUT',
                            modulo='SEGURIDAD',
                            descripcion='Sesión cerrada por timeout',
                            direccion_ip=request.direccion_ip
                        )
                        
            except Exception as e:
                logger.error(f"Error verificando timeout sesión: {e}")


class AuditoriaMiddleware:
    """
    Middleware para auditoría automática de operaciones críticas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Rutas que requieren auditoría automática
        self.rutas_auditoria = [
            '/api/facturacion/',
            '/api/contabilidad/',
            '/api/configuraciones/',
            '/api/usuarios/',
        ]
        
        # Métodos que requieren auditoría
        self.metodos_auditoria = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def __call__(self, request):
        """
        Procesar auditoría automática
        """
        response = self.get_response(request)
        
        # Registrar auditoría si es necesario
        if self.requiere_auditoria(request, response):
            self.registrar_auditoria(request, response)
        
        return response
    
    def requiere_auditoria(self, request, response):
        """
        Determinar si el request requiere auditoría
        """
        # Verificar si es una ruta crítica
        ruta_critica = any(request.path.startswith(ruta) for ruta in self.rutas_auditoria)
        
        # Verificar si es un método que modifica datos
        metodo_critico = request.method in self.metodos_auditoria
        
        # Verificar si la operación fue exitosa
        operacion_exitosa = 200 <= response.status_code < 300
        
        # Verificar si hay usuario autenticado
        usuario_autenticado = hasattr(request, 'user') and request.user.is_authenticated
        
        return ruta_critica and metodo_critico and operacion_exitosa and usuario_autenticado
    
    def registrar_auditoria(self, request, response):
        """
        Registrar actividad en auditoría
        """
        try:
            # Determinar módulo basado en la ruta
            modulo = self.determinar_modulo(request.path)
            
            # Determinar acción basado en el método
            acciones = {
                'POST': 'CREAR',
                'PUT': 'ACTUALIZAR',
                'PATCH': 'ACTUALIZAR_PARCIAL',
                'DELETE': 'ELIMINAR'
            }
            accion = acciones.get(request.method, 'MODIFICAR')
            
            # Crear descripción
            descripcion = f"{accion} en {modulo} - {request.path}"
            
            # Datos adicionales
            datos_adicionales = {
                'metodo': request.method,
                'ruta': request.path,
                'status_code': response.status_code,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
            
            # Registrar en log de actividad
            LogActividad.registrar_actividad(
                usuario=request.user,
                accion=f"{accion}_{modulo.upper()}",
                modulo=modulo.upper(),
                descripcion=descripcion,
                datos_adicionales=datos_adicionales,
                direccion_ip=getattr(request, 'direccion_ip', '127.0.0.1')
            )
            
        except Exception as e:
            logger.error(f"Error registrando auditoría: {e}")
    
    def determinar_modulo(self, ruta):
        """
        Determinar módulo basado en la ruta
        """
        if '/facturacion/' in ruta:
            return 'FACTURACION'
        elif '/contabilidad/' in ruta:
            return 'CONTABILIDAD'
        elif '/inventarios/' in ruta:
            return 'INVENTARIOS'
        elif '/usuarios/' in ruta:
            return 'USUARIOS'
        elif '/configuraciones/' in ruta:
            return 'CONFIGURACIONES'
        elif '/pos/' in ruta:
            return 'POS'
        elif '/reportes/' in ruta:
            return 'REPORTES'
        else:
            return 'SISTEMA'


class BloqueoIntentosFallidosMiddleware:
    """
    Middleware para bloquear IPs con intentos fallidos de login
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_intentos = getattr(settings, 'MAX_INTENTOS_LOGIN', 5)
        self.tiempo_bloqueo = getattr(settings, 'TIEMPO_BLOQUEO_MINUTOS', 15)
    
    def __call__(self, request):
        """
        Procesar bloqueo por intentos fallidos
        """
        response = self.get_response(request)
        
        # Verificar si es un intento de login fallido
        if self.es_login_fallido(request, response):
            self.registrar_intento_fallido(request)
        
        # Verificar si es un login exitoso para limpiar intentos
        elif self.es_login_exitoso(request, response):
            self.limpiar_intentos_fallidos(request)
        
        return response
    
    def es_login_fallido(self, request, response):
        """
        Determinar si es un intento de login fallido
        """
        return (
            request.path == '/api/auth/login/' and
            request.method == 'POST' and
            response.status_code >= 400
        )
    
    def es_login_exitoso(self, request, response):
        """
        Determinar si es un login exitoso
        """
        return (
            request.path == '/api/auth/login/' and
            request.method == 'POST' and
            response.status_code == 200
        )
    
    def registrar_intento_fallido(self, request):
        """
        Registrar intento fallido y bloquear si es necesario
        """
        direccion_ip = getattr(request, 'direccion_ip', '127.0.0.1')
        clave_intentos = f"intentos_login:{direccion_ip}"
        
        # Obtener intentos actuales
        intentos = cache.get(clave_intentos, 0)
        intentos += 1
        
        # Guardar intentos con TTL
        cache.set(clave_intentos, intentos, self.tiempo_bloqueo * 60)
        
        # Bloquear IP si excede intentos máximos
        if intentos >= self.max_intentos:
            clave_bloqueo = f"ip_bloqueada:{direccion_ip}"
            cache.set(clave_bloqueo, True, self.tiempo_bloqueo * 60)
            
            # Registrar bloqueo en logs
            LogActividad.registrar_actividad(
                usuario=None,
                accion='BLOQUEO_IP',
                modulo='SEGURIDAD',
                descripcion=f'IP bloqueada por {intentos} intentos fallidos',
                datos_adicionales={
                    'ip': direccion_ip,
                    'intentos': intentos,
                    'tiempo_bloqueo_minutos': self.tiempo_bloqueo
                },
                direccion_ip=direccion_ip
            )
            
            logger.warning(f"IP {direccion_ip} bloqueada por {intentos} intentos fallidos")
    
    def limpiar_intentos_fallidos(self, request):
        """
        Limpiar intentos fallidos después de login exitoso
        """
        direccion_ip = getattr(request, 'direccion_ip', '127.0.0.1')
        clave_intentos = f"intentos_login:{direccion_ip}"
        cache.delete(clave_intentos)


class MonitoreoRendimientoMiddleware:
    """
    Middleware para monitoreo de rendimiento y métricas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Monitorear rendimiento del request
        """
        # Registrar tiempo de inicio
        inicio = time.time()
        
        # Procesar request
        response = self.get_response(request)
        
        # Calcular tiempo de respuesta
        tiempo_respuesta = time.time() - inicio
        
        # Registrar métricas
        self.registrar_metricas(request, response, tiempo_respuesta)
        
        # Agregar header con tiempo de respuesta
        response['X-Response-Time'] = f"{tiempo_respuesta:.3f}s"
        
        return response
    
    def registrar_metricas(self, request, response, tiempo_respuesta):
        """
        Registrar métricas de rendimiento
        """
        try:
            # Métricas básicas
            metrica = {
                'ruta': request.path,
                'metodo': request.method,
                'status_code': response.status_code,
                'tiempo_respuesta': tiempo_respuesta,
                'usuario': request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'anonimo',
                'direccion_ip': getattr(request, 'direccion_ip', '127.0.0.1'),
                'timestamp': timezone.now().isoformat()
            }
            
            # Alertas por rendimiento
            if tiempo_respuesta > 5.0:
                logger.error(f"ALERTA: Respuesta muy lenta {tiempo_respuesta:.2f}s - {request.path}")
                
                # Registrar en auditoría si es crítico
                if hasattr(request, 'user') and request.user.is_authenticated:
                    LogActividad.registrar_actividad(
                        usuario=request.user,
                        accion='ALERTA_RENDIMIENTO',
                        modulo='SISTEMA',
                        descripcion=f'Respuesta lenta detectada: {tiempo_respuesta:.2f}s',
                        datos_adicionales=metrica,
                        direccion_ip=getattr(request, 'direccion_ip', '127.0.0.1')
                    )
            
            # Log de métricas (se puede enviar a sistema de métricas externo)
            logger.info(f"METRICA: {metrica}")
            
        except Exception as e:
            logger.error(f"Error registrando métricas: {e}")