
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contabilidad', '0002_initial_data'),  # Ajustar según la última migración
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Crear modelo PeriodoContable
        migrations.CreateModel(
            name='PeriodoContable',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('año', models.PositiveIntegerField(verbose_name='Año')),
                ('mes', models.PositiveIntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)], null=True, verbose_name='Mes')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre del Período')),
                ('fecha_inicio', models.DateField(verbose_name='Fecha de Inicio')),
                ('fecha_fin', models.DateField(verbose_name='Fecha de Fin')),
                ('estado', models.CharField(choices=[('abierto', 'Abierto'), ('cerrado', 'Cerrado'), ('auditoria', 'En Auditoría'), ('bloqueado', 'Bloqueado')], default='abierto', max_length=15, verbose_name='Estado del Período')),
                ('es_periodo_principal', models.BooleanField(default=True, verbose_name='Es Período Principal')),
                ('fecha_cierre', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Cierre')),
                ('observaciones_cierre', models.TextField(blank=True, verbose_name='Observaciones del Cierre')),
                ('permite_reapertura', models.BooleanField(default=True, verbose_name='Permite Reapertura')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='periodos_contables', to='core.empresa', verbose_name='Empresa')),
                ('usuario_cierre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='periodos_cerrados', to=settings.AUTH_USER_MODEL, verbose_name='Usuario que Cerró')),
            ],
            options={
                'verbose_name': 'Período Contable',
                'verbose_name_plural': 'Períodos Contables',
                'db_table': 'contabilidad_periodo_contable',
                'ordering': ['-año', '-mes'],
            },
        ),
        
        # Crear modelo BalanceComprobacion
        migrations.CreateModel(
            name='BalanceComprobacion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('fecha_desde', models.DateField(verbose_name='Fecha Desde')),
                ('fecha_hasta', models.DateField(verbose_name='Fecha Hasta')),
                ('saldo_inicial_debe', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Saldo Inicial Debe')),
                ('saldo_inicial_haber', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Saldo Inicial Haber')),
                ('movimientos_debe', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Movimientos Debe')),
                ('movimientos_haber', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Movimientos Haber')),
                ('saldo_final_debe', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Saldo Final Debe')),
                ('saldo_final_haber', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Saldo Final Haber')),
                ('fecha_generacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Generación')),
                ('es_balance_oficial', models.BooleanField(default=False, verbose_name='Es Balance Oficial')),
                ('observaciones', models.TextField(blank=True, verbose_name='Observaciones')),
                ('cuenta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balances_comprobacion', to='contabilidad.cuentacontable', verbose_name='Cuenta Contable')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balances_comprobacion', to='core.empresa', verbose_name='Empresa')),
                ('periodo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balances_comprobacion', to='contabilidad.periodocontable', verbose_name='Período Contable')),
                ('usuario_generacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Usuario que Generó')),
            ],
            options={
                'verbose_name': 'Balance de Comprobación',
                'verbose_name_plural': 'Balances de Comprobación',
                'db_table': 'contabilidad_balance_comprobacion',
                'ordering': ['cuenta__codigo', 'fecha_desde'],
            },
        ),
        
        # Agregar constraints únicos
        migrations.AddConstraint(
            model_name='periodocontable',
            constraint=models.UniqueConstraint(fields=['empresa', 'año', 'mes'], name='unique_periodo_empresa_año_mes'),
        ),
        migrations.AddConstraint(
            model_name='balancecomprobacion',
            constraint=models.UniqueConstraint(fields=['empresa', 'periodo', 'cuenta', 'fecha_desde', 'fecha_hasta'], name='unique_balance_empresa_periodo_cuenta_fechas'),
        ),
        
        # Crear índices para mejorar rendimiento
        migrations.AddIndex(
            model_name='periodocontable',
            index=models.Index(fields=['empresa', 'año'], name='idx_periodo_empresa_año'),
        ),
        migrations.AddIndex(
            model_name='periodocontable',
            index=models.Index(fields=['estado'], name='idx_periodo_estado'),
        ),
        migrations.AddIndex(
            model_name='periodocontable',
            index=models.Index(fields=['es_periodo_principal'], name='idx_periodo_principal'),
        ),
        migrations.AddIndex(
            model_name='balancecomprobacion',
            index=models.Index(fields=['empresa', 'periodo'], name='idx_balance_empresa_periodo'),
        ),
        migrations.AddIndex(
            model_name='balancecomprobacion',
            index=models.Index(fields=['fecha_desde', 'fecha_hasta'], name='idx_balance_fechas'),
        ),
        migrations.AddIndex(
            model_name='balancecomprobacion',
            index=models.Index(fields=['es_balance_oficial'], name='idx_balance_oficial'),
        ),
    ]