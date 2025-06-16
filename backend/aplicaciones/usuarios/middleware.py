"""
FELICITA - Middleware de Seguridad
Sistema de Facturación Electrónica para Perú

Middlewares personalizados para auditoría y seguridad
"""

import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from .models import LogAuditoria

logger = logging.getLogger('felicita.security')
audit_logger = logging.getLogger('felicita.usuarios')

Usuario = get_user_model()

# ===========================================
# MIDDLEWARE DE AUDITORÍA
# ===========================================

class AuditMiddleware(MiddlewareMixin):
    """Middleware para registrar todas las acciones del sistema"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Procesar request entrante"""
        # Marcar tiempo de inicio
        request._audit_start_time = time.time()
        
        # Obtener información del cliente
        request._audit_ip = self.get_client_ip(request)
        request._audit_user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return None
    
    def process_response(self, request, response):
        """Procesar response de salida"""
        # Calcular tiempo de procesamiento
        if hasattr(request, '_audit_start_time'):
            processing_time = time.time() - request._audit_start_time
        else:
            processing_time = 0
        
        # Solo auditar ciertas rutas y métodos
        if self.should_audit(request):
            self.create_audit_log(request, response, processing_time)
        
        return response
    
    def process_exception(self, request, exception):
        """Procesar excepciones"""
        # Log de seguridad para excepciones
        logger.error(
            f"Excepción en {request.method} {request.path}: {str(exception)}",
            extra={
                'ip_address': getattr(request, '_audit_ip', 'unknown'),
                'user_agent': getattr(request, '_audit_user_agent', ''),
                'user_id': request.user.id if request.user.is_authenticated else None,
                'exception_type': type(exception).__name__,
            }
        )
        
        return None
    
    def get_client_ip(self, request):
        """Obtener IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def should_audit(self, request):
        """Determinar si se debe auditar la request"""
        # No auditar rutas estáticas
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return False
        
        # No auditar health checks
        if request.path.startswith('/health/'):
            return False
        
        # Solo auditar APIs importantes
        api_paths = [
            '/api/usuarios/',
            '/api/core/',
            '/api/facturacion/',
            '/api/inventario/',
            '/api/reportes/',
        ]
        
        # Auditar si es una API importante o acciones POST/PUT/DELETE
        return (
            any(request.path.startswith(path) for path in api_paths) or
            request.method in ['POST', 'PUT', 'PATCH', 'DELETE']
        )
    
    def create_audit_log(self, request, response, processing_time):
        """Crear log de auditoría"""
        try:
            # Determinar acción basada en método y ruta
            accion = self.determine_action(request)
            
            # Determinar recurso
            recurso = self.determine_resource(request)
            
            # Determinar resultado
            resultado = 'EXITOSO' if 200 <= response.status_code < 400 else 'FALLIDO'
            
            # Datos adicionales
            datos_adicionales = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'processing_time': round(processing_time, 3),
                'query_params': dict(request.GET),
            }
            
            # Agregar datos del body para métodos que lo permiten
            if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'body'):
                try:
                    # Solo auditar datos no sensibles
                    if request.content_type == 'application/json':
                        body_data = json.loads(request.body.decode('utf-8'))
                        # Eliminar campos sensibles
                        sensitive_fields = ['password', 'password_nuevo', 'password_actual']
                        for field in sensitive_fields:
                            if field in body_data:
                                body_data[field] = '***'
                        datos_adicionales['body'] = body_data
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
            
            # Crear log de auditoría
            LogAuditoria.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                accion=accion,
                recurso=recurso,
                ip_address=request._audit_ip,
                user_agent=request._audit_user_agent,
                datos_adicionales=datos_adicionales,
                resultado=resultado
            )
            
        except Exception as e:
            # Log de error pero no fallar la request
            logger.error(f"Error creando log de auditoría: {e}")
    
    def determine_action(self, request):
        """Determinar la acción basada en el request"""
        method_map = {
            'GET': 'CONSULTAR',
            'POST': 'CREAR',
            'PUT': 'ACTUALIZAR',
            'PATCH': 'ACTUALIZAR',
            'DELETE': 'ELIMINAR',
        }
        
        # Acciones específicas por ruta
        if 'login' in request.path:
            return 'LOGIN'
        elif 'logout' in request.path:
            return 'LOGOUT'
        elif 'password' in request.path:
            return 'CAMBIAR_PASSWORD'
        elif 'activar' in request.path:
            return 'ACTIVAR_USUARIO'
        elif 'desactivar' in request.path:
            return 'DESACTIVAR_USUARIO'
        
        return method_map.get(request.method, 'ACCION_DESCONOCIDA')
    
    def determine_resource(self, request):
        """Determinar el recurso basado en la ruta"""
        path_parts = request.path.strip('/').split('/')
        
        if len(path_parts) >= 2 and path_parts[0] == 'api':
            return path_parts[1].upper()
        
        return 'SISTEMA'

# ===========================================
# MIDDLEWARE DE HEADERS DE SEGURIDAD
# ===========================================

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware para agregar headers de seguridad adicionales"""
    
    def process_response(self, request, response):
        """Agregar headers de seguridad"""
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.nubefact.com; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self'"
        )
        response['Content-Security-Policy'] = csp_policy
        
        # Permissions Policy (anteriormente Feature Policy)
        permissions_policy = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        response['Permissions-Policy'] = permissions_policy
        
        # Headers adicionales de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Header personalizado de la aplicación
        response['X-Powered-By'] = 'FELICITA v1.0'
        
        # Cache control para APIs
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response

# ===========================================
# MIDDLEWARE DE RATE LIMITING
# ===========================================

class RateLimitMiddleware(MiddlewareMixin):
    """Middleware para rate limiting por IP y usuario"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Verificar rate limits antes de procesar"""
        
        # Solo aplicar a rutas de API
        if not request.path.startswith('/api/'):
            return None
        
        ip_address = self.get_client_ip(request)
        
        # Rate limiting por IP
        if self.is_rate_limited_by_ip(ip_address):
            logger.warning(f"Rate limit excedido para IP: {ip_address}")
            return JsonResponse({
                'error': 'Rate limit excedido. Intente más tarde.',
                'detail': 'Demasiadas peticiones desde esta IP.'
            }, status=429)
        
        # Rate limiting por usuario autenticado
        if request.user.is_authenticated:
            if self.is_rate_limited_by_user(request.user.id):
                logger.warning(f"Rate limit excedido para usuario: {request.user.username}")
                return JsonResponse({
                    'error': 'Rate limit excedido. Intente más tarde.',
                    'detail': 'Demasiadas peticiones de este usuario.'
                }, status=429)
        
        # Rate limiting específico para login
        if 'login' in request.path and request.method == 'POST':
            if self.is_rate_limited_login(ip_address):
                logger.warning(f"Rate limit de login excedido para IP: {ip_address}")
                return JsonResponse({
                    'error': 'Demasiados intentos de login.',
                    'detail': 'Espere antes de intentar nuevamente.'
                }, status=429)
        
        return None
    
    def process_response(self, request, response):
        """Actualizar contadores después de procesar"""
        
        if not request.path.startswith('/api/'):
            return response
        
        ip_address = self.get_client_ip(request)
        
        # Incrementar contador por IP
        self.increment_ip_counter(ip_address)
        
        # Incrementar contador por usuario
        if request.user.is_authenticated:
            self.increment_user_counter(request.user.id)
        
        # Incrementar contador de login si es necesario
        if 'login' in request.path and request.method == 'POST':
            self.increment_login_counter(ip_address)
        
        # Agregar headers de rate limit
        self.add_rate_limit_headers(response, ip_address, request.user)
        
        return response
    
    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited_by_ip(self, ip_address):
        """Verificar rate limit por IP"""
        key = f"rate_limit_ip_{ip_address}"
        count = cache.get(key, 0)
        return count >= getattr(settings, 'RATE_LIMIT_IP_PER_HOUR', 1000)
    
    def is_rate_limited_by_user(self, user_id):
        """Verificar rate limit por usuario"""
        key = f"rate_limit_user_{user_id}"
        count = cache.get(key, 0)
        return count >= getattr(settings, 'RATE_LIMIT_USER_PER_HOUR', 2000)
    
    def is_rate_limited_login(self, ip_address):
        """Verificar rate limit específico para login"""
        key = f"rate_limit_login_{ip_address}"
        count = cache.get(key, 0)
        return count >= getattr(settings, 'RATE_LIMIT_LOGIN_PER_HOUR', 20)
    
    def increment_ip_counter(self, ip_address):
        """Incrementar contador por IP"""
        key = f"rate_limit_ip_{ip_address}"
        try:
            cache.add(key, 0, 3600)  # 1 hora
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, 3600)
    
    def increment_user_counter(self, user_id):
        """Incrementar contador por usuario"""
        key = f"rate_limit_user_{user_id}"
        try:
            cache.add(key, 0, 3600)  # 1 hora
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, 3600)
    
    def increment_login_counter(self, ip_address):
        """Incrementar contador de login"""
        key = f"rate_limit_login_{ip_address}"
        try:
            cache.add(key, 0, 3600)  # 1 hora
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, 3600)
    
    def add_rate_limit_headers(self, response, ip_address, user):
        """Agregar headers de rate limit"""
        # Contador por IP
        ip_key = f"rate_limit_ip_{ip_address}"
        ip_count = cache.get(ip_key, 0)
        ip_limit = getattr(settings, 'RATE_LIMIT_IP_PER_HOUR', 1000)
        
        response['X-RateLimit-Limit'] = str(ip_limit)
        response['X-RateLimit-Remaining'] = str(max(0, ip_limit - ip_count))
        response['X-RateLimit-Reset'] = str(int(time.time()) + 3600)
        
        # Contador por usuario si está autenticado
        if user.is_authenticated:
            user_key = f"rate_limit_user_{user.id}"
            user_count = cache.get(user_key, 0)
            user_limit = getattr(settings, 'RATE_LIMIT_USER_PER_HOUR', 2000)
            
            response['X-RateLimit-User-Limit'] = str(user_limit)
            response['X-RateLimit-User-Remaining'] = str(max(0, user_limit - user_count))

# ===========================================
# MIDDLEWARE DE SESSIÓN TIMEOUT
# ===========================================

class SessionTimeoutMiddleware(MiddlewareMixin):
    """Middleware para manejar timeout de sesiones"""
    
    def process_request(self, request):
        """Verificar timeout de sesión"""
        
        if not request.user.is_authenticated:
            return None
        
        # Obtener configuración de timeout
        timeout_minutes = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 480)  # 8 horas por defecto
        
        # Verificar última actividad
        last_activity = request.session.get('last_activity')
        
        if last_activity:
            last_activity_time = timezone.datetime.fromisoformat(last_activity)
            time_diff = timezone.now() - last_activity_time
            
            if time_diff.total_seconds() > (timeout_minutes * 60):
                # Sesión expirada
                request.session.flush()
                
                if request.path.startswith('/api/'):
                    return JsonResponse({
                        'error': 'Sesión expirada',
                        'detail': 'Su sesión ha expirado por inactividad.'
                    }, status=401)
                else:
                    # Redirigir a login para requests web
                    from django.shortcuts import redirect
                    return redirect('/login')
        
        # Actualizar última actividad
        request.session['last_activity'] = timezone.now().isoformat()
        
        return None

# ===========================================
# MIDDLEWARE DE BLOQUEO DE USUARIOS
# ===========================================

class UserBlockingMiddleware(MiddlewareMixin):
    """Middleware para verificar usuarios bloqueados"""
    
    def process_request(self, request):
        """Verificar si el usuario está bloqueado"""
        
        if not request.user.is_authenticated:
            return None
        
        # Verificar si el usuario está bloqueado
        if hasattr(request.user, 'esta_bloqueado') and request.user.esta_bloqueado:
            # Log de seguridad
            logger.warning(f"Usuario bloqueado intentó acceder: {request.user.username}")
            
            # Forzar logout
            from django.contrib.auth import logout
            logout(request)
            
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Usuario bloqueado',
                    'detail': 'Su cuenta ha sido bloqueada temporalmente.'
                }, status=403)
            else:
                from django.shortcuts import redirect
                return redirect('/login')
        
        return None