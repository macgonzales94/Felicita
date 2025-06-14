from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0002_initial_data'),  # Ajustar según la última migración
        ('inventario', '0001_initial'),
    ]

    operations = [
        # Crear modelo ItemNotaCredito
        migrations.CreateModel(
            name='ItemNotaCredito',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('numero_item', models.PositiveIntegerField(verbose_name='Número de Item')),
                ('descripcion', models.CharField(max_length=500, verbose_name='Descripción')),
                ('unidad_medida', models.CharField(default='NIU', max_length=10, verbose_name='Unidad de Medida')),
                ('cantidad', models.DecimalField(decimal_places=4, max_digits=12, verbose_name='Cantidad')),
                ('precio_unitario', models.DecimalField(decimal_places=4, max_digits=12, verbose_name='Precio Unitario')),
                ('descuento_unitario', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=12, verbose_name='Descuento Unitario')),
                ('valor_venta', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Valor de Venta')),
                ('tipo_afectacion_igv', models.CharField(choices=[('10', 'Gravado - Operación Onerosa'), ('11', 'Gravado - Retiro por premio'), ('12', 'Gravado - Retiro por donación'), ('13', 'Gravado - Retiro'), ('14', 'Gravado - Retiro por publicidad'), ('15', 'Gravado - Bonificaciones'), ('16', 'Gravado - Retiro por entrega a trabajadores'), ('17', 'Gravado - IVAP'), ('20', 'Exonerado - Operación Onerosa'), ('21', 'Exonerado - Transferencia Gratuita'), ('30', 'Inafecto - Operación Onerosa'), ('31', 'Inafecto - Retiro por Bonificación'), ('32', 'Inafecto - Retiro'), ('33', 'Inafecto - Retiro por Muestras Médicas'), ('34', 'Inafecto - Retiro por Convenio Colectivo'), ('35', 'Inafecto - Retiro por premio'), ('36', 'Inafecto - Retiro por publicidad'), ('40', 'Exportación')], default='10', max_length=2, verbose_name='Tipo de Afectación IGV')),
                ('porcentaje_igv', models.DecimalField(decimal_places=2, default=Decimal('18.00'), max_digits=5, verbose_name='Porcentaje IGV')),
                ('igv', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='IGV')),
                ('precio_total', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Precio Total')),
                ('nota_credito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='facturacion.notacredito', verbose_name='Nota de Crédito')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventario.producto', verbose_name='Producto')),
            ],
            options={
                'verbose_name': 'Item de Nota de Crédito',
                'verbose_name_plural': 'Items de Notas de Crédito',
                'db_table': 'facturacion_nota_credito_item',
                'ordering': ['numero_item'],
            },
        ),
        
        # Crear modelo ItemNotaDebito
        migrations.CreateModel(
            name='ItemNotaDebito',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('numero_item', models.PositiveIntegerField(verbose_name='Número de Item')),
                ('descripcion', models.CharField(max_length=500, verbose_name='Descripción')),
                ('unidad_medida', models.CharField(default='NIU', max_length=10, verbose_name='Unidad de Medida')),
                ('cantidad', models.DecimalField(decimal_places=4, max_digits=12, verbose_name='Cantidad')),
                ('precio_unitario', models.DecimalField(decimal_places=4, max_digits=12, verbose_name='Precio Unitario')),
                ('descuento_unitario', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=12, verbose_name='Descuento Unitario')),
                ('valor_venta', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Valor de Venta')),
                ('tipo_afectacion_igv', models.CharField(choices=[('10', 'Gravado - Operación Onerosa'), ('11', 'Gravado - Retiro por premio'), ('12', 'Gravado - Retiro por donación'), ('13', 'Gravado - Retiro'), ('14', 'Gravado - Retiro por publicidad'), ('15', 'Gravado - Bonificaciones'), ('16', 'Gravado - Retiro por entrega a trabajadores'), ('17', 'Gravado - IVAP'), ('20', 'Exonerado - Operación Onerosa'), ('21', 'Exonerado - Transferencia Gratuita'), ('30', 'Inafecto - Operación Onerosa'), ('31', 'Inafecto - Retiro por Bonificación'), ('32', 'Inafecto - Retiro'), ('33', 'Inafecto - Retiro por Muestras Médicas'), ('34', 'Inafecto - Retiro por Convenio Colectivo'), ('35', 'Inafecto - Retiro por premio'), ('36', 'Inafecto - Retiro por publicidad'), ('40', 'Exportación')], default='10', max_length=2, verbose_name='Tipo de Afectación IGV')),
                ('porcentaje_igv', models.DecimalField(decimal_places=2, default=Decimal('18.00'), max_digits=5, verbose_name='Porcentaje IGV')),
                ('igv', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='IGV')),
                ('precio_total', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Precio Total')),
                ('nota_debito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='facturacion.notadebito', verbose_name='Nota de Débito')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventario.producto', verbose_name='Producto')),
            ],
            options={
                'verbose_name': 'Item de Nota de Débito',
                'verbose_name_plural': 'Items de Notas de Débito',
                'db_table': 'facturacion_nota_debito_item',
                'ordering': ['numero_item'],
            },
        ),
        
        # Crear modelo ItemGuiaRemision
        migrations.CreateModel(
            name='ItemGuiaRemision',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('numero_item', models.PositiveIntegerField(verbose_name='Número de Item')),
                ('descripcion', models.CharField(max_length=500, verbose_name='Descripción')),
                ('unidad_medida', models.CharField(default='NIU', max_length=10, verbose_name='Unidad de Medida')),
                ('cantidad', models.DecimalField(decimal_places=4, max_digits=12, verbose_name='Cantidad')),
                ('peso_unitario', models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=10, verbose_name='Peso Unitario (kg)')),
                ('peso_total', models.DecimalField(decimal_places=4, max_digits=12, verbose_name='Peso Total (kg)')),
                ('guia_remision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='facturacion.guiaremision', verbose_name='Guía de Remisión')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventario.producto', verbose_name='Producto')),
            ],
            options={
                'verbose_name': 'Item de Guía de Remisión',
                'verbose_name_plural': 'Items de Guías de Remisión',
                'db_table': 'facturacion_guia_remision_item',
                'ordering': ['numero_item'],
            },
        ),
        
        # Agregar constraints únicos
        migrations.AddConstraint(
            model_name='itemnotacredito',
            constraint=models.UniqueConstraint(fields=['nota_credito', 'numero_item'], name='unique_item_nota_credito'),
        ),
        migrations.AddConstraint(
            model_name='itemnotadebito',
            constraint=models.UniqueConstraint(fields=['nota_debito', 'numero_item'], name='unique_item_nota_debito'),
        ),
        migrations.AddConstraint(
            model_name='itemguiaremision',
            constraint=models.UniqueConstraint(fields=['guia_remision', 'numero_item'], name='unique_item_guia_remision'),
        ),
        
        # Crear índices para mejorar rendimiento
        migrations.AddIndex(
            model_name='itemnotacredito',
            index=models.Index(fields=['nota_credito', 'numero_item'], name='idx_item_nc_orden'),
        ),
        migrations.AddIndex(
            model_name='itemnotadebito',
            index=models.Index(fields=['nota_debito', 'numero_item'], name='idx_item_nd_orden'),
        ),
        migrations.AddIndex(
            model_name='itemguiaremision',
            index=models.Index(fields=['guia_remision', 'numero_item'], name='idx_item_gr_orden'),
        ),
    ]
