# Generated by Django 4.2.11 on 2025-06-15 10:08

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Usuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "rol",
                    models.CharField(
                        choices=[
                            ("administrador", "Administrador"),
                            ("contador", "Contador"),
                            ("vendedor", "Vendedor"),
                            ("supervisor", "Supervisor"),
                            ("cliente", "Cliente"),
                        ],
                        default="vendedor",
                        help_text="Rol del usuario en el sistema",
                        max_length=20,
                        verbose_name="Rol",
                    ),
                ),
                (
                    "telefono",
                    models.CharField(
                        blank=True,
                        help_text="Número de teléfono de contacto",
                        max_length=20,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Formato de teléfono inválido",
                                regex="^[+]?[0-9\\s\\-\\(\\)]{7,20}$",
                            )
                        ],
                        verbose_name="Teléfono",
                    ),
                ),
                (
                    "documento_identidad",
                    models.CharField(
                        blank=True,
                        help_text="DNI o Carnet de Extranjería",
                        max_length=11,
                        verbose_name="Documento de Identidad",
                    ),
                ),
                (
                    "preferencias",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Configuraciones personalizadas del usuario",
                        verbose_name="Preferencias",
                    ),
                ),
                (
                    "ultimo_acceso_ip",
                    models.GenericIPAddressField(
                        blank=True, null=True, verbose_name="Última IP de Acceso"
                    ),
                ),
                (
                    "intentos_fallidos",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Contador de intentos de login fallidos",
                        verbose_name="Intentos de Login Fallidos",
                    ),
                ),
                (
                    "bloqueado_hasta",
                    models.DateTimeField(
                        blank=True,
                        help_text="Fecha hasta cuando está bloqueado el usuario",
                        null=True,
                        verbose_name="Bloqueado Hasta",
                    ),
                ),
                (
                    "notificaciones_email",
                    models.BooleanField(
                        default=True,
                        help_text="Recibir notificaciones por correo electrónico",
                        verbose_name="Notificaciones por Email",
                    ),
                ),
                (
                    "notificaciones_sistema",
                    models.BooleanField(
                        default=True,
                        help_text="Recibir notificaciones en el sistema",
                        verbose_name="Notificaciones del Sistema",
                    ),
                ),
                (
                    "empresa",
                    models.ForeignKey(
                        blank=True,
                        help_text="Empresa a la que pertenece el usuario",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="usuarios",
                        to="core.empresa",
                        verbose_name="Empresa",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "sucursales",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Sucursales donde puede trabajar este usuario",
                        related_name="usuarios_asignados",
                        to="core.sucursal",
                        verbose_name="Sucursales Asignadas",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "Usuario",
                "verbose_name_plural": "Usuarios",
                "db_table": "usuarios_usuario",
                "ordering": ["username"],
                "permissions": [
                    ("puede_ver_todas_empresas", "Puede ver todas las empresas"),
                    ("puede_cambiar_roles", "Puede cambiar roles de usuarios"),
                    ("puede_reiniciar_passwords", "Puede reiniciar contraseñas"),
                    ("puede_bloquear_usuarios", "Puede bloquear/desbloquear usuarios"),
                    ("puede_ver_auditoria", "Puede ver logs de auditoría"),
                ],
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="SesionUsuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "token_jti",
                    models.CharField(
                        help_text="JWT Token Identifier",
                        max_length=255,
                        unique=True,
                        verbose_name="Token JTI",
                    ),
                ),
                (
                    "ip_address",
                    models.GenericIPAddressField(verbose_name="Dirección IP"),
                ),
                (
                    "user_agent",
                    models.TextField(
                        blank=True,
                        help_text="Información del navegador/dispositivo",
                        verbose_name="User Agent",
                    ),
                ),
                (
                    "fecha_inicio",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de Inicio"
                    ),
                ),
                (
                    "fecha_ultimo_uso",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha de Último Uso"
                    ),
                ),
                (
                    "activa",
                    models.BooleanField(default=True, verbose_name="Sesión Activa"),
                ),
                (
                    "dispositivo",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Dispositivo"
                    ),
                ),
                (
                    "ubicacion",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Ubicación"
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sesiones",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sesión de Usuario",
                "verbose_name_plural": "Sesiones de Usuario",
                "db_table": "usuarios_sesion",
                "ordering": ["-fecha_ultimo_uso"],
                "indexes": [
                    models.Index(
                        fields=["usuario", "activa"],
                        name="usuarios_se_usuario_7b5ede_idx",
                    ),
                    models.Index(
                        fields=["token_jti"], name="usuarios_se_token_j_334ba2_idx"
                    ),
                    models.Index(
                        fields=["fecha_ultimo_uso"],
                        name="usuarios_se_fecha_u_4a0c83_idx",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="LogAuditoria",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "accion",
                    models.CharField(
                        choices=[
                            ("login", "Inicio de Sesión"),
                            ("logout", "Cierre de Sesión"),
                            ("login_fallido", "Intento de Login Fallido"),
                            ("cambio_password", "Cambio de Contraseña"),
                            ("cambio_rol", "Cambio de Rol"),
                            ("bloqueo", "Bloqueo de Usuario"),
                            ("desbloqueo", "Desbloqueo de Usuario"),
                            ("creacion", "Creación de Registro"),
                            ("modificacion", "Modificación de Registro"),
                            ("eliminacion", "Eliminación de Registro"),
                            ("facturacion", "Acción de Facturación"),
                            ("anulacion", "Anulación de Comprobante"),
                            ("configuracion", "Cambio de Configuración"),
                            ("exportacion", "Exportación de Datos"),
                            ("importacion", "Importación de Datos"),
                        ],
                        max_length=20,
                        verbose_name="Acción",
                    ),
                ),
                (
                    "modelo",
                    models.CharField(
                        blank=True,
                        help_text="Modelo Django afectado",
                        max_length=100,
                        verbose_name="Modelo",
                    ),
                ),
                (
                    "objeto_id",
                    models.CharField(
                        blank=True,
                        help_text="ID del objeto afectado",
                        max_length=50,
                        verbose_name="ID del Objeto",
                    ),
                ),
                (
                    "descripcion",
                    models.TextField(
                        help_text="Descripción detallada de la acción",
                        verbose_name="Descripción",
                    ),
                ),
                (
                    "datos_anteriores",
                    models.JSONField(
                        blank=True,
                        help_text="Estado anterior del objeto (para modificaciones)",
                        null=True,
                        verbose_name="Datos Anteriores",
                    ),
                ),
                (
                    "datos_nuevos",
                    models.JSONField(
                        blank=True,
                        help_text="Estado nuevo del objeto",
                        null=True,
                        verbose_name="Datos Nuevos",
                    ),
                ),
                (
                    "ip_address",
                    models.GenericIPAddressField(
                        blank=True, null=True, verbose_name="Dirección IP"
                    ),
                ),
                ("user_agent", models.TextField(blank=True, verbose_name="User Agent")),
                (
                    "fecha",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Fecha y hora de la acción",
                        verbose_name="Fecha",
                    ),
                ),
                (
                    "empresa",
                    models.ForeignKey(
                        blank=True,
                        help_text="Empresa en la que se realizó la acción",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.empresa",
                        verbose_name="Empresa",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="logs_auditoria",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Log de Auditoría",
                "verbose_name_plural": "Logs de Auditoría",
                "db_table": "usuarios_log_auditoria",
                "ordering": ["-fecha"],
                "indexes": [
                    models.Index(
                        fields=["usuario", "fecha"],
                        name="usuarios_lo_usuario_ba9fd8_idx",
                    ),
                    models.Index(
                        fields=["accion", "fecha"], name="usuarios_lo_accion_92ddf3_idx"
                    ),
                    models.Index(
                        fields=["modelo", "objeto_id"],
                        name="usuarios_lo_modelo_1807bd_idx",
                    ),
                    models.Index(
                        fields=["empresa", "fecha"],
                        name="usuarios_lo_empresa_4a39ac_idx",
                    ),
                ],
            },
        ),
    ]
