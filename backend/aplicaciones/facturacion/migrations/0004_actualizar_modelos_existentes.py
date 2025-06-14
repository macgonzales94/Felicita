from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0003_agregar_items_faltantes'),
    ]

    operations = [
        # Agregar campos faltantes a NotaDebito si no existen
        migrations.RunSQL(
            "ALTER TABLE facturacion_nota_debito ADD COLUMN IF NOT EXISTS tipo_documento_modificado VARCHAR(2);",
            reverse_sql="ALTER TABLE facturacion_nota_debito DROP COLUMN IF EXISTS tipo_documento_modificado;"
        ),
        migrations.RunSQL(
            "ALTER TABLE facturacion_nota_debito ADD COLUMN IF NOT EXISTS numero_documento_modificado VARCHAR(20);",
            reverse_sql="ALTER TABLE facturacion_nota_debito DROP COLUMN IF EXISTS numero_documento_modificado;"
        ),
        migrations.RunSQL(
            "ALTER TABLE facturacion_nota_debito ADD COLUMN IF NOT EXISTS codigo_motivo VARCHAR(2);",
            reverse_sql="ALTER TABLE facturacion_nota_debito DROP COLUMN IF EXISTS codigo_motivo;"
        ),
        migrations.RunSQL(
            "ALTER TABLE facturacion_nota_debito ADD COLUMN IF NOT EXISTS descripcion_motivo TEXT;",
            reverse_sql="ALTER TABLE facturacion_nota_debito DROP COLUMN IF EXISTS descripcion_motivo;"
        ),
        
        # Agregar campos faltantes a GuiaRemision si no existen
        migrations.RunSQL(
            "ALTER TABLE facturacion_guia_remision ADD COLUMN IF NOT EXISTS ubigeo_destino VARCHAR(6);",
            reverse_sql="ALTER TABLE facturacion_guia_remision DROP COLUMN IF EXISTS ubigeo_destino;"
        ),
        migrations.RunSQL(
            "ALTER TABLE facturacion_guia_remision ADD COLUMN IF NOT EXISTS transportista_ruc VARCHAR(11);",
            reverse_sql="ALTER TABLE facturacion_guia_remision DROP COLUMN IF EXISTS transportista_ruc;"
        ),
        migrations.RunSQL(
            "ALTER TABLE facturacion_guia_remision ADD COLUMN IF NOT EXISTS transportista_nombre VARCHAR(200);",
            reverse_sql="ALTER TABLE facturacion_guia_remision DROP COLUMN IF EXISTS transportista_nombre;"
        ),
        migrations.RunSQL(
            "ALTER TABLE facturacion_guia_remision ADD COLUMN IF NOT EXISTS vehiculo_placa VARCHAR(10);",
            reverse_sql="ALTER TABLE facturacion_guia_remision DROP COLUMN IF EXISTS vehiculo_placa;"
        ),
        migrations.RunSQL(
            "ALTER TABLE facturacion_guia_remision ADD COLUMN IF NOT EXISTS conductor_licencia VARCHAR(20);",
            reverse_sql="ALTER TABLE facturacion_guia_remision DROP COLUMN IF EXISTS conductor_licencia;"
        ),
        migrations.RunSQL(
            "ALTER TABLE facturacion_guia_remision ADD COLUMN IF NOT EXISTS conductor_nombre VARCHAR(200);",
            reverse_sql="ALTER TABLE facturacion_guia_remision DROP COLUMN IF EXISTS conductor_nombre;"
        ),
        migrations.RunSQL(
            "ALTER TABLE facturacion_guia_remision ADD COLUMN IF NOT EXISTS estado_sunat VARCHAR(20) DEFAULT 'PENDIENTE';",
            reverse_sql="ALTER TABLE facturacion_guia_remision DROP COLUMN IF EXISTS estado_sunat;"
        ),
        migrations.RunSQL(
            "ALTER TABLE facturacion_guia_remision ADD COLUMN IF NOT EXISTS nubefact_id VARCHAR(50);",
            reverse_sql="ALTER TABLE facturacion_guia_remision DROP COLUMN IF EXISTS nubefact_id;"
        ),
        migrations.RunSQL(
            "ALTER TABLE facturacion_guia_remision ADD COLUMN IF NOT EXISTS hash_cpe VARCHAR(100);",
            reverse_sql="ALTER TABLE facturacion_guia_remision DROP COLUMN IF EXISTS hash_cpe;"
        ),
    ]


# =============================================================================
# COMANDOS PARA EJECUTAR LAS MIGRACIONES
# =============================================================================

"""
# Ejecutar en la terminal para aplicar las migraciones:

# 1. Crear las migraciones automáticamente
python manage.py makemigrations facturacion
python manage.py makemigrations contabilidad

# 2. Aplicar las migraciones
python manage.py migrate facturacion
python manage.py migrate contabilidad

# 3. Crear superusuario si no existe
python manage.py createsuperuser

# 4. Cargar datos iniciales
python manage.py loaddata fixtures/plan_cuentas_pcge.json
python manage.py loaddata fixtures/series_comprobantes.json
python manage.py loaddata fixtures/datos_iniciales.json

# 5. Generar esquema de la base de datos (opcional)
python manage.py sqlmigrate facturacion 0003
python manage.py sqlmigrate contabilidad 0003

# 6. Verificar estado de migraciones
python manage.py showmigrations
"""