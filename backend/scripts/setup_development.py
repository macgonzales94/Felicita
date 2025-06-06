#!/usr/bin/env python3
"""
Script de configuración y validación para desarrollo de FELICITA
Sistema de Facturación Electrónica para Perú
FASE 2: Autenticación y Seguridad

Ejecutar: python scripts/setup_development.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


class FelicitaSetup:
    """
    Clase para configurar el entorno de desarrollo de FELICITA
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.logs = []
        
    def log(self, message, level="INFO"):
        """Registrar mensaje con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.logs.append(log_entry)
        
        # Colores para terminal
        colors = {
            "INFO": "\033[94m",      # Azul
            "SUCCESS": "\033[92m",   # Verde
            "WARNING": "\033[93m",   # Amarillo
            "ERROR": "\033[91m",     # Rojo
            "RESET": "\033[0m"       # Reset
        }
        
        color = colors.get(level, colors["INFO"])
        print(f"{color}{log_entry}{colors['RESET']}")
    
    def check_requirements(self):
        """Verificar requisitos del sistema"""
        self.log("🔍 Verificando requisitos del sistema...")
        
        # Verificar Python
        python_version = sys.version_info
        if python_version < (3, 8):
            self.log(f"❌ Python {python_version.major}.{python_version.minor} no es compatible. Se requiere Python 3.8+", "ERROR")
            return False
        else:
            self.log(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} OK", "SUCCESS")
        
        # Verificar PostgreSQL
        try:
            result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split()[2]
                self.log(f"✅ PostgreSQL {version} disponible", "SUCCESS")
            else:
                self.log("⚠️ PostgreSQL no encontrado. Asegúrate de tener Docker o PostgreSQL instalado", "WARNING")
        except FileNotFoundError:
            self.log("⚠️ PostgreSQL no encontrado en PATH. Verificar Docker Compose", "WARNING")
        
        # Verificar Redis
        try:
            result = subprocess.run(['redis-cli', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split()[1]
                self.log(f"✅ Redis {version} disponible", "SUCCESS")
            else:
                self.log("⚠️ Redis no encontrado. Asegúrate de tener Docker o Redis instalado", "WARNING")
        except FileNotFoundError:
            self.log("⚠️ Redis no encontrado en PATH. Verificar Docker Compose", "WARNING")
        
        return True
    
    def check_env_file(self):
        """Verificar archivo .env"""
        self.log("🔍 Verificando archivo .env...")
        
        env_path = self.base_dir / '.env'
        env_example_path = self.base_dir / '.env.example'
        
        if not env_path.exists():
            if env_example_path.exists():
                self.log("📋 Copiando .env.example a .env...", "INFO")
                import shutil
                shutil.copy(env_example_path, env_path)
                self.log("✅ Archivo .env creado desde .env.example", "SUCCESS")
            else:
                self.log("❌ No se encontró .env ni .env.example", "ERROR")
                return False
        
        # Verificar variables requeridas
        required_vars = [
            'DJANGO_SECRET_KEY',
            'DATABASE_NAME',
            'DATABASE_USER',
            'DATABASE_PASSWORD',
            'JWT_SECRET_KEY',
        ]
        
        missing_vars = []
        try:
            with open(env_path, 'r') as f:
                env_content = f.read()
                
            for var in required_vars:
                if f"{var}=" not in env_content or f"{var}=" in env_content and env_content.split(f"{var}=")[1].split('\n')[0].strip() == '':
                    missing_vars.append(var)
            
            if missing_vars:
                self.log(f"⚠️ Variables faltantes en .env: {', '.join(missing_vars)}", "WARNING")
                self.log("💡 Configura estas variables en .env antes de continuar", "INFO")
                return False
            else:
                self.log("✅ Todas las variables requeridas están en .env", "SUCCESS")
                
        except Exception as e:
            self.log(f"❌ Error leyendo .env: {e}", "ERROR")
            return False
        
        return True
    
    def check_database_connection(self):
        """Verificar conexión a base de datos"""
        self.log("🔍 Verificando conexión a base de datos...")
        
        try:
            # Intentar importar Django y conectar
            import django
            from django.conf import settings
            from django.db import connection
            
            # Configurar Django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'felicita.settings')
            django.setup()
            
            # Probar conexión
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            
            self.log("✅ Conexión a PostgreSQL exitosa", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Error conectando a base de datos: {e}", "ERROR")
            self.log("💡 Verifica que PostgreSQL esté corriendo: docker-compose up -d", "INFO")
            return False
    
    def run_migrations(self):
        """Ejecutar migraciones"""
        self.log("🔄 Ejecutando migraciones...")
        
        try:
            # Makemigrations
            result = subprocess.run([
                sys.executable, 'manage.py', 'makemigrations'
            ], cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Makemigrations ejecutado correctamente", "SUCCESS")
            else:
                self.log(f"⚠️ Makemigrations warnings: {result.stderr}", "WARNING")
            
            # Migrate
            result = subprocess.run([
                sys.executable, 'manage.py', 'migrate'
            ], cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Migraciones aplicadas correctamente", "SUCCESS")
                return True
            else:
                self.log(f"❌ Error en migraciones: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error ejecutando migraciones: {e}", "ERROR")
            return False
    
    def create_demo_users(self):
        """Crear usuarios de demostración"""
        self.log("👥 Creando usuarios de demostración...")
        
        try:
            result = subprocess.run([
                sys.executable, 'manage.py', 'crear_usuarios_demo'
            ], cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Usuarios de demostración creados", "SUCCESS")
                return True
            else:
                self.log(f"❌ Error creando usuarios demo: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error ejecutando comando de usuarios demo: {e}", "ERROR")
            return False
    
    def check_security_settings(self):
        """Verificar configuraciones de seguridad"""
        self.log("🔒 Verificando configuraciones de seguridad...")
        
        try:
            import django
            from django.conf import settings
            
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'felicita.settings')
            django.setup()
            
            security_checks = [
                ('SECRET_KEY definido', hasattr(settings, 'SECRET_KEY') and settings.SECRET_KEY),
                ('DEBUG es False en producción', not settings.DEBUG or settings.ENVIRONMENT == 'local'),
                ('Middleware de seguridad presente', 'aplicaciones.usuarios.middleware.SeguridadFelicitaMiddleware' in settings.MIDDLEWARE),
                ('JWT configurado', hasattr(settings, 'SIMPLE_JWT')),
                ('Rate limiting habilitado', getattr(settings, 'RATELIMIT_ENABLE', False)),
                ('CORS configurado', hasattr(settings, 'CORS_ALLOWED_ORIGINS')),
            ]
            
            all_passed = True
            for check_name, passed in security_checks:
                if passed:
                    self.log(f"✅ {check_name}", "SUCCESS")
                else:
                    self.log(f"❌ {check_name}", "ERROR")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log(f"❌ Error verificando configuraciones: {e}", "ERROR")
            return False
    
    def create_directories(self):
        """Crear directorios necesarios"""
        self.log("📁 Creando directorios necesarios...")
        
        directories = [
            'logs',
            'media',
            'static',
            'staticfiles',
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            if not dir_path.exists():
                dir_path.mkdir(exist_ok=True)
                self.log(f"✅ Directorio creado: {directory}", "SUCCESS")
            else:
                self.log(f"✅ Directorio existe: {directory}", "SUCCESS")
        
        return True
    
    def validate_apis(self):
        """Validar configuración de APIs"""
        self.log("🌐 Validando configuración de APIs...")
        
        try:
            import django
            from django.conf import settings
            
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'felicita.settings')
            django.setup()
            
            # Verificar URLs
            from django.urls import reverse
            from django.test import Client
            
            client = Client()
            
            # Test básico de API root
            try:
                response = client.get('/api/')
                if response.status_code == 200:
                    self.log("✅ API root accesible", "SUCCESS")
                else:
                    self.log(f"⚠️ API root devuelve {response.status_code}", "WARNING")
            except Exception as e:
                self.log(f"❌ Error accediendo API root: {e}", "ERROR")
            
            # Test documentación
            try:
                response = client.get('/api/docs/')
                if response.status_code == 200:
                    self.log("✅ Documentación API accesible", "SUCCESS")
                else:
                    self.log(f"⚠️ Documentación API devuelve {response.status_code}", "WARNING")
            except Exception as e:
                self.log(f"❌ Error accediendo documentación: {e}", "ERROR")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error validando APIs: {e}", "ERROR")
            return False
    
    def generate_summary(self):
        """Generar resumen de configuración"""
        self.log("📋 Generando resumen de configuración...")
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "environment": "local",
            "phase": "FASE 2 - Autenticación y Seguridad",
            "status": "configured",
            "endpoints": [
                "http://localhost:8000/api/",
                "http://localhost:8000/api/docs/",
                "http://localhost:8000/admin/",
            ],
            "demo_users": [
                {"username": "admin", "password": "felicita123", "role": "Administrador"},
                {"username": "contador", "password": "felicita123", "role": "Contador"},
                {"username": "vendedor1", "password": "felicita123", "role": "Vendedor"},
                {"username": "vendedor2", "password": "felicita123", "role": "Vendedor"},
                {"username": "cliente_demo", "password": "felicita123", "role": "Cliente"},
            ],
            "next_steps": [
                "Ejecutar: python manage.py runserver",
                "Acceder a: http://localhost:8000/api/docs/",
                "Probar login con usuarios demo",
                "Continuar con Fase 3: API Core y Nubefact"
            ]
        }
        
        # Guardar resumen
        summary_path = self.base_dir / 'setup_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        self.log(f"✅ Resumen guardado en: {summary_path}", "SUCCESS")
        
        # Mostrar resumen en consola
        print("\n" + "="*60)
        print("🎉 CONFIGURACIÓN COMPLETADA - FELICITA FASE 2")
        print("="*60)
        print(f"📅 Configurado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"🏗️ Entorno: {summary['environment']}")
        print(f"🚀 Fase: {summary['phase']}")
        
        print("\n🌐 ENDPOINTS DISPONIBLES:")
        for endpoint in summary['endpoints']:
            print(f"   • {endpoint}")
        
        print("\n👥 USUARIOS DEMO:")
        for user in summary['demo_users']:
            print(f"   • {user['username']} / {user['password']} ({user['role']})")
        
        print("\n🔧 PRÓXIMOS PASOS:")
        for step in summary['next_steps']:
            print(f"   • {step}")
        
        print("\n" + "="*60)
        
        return True
    
    def run_setup(self):
        """Ejecutar configuración completa"""
        print("🚀 Iniciando configuración de FELICITA - FASE 2")
        print("Sistema de Facturación Electrónica para Perú")
        print("=" * 60)
        
        steps = [
            ("Verificar requisitos", self.check_requirements),
            ("Verificar archivo .env", self.check_env_file),
            ("Crear directorios", self.create_directories),
            ("Verificar base de datos", self.check_database_connection),
            ("Ejecutar migraciones", self.run_migrations),
            ("Crear usuarios demo", self.create_demo_users),
            ("Verificar seguridad", self.check_security_settings),
            ("Validar APIs", self.validate_apis),
            ("Generar resumen", self.generate_summary),
        ]
        
        success_count = 0
        total_steps = len(steps)
        
        for i, (step_name, step_function) in enumerate(steps, 1):
            print(f"\n📋 Paso {i}/{total_steps}: {step_name}")
            print("-" * 40)
            
            try:
                if step_function():
                    success_count += 1
                    self.log(f"✅ {step_name} completado", "SUCCESS")
                else:
                    self.log(f"❌ {step_name} falló", "ERROR")
            except Exception as e:
                self.log(f"❌ Error en {step_name}: {e}", "ERROR")
        
        # Resultado final
        print("\n" + "="*60)
        if success_count == total_steps:
            print("🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
            print("✅ Todos los pasos se ejecutaron correctamente")
            print("\n🚀 Puedes ejecutar: python manage.py runserver")
            return True
        else:
            print(f"⚠️ Configuración parcial: {success_count}/{total_steps} pasos completados")
            print("💡 Revisa los errores anteriores y vuelve a ejecutar")
            return False


if __name__ == "__main__":
    setup = FelicitaSetup()
    success = setup.run_setup()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)