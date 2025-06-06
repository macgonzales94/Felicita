"""
Signals para auditoría automática en FELICITA
Sistema de Facturación Electrónica para Perú
"""

import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils import timezone
from threading import local

from .models import Usuario, SesionUsuario, LogActividad


logger = logging.getLogger('felicita')

# Thread-local storage para mantener información del request
_thread_locals = local()


def obtener_usuario_actual():
    """
    Obtener usuario actual del thread local
    """
    return getattr(_thread_locals, 'usuario', None)


def obtener_direccion_ip_actual():
    """
    Obtener dirección IP actual del thread local
    """
    return getattr(_thread_locals, 'direccion_ip', '127.0.0.1')


def establecer_contexto_request(usuario, direccion_ip):
    """
    Establecer contexto del request en thread local
    """
    _thread_locals.usuario = usuario
    _thread_locals.direccion_ip = direccion_ip


# ==============================================
# SIGNALS DE AUTENTICACIÓN
# ==============================================

@receiver(user_logged_in)
def usuario_inicio_sesion(sender, request, user, **kwargs):
    """
    Signal cuando usuario inicia sesión exitosamente
    """
    try:
        direccion_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Establecer contexto para otros signals
        establecer_contexto_request(user, direccion_ip)
        
        # Registrar en log de actividad
        LogActividad.registrar_actividad(
            usuario=user,
            accion='INICIO_SESION_SIGNAL',
            modulo='AUTENTICACION',
            descripcion=f'Usuario {user.username} inició sesión',
            datos_adicionales={
                'user_agent': user_agent,
                'metodo': 'SIGNAL'
            },
            direccion_ip=direccion_ip
        )
        
        logger.info(f"Usuario {user.username} inició sesión desde {direccion_ip}")
        
    except Exception as e:
        logger.error(f"Error en signal usuario_inicio_sesion: {e}")


@receiver(user_logged_out)
def usuario_cerro_sesion(sender, request, user, **kwargs):
    """
    Signal cuando usuario cierra sesión
    """
    try:
        direccion_ip = request.META.get('REMOTE_ADDR', '127.0.0.1') if request else '127.0.0.1'
        
        if user:
            # Registrar en log de actividad
            LogActividad.registrar_actividad(
                usuario=user,
                accion='CERRAR_SESION_SIGNAL',
                modulo='AUTENTICACION',
                descripcion=f'Usuario {user.username} cerró sesión',
                datos_adicionales={
                    'metodo': 'SIGNAL'
                },
                direccion_ip=direccion_ip
            )
            
            # Marcar sesiones como inactivas
            SesionUsuario.objects.filter(
                usuario=user,
                direccion_ip=direccion_ip,
                activa=True
            ).update(activa=False)
            
            logger.info(f"Usuario {user.username} cerró sesión desde {direccion_ip}")
        
    except Exception as e:
        logger.error(f"Error en signal usuario_cerro_sesion: {e}")


@receiver(user_login_failed)
def intento_login_fallido(sender, credentials, request, **kwargs):
    """
    Signal cuando falla un intento de login
    """
    try:
        direccion_ip = request.META.get('REMOTE_ADDR', '127.0.0.1') if request else '127.0.0.1'
        username = credentials.get('username', 'desconocido')
        
        # Registrar en log de actividad
        LogActividad.registrar_actividad(
            usuario=None,
            accion='INTENTO_LOGIN_FALLIDO_SIGNAL',
            modulo='SEGURIDAD',
            descripcion=f'Intento fallido de login para usuario: {username}',
            datos_adicionales={
                'username_intentado': username,
                'metodo': 'SIGNAL'
            },
            direccion_ip=direccion_ip
        )
        
        logger.warning(f"Intento fallido de login para {username} desde {direccion_ip}")
        
    except Exception as e:
        logger.error(f"Error en signal intento_login_fallido: {e}")


# ==============================================
# SIGNALS DE USUARIO
# ==============================================

@receiver(post_save, sender=Usuario)
def usuario_guardado(sender, instance, created, **kwargs):
    """
    Signal cuando se guarda un usuario (crear o actualizar)
    """
    try:
        usuario_actual = obtener_usuario_actual()
        direccion_ip = obtener_direccion_ip_actual()
        
        if created:
            # Usuario creado
            accion = 'CREAR_USUARIO_SIGNAL'
            descripcion = f'Nuevo usuario creado: {instance.username}'
            
            logger.info(f"Nuevo usuario creado: {instance.username}")
        else:
            # Usuario actualizado
            accion = 'ACTUALIZAR_USUARIO_SIGNAL'
            descripcion = f'Usuario actualizado: {instance.username}'
        
        # Registrar en log si hay usuario actual (no auto-registro)
        if usuario_actual and usuario_actual != instance:
            LogActividad.registrar_actividad(
                usuario=usuario_actual,
                accion=accion,
                modulo='ADMINISTRACION',
                descripcion=descripcion,
                datos_adicionales={
                    'usuario_afectado_id': instance.id,
                    'usuario_afectado_username': instance.username,
                    'metodo': 'SIGNAL'
                },
                direccion_ip=direccion_ip
            )
        
        # Si es creación por auto-registro
        elif created and not usuario_actual:
            LogActividad.registrar_actividad(
                usuario=instance,
                accion='AUTO_REGISTRO_SIGNAL',
                modulo='AUTENTICACION',
                descripcion=f'Usuario se auto-registró: {instance.username}',
                datos_adicionales={
                    'metodo': 'SIGNAL'
                },
                direccion_ip=direccion_ip
            )
        
    except Exception as e:
        logger.error(f"Error en signal usuario_guardado: {e}")


@receiver(pre_save, sender=Usuario)
def usuario_antes_guardar(sender, instance, **kwargs):
    """
    Signal antes de guardar usuario para detectar cambios
    """
    try:
        if instance.pk:  # Solo si es actualización
            # Obtener usuario original
            original = Usuario.objects.get(pk=instance.pk)
            
            # Detectar cambios importantes
            cambios_importantes = []
            
            if original.is_active != instance.is_active:
                estado = 'activado' if instance.is_active else 'desactivado'
                cambios_importantes.append(f'Usuario {estado}')
            
            if original.rol != instance.rol:
                cambios_importantes.append(f'Rol cambiado de {original.rol} a {instance.rol}')
            
            if original.empresa != instance.empresa:
                empresa_original = original.empresa.razon_social if original.empresa else 'Ninguna'
                empresa_nueva = instance.empresa.razon_social if instance.empresa else 'Ninguna'
                cambios_importantes.append(f'Empresa cambiada de {empresa_original} a {empresa_nueva}')
            
            # Guardar cambios en el contexto para post_save
            if cambios_importantes:
                _thread_locals.cambios_usuario = cambios_importantes
    
    except Exception as e:
        logger.error(f"Error en signal usuario_antes_guardar: {e}")


@receiver(post_delete, sender=Usuario)
def usuario_eliminado(sender, instance, **kwargs):
    """
    Signal cuando se elimina un usuario
    """
    try:
        usuario_actual = obtener_usuario_actual()
        direccion_ip = obtener_direccion_ip_actual()
        
        # Registrar eliminación
        LogActividad.registrar_actividad(
            usuario=usuario_actual,
            accion='ELIMINAR_USUARIO_SIGNAL',
            modulo='ADMINISTRACION',
            descripcion=f'Usuario eliminado: {instance.username}',
            datos_adicionales={
                'usuario_eliminado_id': instance.id,
                'usuario_eliminado_username': instance.username,
                'usuario_eliminado_email': instance.email,
                'metodo': 'SIGNAL'
            },
            direccion_ip=direccion_ip
        )
        
        # Cerrar todas las sesiones del usuario eliminado
        SesionUsuario.objects.filter(usuario=instance).update(activa=False)
        
        logger.warning(f"Usuario eliminado: {instance.username}")
        
    except Exception as e:
        logger.error(f"Error en signal usuario_eliminado: {e}")


# ==============================================
# SIGNALS DE MODELOS CRÍTICOS
# ==============================================

def crear_signal_auditoria(modelo_clase, modulo_nombre):
    """
    Factory para crear signals de auditoría para modelos críticos
    """
    
    @receiver(post_save, sender=modelo_clase)
    def modelo_guardado(sender, instance, created, **kwargs):
        try:
            usuario_actual = obtener_usuario_actual()
            direccion_ip = obtener_direccion_ip_actual()
            
            if not usuario_actual:
                return
            
            nombre_modelo = sender.__name__
            
            if created:
                accion = f'CREAR_{nombre_modelo.upper()}_SIGNAL'
                descripcion = f'Nuevo {nombre_modelo} creado'
            else:
                accion = f'ACTUALIZAR_{nombre_modelo.upper()}_SIGNAL'
                descripcion = f'{nombre_modelo} actualizado'
            
            # Obtener identificador del objeto
            identificador = str(instance)
            if hasattr(instance, 'numero_completo'):
                identificador = instance.numero_completo
            elif hasattr(instance, 'codigo'):
                identificador = instance.codigo
            elif hasattr(instance, 'nombre'):
                identificador = instance.nombre
            
            LogActividad.registrar_actividad(
                usuario=usuario_actual,
                accion=accion,
                modulo=modulo_nombre.upper(),
                descripcion=f'{descripcion}: {identificador}',
                datos_adicionales={
                    'modelo': nombre_modelo,
                    'objeto_id': instance.pk,
                    'objeto_str': str(instance),
                    'metodo': 'SIGNAL'
                },
                direccion_ip=direccion_ip
            )
            
        except Exception as e:
            logger.error(f"Error en signal {modelo_clase.__name__}_guardado: {e}")
    
    @receiver(post_delete, sender=modelo_clase)
    def modelo_eliminado(sender, instance, **kwargs):
        try:
            usuario_actual = obtener_usuario_actual()
            direccion_ip = obtener_direccion_ip_actual()
            
            if not usuario_actual:
                return
            
            nombre_modelo = sender.__name__
            
            LogActividad.registrar_actividad(
                usuario=usuario_actual,
                accion=f'ELIMINAR_{nombre_modelo.upper()}_SIGNAL',
                modulo=modulo_nombre.upper(),
                descripcion=f'{nombre_modelo} eliminado: {str(instance)}',
                datos_adicionales={
                    'modelo': nombre_modelo,
                    'objeto_eliminado_str': str(instance),
                    'metodo': 'SIGNAL'
                },
                direccion_ip=direccion_ip
            )
            
        except Exception as e:
            logger.error(f"Error en signal {modelo_clase.__name__}_eliminado: {e}")


# Configurar signals para modelos críticos cuando las apps estén listas
def configurar_signals_modelos_criticos():
    """
    Configurar signals para modelos críticos de todas las apps
    """
    try:
        # Facturación
        from aplicaciones.facturacion.models import Comprobante, SerieComprobante
        crear_signal_auditoria(Comprobante, 'FACTURACION')
        crear_signal_auditoria(SerieComprobante, 'FACTURACION')
        
        # Contabilidad
        from aplicaciones.contabilidad.models import AsientoContable, PlanCuentas
        crear_signal_auditoria(AsientoContable, 'CONTABILIDAD')
        crear_signal_auditoria(PlanCuentas, 'CONTABILIDAD')
        
        # Inventarios
        from aplicaciones.inventarios.models import MovimientoInventario, Almacen
        crear_signal_auditoria(MovimientoInventario, 'INVENTARIOS')
        crear_signal_auditoria(Almacen, 'INVENTARIOS')
        
        # Productos
        from aplicaciones.productos.models import Producto
        crear_signal_auditoria(Producto, 'PRODUCTOS')
        
        # Clientes
        from aplicaciones.clientes.models import Cliente
        crear_signal_auditoria(Cliente, 'CLIENTES')
        
        # Empresas
        from aplicaciones.empresas.models import Empresa
        crear_signal_auditoria(Empresa, 'EMPRESAS')
        
        logger.info("Signals de auditoría configurados para modelos críticos")
        
    except ImportError as e:
        logger.warning(f"No se pudieron configurar todos los signals: {e}")


# ==============================================
# SIGNALS PERSONALIZADOS PARA FELICITA
# ==============================================

from django.dispatch import Signal

# Signal personalizado para cambios de permisos
permiso_modificado = Signal()

# Signal personalizado para operaciones críticas
operacion_critica_realizada = Signal()

# Signal personalizado para alertas de seguridad
alerta_seguridad = Signal()


@receiver(permiso_modificado)
def manejar_permiso_modificado(sender, usuario_afectado, permiso_modificado, usuario_modificador, **kwargs):
    """
    Manejar cambios en permisos de usuario
    """
    try:
        LogActividad.registrar_actividad(
            usuario=usuario_modificador,
            accion='MODIFICAR_PERMISOS',
            modulo='SEGURIDAD',
            descripcion=f'Permisos modificados para {usuario_afectado.username}',
            datos_adicionales={
                'usuario_afectado_id': usuario_afectado.id,
                'permiso_modificado': permiso_modificado,
                'metodo': 'SIGNAL_PERSONALIZADO'
            },
            direccion_ip=obtener_direccion_ip_actual()
        )
        
    except Exception as e:
        logger.error(f"Error en signal permiso_modificado: {e}")


@receiver(operacion_critica_realizada)
def manejar_operacion_critica(sender, usuario, descripcion, datos_adicionales=None, **kwargs):
    """
    Manejar operaciones críticas del sistema
    """
    try:
        LogActividad.registrar_actividad(
            usuario=usuario,
            accion='OPERACION_CRITICA',
            modulo='SEGURIDAD',
            descripcion=descripcion,
            datos_adicionales=datos_adicionales or {},
            direccion_ip=obtener_direccion_ip_actual()
        )
        
        # Log adicional para operaciones críticas
        logger.critical(f"OPERACION CRITICA: {descripcion} - Usuario: {usuario.username}")
        
    except Exception as e:
        logger.error(f"Error en signal operacion_critica_realizada: {e}")


@receiver(alerta_seguridad)
def manejar_alerta_seguridad(sender, tipo_alerta, descripcion, datos_adicionales=None, **kwargs):
    """
    Manejar alertas de seguridad
    """
    try:
        usuario_actual = obtener_usuario_actual()
        
        LogActividad.registrar_actividad(
            usuario=usuario_actual,
            accion=f'ALERTA_SEGURIDAD_{tipo_alerta.upper()}',
            modulo='SEGURIDAD',
            descripcion=descripcion,
            datos_adicionales=datos_adicionales or {},
            direccion_ip=obtener_direccion_ip_actual()
        )
        
        # Log de seguridad crítico
        logger.critical(f"ALERTA SEGURIDAD [{tipo_alerta}]: {descripcion}")
        
        # Aquí se podría integrar con sistemas de alertas externos
        # como email, Slack, etc.
        
    except Exception as e:
        logger.error(f"Error en signal alerta_seguridad: {e}")


# ==============================================
# UTILIDADES PARA USAR EN VIEWS
# ==============================================

def registrar_actividad_view(usuario, accion, modulo, descripcion, request=None, datos_adicionales=None):
    """
    Utilidad para registrar actividad desde views
    """
    try:
        direccion_ip = '127.0.0.1'
        
        if request:
            direccion_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
            # Establecer contexto para signals
            establecer_contexto_request(usuario, direccion_ip)
        
        LogActividad.registrar_actividad(
            usuario=usuario,
            accion=accion,
            modulo=modulo,
            descripcion=descripcion,
            datos_adicionales=datos_adicionales or {},
            direccion_ip=direccion_ip
        )
        
    except Exception as e:
        logger.error(f"Error registrando actividad desde view: {e}")


def emitir_operacion_critica(usuario, descripcion, datos_adicionales=None):
    """
    Emitir signal de operación crítica
    """
    operacion_critica_realizada.send(
        sender=None,
        usuario=usuario,
        descripcion=descripcion,
        datos_adicionales=datos_adicionales
    )


def emitir_alerta_seguridad(tipo_alerta, descripcion, datos_adicionales=None):
    """
    Emitir signal de alerta de seguridad
    """
    alerta_seguridad.send(
        sender=None,
        tipo_alerta=tipo_alerta,
        descripcion=descripcion,
        datos_adicionales=datos_adicionales
    )