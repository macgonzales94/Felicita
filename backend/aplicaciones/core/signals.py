"""
SIGNALS CORE - PROYECTO FELICITA
Sistema de Facturación Electrónica para Perú

Señales automáticas para el sistema
"""

from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from django.conf import settings
import logging

from .models import (
    Empresa, Sucursal, Cliente, Proveedor, Producto, Categoria,
    TipoCambio, ConfiguracionSistema
)

logger = logging.getLogger('felicita.signals')


# =============================================================================
# SEÑALES DE EMPRESA
# =============================================================================
@receiver(post_save, sender=Empresa)
def empresa_post_save(sender, instance, created, **kwargs):
    """
    Acciones después de guardar una empresa
    """
    if created:
        logger.info(f"Nueva empresa creada: {instance.razon_social} (RUC: {instance.ruc})")
        
        # Crear sucursal principal automáticamente
        if not instance.sucursales.exists():
            Sucursal.objects.create(
                empresa=instance,
                codigo="PRINCIPAL",
                nombre="Sucursal Principal",
                direccion=instance.direccion,
                distrito=instance.distrito,
                provincia=instance.provincia,
                departamento=instance.departamento,
                ubigeo=instance.ubigeo,
                telefono=instance.telefono,
                email=instance.email,
                es_principal=True,
                activo=True
            )
            logger.info(f"Sucursal principal creada para empresa: {instance.razon_social}")
        
        # Crear configuraciones básicas
        crear_configuraciones_empresa(instance)
        
        # Log de actividad
        log_actividad_sistema(
            accion='crear',
            modulo='empresas',
            descripcion=f'Empresa creada: {instance.razon_social}',
            objeto_id=str(instance.id)
        )
    else:
        logger.info(f"Empresa actualizada: {instance.razon_social}")
        
        # Log de actividad
        log_actividad_sistema(
            accion='actualizar',
            modulo='empresas',
            descripcion=f'Empresa actualizada: {instance.razon_social}',
            objeto_id=str(instance.id)
        )


def crear_configuraciones_empresa(empresa):
    """
    Crear configuraciones básicas para nueva empresa
    """
    configuraciones_default = [
        {
            'clave': f'empresa_{empresa.id}_facturacion_serie_factura',
            'valor': 'F001',
            'descripcion': 'Serie por defecto para facturas',
            'tipo_dato': 'STRING'
            #'categoria': 'facturacion'
        },
        {
            'clave': f'empresa_{empresa.id}_facturacion_serie_boleta',
            'valor': 'B001',
            'descripcion': 'Serie por defecto para boletas',
            'tipo_dato': 'STRING'
            #'categoria': 'facturacion'
        },
        {
            'clave': f'empresa_{empresa.id}_facturacion_correlativo_inicial',
            'valor': '1',
            'descripcion': 'Número correlativo inicial',
            'tipo_dato': 'INTEGER'
            #'categoria': 'facturacion'
        },
        {
            'clave': f'empresa_{empresa.id}_igv_tasa',
            'valor': '0.18',
            'descripcion': 'Tasa de IGV aplicable',
            'tipo_dato': 'DECIMAL'
            #'categoria': 'tributario'
        },
        {
            'clave': f'empresa_{empresa.id}_moneda_default',
            'valor': 'PEN',
            'descripcion': 'Moneda por defecto',
            'tipo_dato': 'STRING'
            #'categoria': 'general'
        }
    ]
    
    for config in configuraciones_default:
        ConfiguracionSistema.objects.get_or_create(
            clave=config['clave'],
            defaults=config
        )


# =============================================================================
# SEÑALES DE SUCURSAL
# =============================================================================
@receiver(post_save, sender=Sucursal)
def sucursal_post_save(sender, instance, created, **kwargs):
    """
    Acciones después de guardar una sucursal
    """
    if created:
        logger.info(f"Nueva sucursal creada: {instance.nombre} para empresa {instance.empresa.razon_social}")
        
        # Si es principal, desmarcar otras sucursales principales
        if instance.es_principal:
            Sucursal.objects.filter(
                empresa=instance.empresa,
                es_principal=True
            ).exclude(id=instance.id).update(es_principal=False)
    
    # Verificar que siempre haya una sucursal principal
    if not instance.empresa.sucursales.filter(es_principal=True).exists():
        # Si no hay sucursal principal, marcar la primera como principal
        primera_sucursal = instance.empresa.sucursales.filter(activo=True).first()
        if primera_sucursal:
            primera_sucursal.es_principal = True
            primera_sucursal.save()


# =============================================================================
# SEÑALES DE CLIENTE
# =============================================================================
@receiver(post_save, sender=Cliente)
def cliente_post_save(sender, instance, created, **kwargs):
    """
    Acciones después de guardar un cliente
    """
    if created:
        logger.info(f"Nuevo cliente creado: {instance.numero_documento}")
        
        # Log de actividad
        log_actividad_sistema(
            accion='crear',
            modulo='clientes',
            descripcion=f'Cliente creado: {instance.numero_documento}',
            objeto_id=str(instance.id)
        )
        
        # Validar datos automáticamente si es RUC
        if instance.tipo_documento == 'RUC':
            validar_datos_ruc_cliente.delay(instance.id)


@receiver(pre_save, sender=Cliente)
def cliente_pre_save(sender, instance, **kwargs):
    """
    Acciones antes de guardar un cliente
    """
    # Normalizar email
    if instance.email:
        instance.email = instance.email.lower().strip()
    
    # Limpiar número de teléfono
    if instance.telefono:
        instance.telefono = ''.join(filter(str.isdigit, instance.telefono))
    
    # Validar coherencia de datos
    if instance.es_empresa and not instance.razon_social:
        if instance.nombres and instance.apellido_paterno:
            instance.razon_social = f"{instance.nombres} {instance.apellido_paterno} {instance.apellido_materno or ''}".strip()


# =============================================================================
# SEÑALES DE PROVEEDOR
# =============================================================================
@receiver(post_save, sender=Proveedor)
def proveedor_post_save(sender, instance, created, **kwargs):
    """
    Acciones después de guardar un proveedor
    """
    if created:
        logger.info(f"Nuevo proveedor creado: {instance.razon_social}")
        
        # Log de actividad
        log_actividad_sistema(
            accion='crear',
            modulo='proveedores',
            descripcion=f'Proveedor creado: {instance.razon_social}',
            objeto_id=str(instance.id)
        )


# =============================================================================
# SEÑALES DE PRODUCTO
# =============================================================================
@receiver(post_save, sender=Producto)
def producto_post_save(sender, instance, created, **kwargs):
    """
    Acciones después de guardar un producto
    """
    if created:
        logger.info(f"Nuevo producto creado: {instance.nombre}")
        
        # Log de actividad
        log_actividad_sistema(
            accion='crear',
            modulo='productos',
            descripcion=f'Producto creado: {instance.nombre}',
            objeto_id=str(instance.id)
        )
        
        # Crear movimiento inicial de inventario si tiene stock
        if instance.stock_actual > 0:
            crear_movimiento_inventario_inicial.delay(instance.id)


@receiver(pre_save, sender=Producto)
def producto_pre_save(sender, instance, **kwargs):
    """
    Acciones antes de guardar un producto
    """
    # Generar código automáticamente si no existe
    if not instance.codigo:
        instance.codigo = generar_codigo_producto(instance)
    
    # Validar precios
    if instance.precio_venta and instance.precio_compra:
        if instance.precio_venta < instance.precio_compra:
            logger.warning(f"Precio de venta menor al precio de compra para producto: {instance.nombre}")


@receiver(post_delete, sender=Producto)
def producto_post_delete(sender, instance, **kwargs):
    """
    Acciones después de eliminar un producto
    """
    logger.info(f"Producto eliminado: {instance.nombre}")
    
    # Log de actividad
    log_actividad_sistema(
        accion='eliminar',
        modulo='productos',
        descripcion=f'Producto eliminado: {instance.nombre}',
        objeto_id=str(instance.id)
    )


# =============================================================================
# SEÑALES DE CATEGORÍA
# =============================================================================
@receiver(post_save, sender=Categoria)
def categoria_post_save(sender, instance, created, **kwargs):
    """
    Acciones después de guardar una categoría
    """
    if created:
        logger.info(f"Nueva categoría creada: {instance.nombre}")
        
        # Log de actividad
        log_actividad_sistema(
            accion='crear',
            modulo='categorias',
            descripcion=f'Categoría creada: {instance.nombre}',
            objeto_id=str(instance.id)
        )


# =============================================================================
# SEÑALES DE TIPO DE CAMBIO
# =============================================================================
@receiver(post_save, sender=TipoCambio)
def tipo_cambio_post_save(sender, instance, created, **kwargs):
    """
    Acciones después de guardar un tipo de cambio
    """
    if created:
        logger.info(f"Nuevo tipo de cambio registrado: {instance.moneda_origen.codigo} -> {instance.moneda_destino.codigo} = {instance.valor_venta}")
        
        # Invalidar cache de tipos de cambio
        invalidar_cache_tipos_cambio.delay()


# =============================================================================
# SEÑALES DE AUTENTICACIÓN
# =============================================================================
@receiver(user_logged_in)
def usuario_login(sender, request, user, **kwargs):
    """
    Acciones cuando un usuario hace login
    """
    logger.info(f"Usuario logueado: {user.email}")
    
    # Actualizar fecha de último login
    user.fecha_ultimo_login = timezone.now()
    user.intentos_login_fallidos = 0
    user.save(update_fields=['fecha_ultimo_login', 'intentos_login_fallidos'])
    
    # Log de actividad
    from aplicaciones.usuarios.models import LogActividadUsuario
    
    LogActividadUsuario.objects.create(
        usuario=user,
        accion='login',
        modulo='autenticacion',
        descripcion='Inicio de sesión exitoso',
        ip_address=get_client_ip(request)
    )


@receiver(user_logged_out)
def usuario_logout(sender, request, user, **kwargs):
    """
    Acciones cuando un usuario hace logout
    """
    if user:
        logger.info(f"Usuario deslogueado: {user.email}")
        
        # Log de actividad
        from aplicaciones.usuarios.models import LogActividadUsuario
        
        LogActividadUsuario.objects.create(
            usuario=user,
            accion='logout',
            modulo='autenticacion',
            descripcion='Cierre de sesión',
            ip_address=get_client_ip(request)
        )


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def get_client_ip(request):
    """
    Obtener IP del cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_actividad_sistema(accion, modulo, descripcion, objeto_id=None, usuario=None, ip_address=None):
    """
    Registrar actividad del sistema
    """
    try:
        from aplicaciones.usuarios.models import LogActividadUsuario
        
        LogActividadUsuario.objects.create(
            usuario=usuario,
            accion=accion,
            modulo=modulo,
            descripcion=descripcion,
            ip_address=ip_address or '127.0.0.1',
            metadata={'objeto_id': objeto_id} if objeto_id else None
        )
    except Exception as e:
        logger.error(f"Error al registrar log de actividad: {e}")


def generar_codigo_producto(producto):
    """
    Generar código automático para producto
    """
    # Usar prefijo de categoría si existe
    prefijo = ""
    if producto.categoria:
        prefijo = producto.categoria.codigo[:3].upper()
    
    # Generar número correlativo
    ultimo_producto = Producto.objects.filter(
        codigo__startswith=prefijo
    ).order_by('-codigo').first()
    
    if ultimo_producto and ultimo_producto.codigo[len(prefijo):].isdigit():
        numero = int(ultimo_producto.codigo[len(prefijo):]) + 1
    else:
        numero = 1
    
    return f"{prefijo}{numero:06d}"


# =============================================================================
# TAREAS CELERY (PLACEHOLDERS)
# =============================================================================
def validar_datos_ruc_cliente(cliente_id):
    """
    Tarea para validar datos de RUC en SUNAT (placeholder)
    """
    try:
        from .utils import consultar_ruc_sunat
        
        cliente = Cliente.objects.get(id=cliente_id)
        if cliente.tipo_documento == 'RUC':
            datos_sunat = consultar_ruc_sunat(cliente.numero_documento)
            
            if datos_sunat:
                # Actualizar datos del cliente con información de SUNAT
                cliente.razon_social = datos_sunat.get('razon_social', cliente.razon_social)
                cliente.direccion = datos_sunat.get('direccion', cliente.direccion)
                cliente.distrito = datos_sunat.get('distrito', cliente.distrito)
                cliente.provincia = datos_sunat.get('provincia', cliente.provincia)
                cliente.departamento = datos_sunat.get('departamento', cliente.departamento)
                cliente.ubigeo = datos_sunat.get('ubigeo', cliente.ubigeo)
                cliente.save()
                
                logger.info(f"Datos de RUC actualizados para cliente: {cliente.numero_documento}")
    
    except Exception as e:
        logger.error(f"Error al validar RUC: {e}")


def crear_movimiento_inventario_inicial(producto_id):
    """
    Crear movimiento inicial de inventario (placeholder)
    """
    try:
        producto = Producto.objects.get(id=producto_id)
        
        # TODO: Implementar cuando se tenga el módulo de inventario
        logger.info(f"Movimiento inicial de inventario creado para producto: {producto.nombre}")
        
    except Exception as e:
        logger.error(f"Error al crear movimiento inicial: {e}")


def invalidar_cache_tipos_cambio():
    """
    Invalidar cache de tipos de cambio (placeholder)
    """
    try:
        # TODO: Implementar invalidación de cache
        logger.info("Cache de tipos de cambio invalidado")
        
    except Exception as e:
        logger.error(f"Error al invalidar cache: {e}")


# =============================================================================
# SEÑALES PARA AUDITORÍA AUTOMÁTICA
# =============================================================================
@receiver(pre_save)
def auditoria_pre_save(sender, instance, **kwargs):
    """
    Auditoría automática antes de guardar cualquier modelo
    """
    # Solo aplicar a modelos del core
    if not sender._meta.app_label == 'core':
        return
    
    # Establecer fecha de actualización
    if hasattr(instance, 'actualizado_en'):
        instance.actualizado_en = timezone.now()
    
    # Log de cambios en desarrollo
    if settings.DEBUG and hasattr(instance, 'pk') and instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            cambios = []
            
            for field in instance._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name)
                new_value = getattr(instance, field_name)
                
                if old_value != new_value:
                    cambios.append(f"{field_name}: {old_value} -> {new_value}")
            
            if cambios:
                logger.debug(f"Cambios en {sender.__name__}: {', '.join(cambios)}")
                
        except sender.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error en auditoría: {e}")


# =============================================================================
# INICIALIZACIÓN DE SEÑALES
# =============================================================================
def conectar_señales():
    """
    Conectar todas las señales del sistema
    """
    logger.info("Señales del sistema conectadas correctamente")


# Conectar señales al cargar el módulo
conectar_señales()