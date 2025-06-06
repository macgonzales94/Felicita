"""
Tests para el sistema de autenticación de FELICITA
Sistema de Facturación Electrónica para Perú
"""

from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from unittest.mock import patch, MagicMock

from .models import Usuario, SesionUsuario, LogActividad, RolUsuario
from .utils import (
    generar_password_temporal, validar_fortaleza_password,
    crear_token_personalizado, verificar_token_valido
)
from aplicaciones.empresas.models import Empresa


class UsuarioModelTest(TestCase):
    """
    Tests para el modelo Usuario
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.empresa = Empresa.objects.create(
            ruc='20123456789',
            razon_social='Empresa Test FELICITA',
            direccion='Lima, Perú'
        )
    
    def test_crear_usuario_basico(self):
        """Test crear usuario básico"""
        usuario = Usuario.objects.create_user(
            username='test_user',
            email='test@felicita.pe',
            password='test123',
            first_name='Test',
            last_name='User',
            numero_documento='12345678',
            empresa=self.empresa
        )
        
        self.assertEqual(usuario.username, 'test_user')
        self.assertEqual(usuario.email, 'test@felicita.pe')
        self.assertTrue(usuario.check_password('test123'))
        self.assertEqual(usuario.rol, RolUsuario.VENDEDOR)  # Rol por defecto
        self.assertEqual(usuario.empresa, self.empresa)
        self.assertTrue(usuario.is_active)
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
    
    def test_validacion_dni(self):
        """Test validación de DNI"""
        self.assertTrue(Usuario.validar_dni('12345678'))
        self.assertFalse(Usuario.validar_dni('1234567'))  # Muy corto
        self.assertFalse(Usuario.validar_dni('123456789'))  # Muy largo
        self.assertFalse(Usuario.validar_dni('1234567a'))  # Con letras
    
    def test_validacion_ruc(self):
        """Test validación de RUC"""
        # RUC válido conocido
        self.assertTrue(Usuario.validar_ruc('20123456789'))
        self.assertFalse(Usuario.validar_ruc('2012345678'))  # Muy corto
        self.assertFalse(Usuario.validar_ruc('201234567890'))  # Muy largo
        self.assertFalse(Usuario.validar_ruc('2012345678a'))  # Con letras
    
    def test_permisos_por_rol(self):
        """Test permisos según rol de usuario"""
        # Administrador
        admin = Usuario.objects.create_user(
            username='admin',
            email='admin@felicita.pe',
            password='admin123',
            rol=RolUsuario.ADMINISTRADOR,
            empresa=self.empresa
        )
        self.assertTrue(admin.es_administrador())
        self.assertTrue(admin.tiene_permiso('facturacion', 'crear'))
        
        # Contador
        contador = Usuario.objects.create_user(
            username='contador',
            email='contador@felicita.pe',
            password='contador123',
            rol=RolUsuario.CONTADOR,
            empresa=self.empresa
        )
        self.assertTrue(contador.es_contador())
        self.assertTrue(contador.tiene_permiso('contabilidad', 'ver'))
        
        # Vendedor
        vendedor = Usuario.objects.create_user(
            username='vendedor',
            email='vendedor@felicita.pe',
            password='vendedor123',
            rol=RolUsuario.VENDEDOR,
            empresa=self.empresa
        )
        self.assertTrue(vendedor.es_vendedor())
        self.assertTrue(vendedor.tiene_permiso('pos', 'crear'))
        self.assertFalse(vendedor.tiene_permiso('contabilidad', 'ver'))


class AutenticacionAPITest(APITestCase):
    """
    Tests para APIs de autenticación
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.client = APIClient()
        self.empresa = Empresa.objects.create(
            ruc='20123456789',
            razon_social='Empresa Test FELICITA',
            direccion='Lima, Perú'
        )
        
        self.usuario_test = Usuario.objects.create_user(
            username='test_user',
            email='test@felicita.pe',
            password='test123',
            first_name='Test',
            last_name='User',
            numero_documento='12345678',
            empresa=self.empresa
        )
    
    def test_login_exitoso(self):
        """Test login exitoso"""
        url = reverse('usuarios:login')
        data = {
            'username': 'test_user',
            'password': 'test123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('usuario', response.data)
        self.assertEqual(response.data['usuario']['username'], 'test_user')
    
    def test_login_credenciales_invalidas(self):
        """Test login con credenciales inválidas"""
        url = reverse('usuarios:login')
        data = {
            'username': 'test_user',
            'password': 'password_incorrecta'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_login_usuario_inactivo(self):
        """Test login con usuario inactivo"""
        self.usuario_test.is_active = False
        self.usuario_test.save()
        
        url = reverse('usuarios:login')
        data = {
            'username': 'test_user',
            'password': 'test123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_registro_exitoso(self):
        """Test registro de nuevo usuario"""
        url = reverse('usuarios:registro')
        data = {
            'username': 'nuevo_usuario',
            'email': 'nuevo@felicita.pe',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'password': 'nueva_password123',
            'confirmar_password': 'nueva_password123',
            'numero_documento': '87654321',
            'empresa': self.empresa.id
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Usuario.objects.filter(username='nuevo_usuario').exists())
    
    def test_registro_passwords_no_coinciden(self):
        """Test registro con contraseñas que no coinciden"""
        url = reverse('usuarios:registro')
        data = {
            'username': 'nuevo_usuario',
            'email': 'nuevo@felicita.pe',
            'password': 'password123',
            'confirmar_password': 'password456',
            'numero_documento': '87654321',
            'empresa': self.empresa.id
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirmar_password', response.data['detalles'])
    
    def test_verificar_token_valido(self):
        """Test verificación de token válido"""
        # Autenticar usuario
        refresh = RefreshToken.for_user(self.usuario_test)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('usuarios:verificar_token')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valido'])
        self.assertEqual(response.data['usuario']['username'], 'test_user')
    
    def test_cambiar_password(self):
        """Test cambio de contraseña"""
        # Autenticar usuario
        refresh = RefreshToken.for_user(self.usuario_test)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('usuarios:cambiar_password')
        data = {
            'password_actual': 'test123',
            'password_nueva': 'nueva_password123',
            'confirmar_password_nueva': 'nueva_password123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la contraseña cambió
        self.usuario_test.refresh_from_db()
        self.assertTrue(self.usuario_test.check_password('nueva_password123'))
    
    def test_cerrar_sesion(self):
        """Test cerrar sesión"""
        # Autenticar usuario
        refresh = RefreshToken.for_user(self.usuario_test)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('usuarios:logout')
        data = {'refresh': str(refresh)}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_perfil_usuario(self):
        """Test obtener y actualizar perfil"""
        # Autenticar usuario
        refresh = RefreshToken.for_user(self.usuario_test)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Obtener perfil
        url = reverse('usuarios:perfil')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'test_user')
        
        # Actualizar perfil
        data = {
            'first_name': 'Nombre Actualizado',
            'telefono': '+51 987654321',
            'tema_preferido': 'oscuro'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usuario_test.refresh_from_db()
        self.assertEqual(self.usuario_test.first_name, 'Nombre Actualizado')


class UtilidadesTest(TestCase):
    """
    Tests para utilidades de autenticación
    """
    
    def test_generar_password_temporal(self):
        """Test generación de contraseña temporal"""
        password = generar_password_temporal()
        
        self.assertEqual(len(password), 12)
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
    
    def test_validar_fortaleza_password(self):
        """Test validación de fortaleza de contraseña"""
        # Contraseña débil
        resultado = validar_fortaleza_password('123')
        self.assertFalse(resultado['valida'])
        self.assertEqual(resultado['nivel'], 'Débil')
        
        # Contraseña fuerte
        resultado = validar_fortaleza_password('MiPassword123!')
        self.assertTrue(resultado['valida'])
        self.assertEqual(resultado['nivel'], 'Excelente')
    
    def test_crear_token_personalizado(self):
        """Test creación de token personalizado"""
        empresa = Empresa.objects.create(
            ruc='20123456789',
            razon_social='Test Empresa',
            direccion='Lima'
        )
        
        usuario = Usuario.objects.create_user(
            username='test',
            email='test@test.com',
            password='test123',
            empresa=empresa,
            rol=RolUsuario.CONTADOR
        )
        
        tokens = crear_token_personalizado(usuario)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertIn('expires_in', tokens)
    
    def test_verificar_token_valido(self):
        """Test verificación de token válido"""
        usuario = Usuario.objects.create_user(
            username='test',
            email='test@test.com',
            password='test123'
        )
        
        refresh = RefreshToken.for_user(usuario)
        access_token = str(refresh.access_token)
        
        resultado = verificar_token_valido(access_token)
        
        self.assertTrue(resultado['valido'])
        self.assertEqual(resultado['usuario'], usuario)


class SeguridadTest(TestCase):
    """
    Tests para funcionalidades de seguridad
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.empresa = Empresa.objects.create(
            ruc='20123456789',
            razon_social='Test Empresa',
            direccion='Lima'
        )
        
        self.usuario = Usuario.objects.create_user(
            username='test_user',
            email='test@test.com',
            password='test123',
            empresa=self.empresa
        )
    
    def test_registro_actividad(self):
        """Test registro de actividad en logs"""
        LogActividad.registrar_actividad(
            usuario=self.usuario,
            accion='TEST_ACCION',
            modulo='TEST',
            descripcion='Test de actividad',
            direccion_ip='127.0.0.1'
        )
        
        log = LogActividad.objects.filter(usuario=self.usuario).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.accion, 'TEST_ACCION')
        self.assertEqual(log.modulo, 'TEST')
    
    def test_sesion_usuario(self):
        """Test gestión de sesiones de usuario"""
        sesion = SesionUsuario.objects.create(
            usuario=self.usuario,
            token_session='test_token',
            direccion_ip='127.0.0.1',
            user_agent='Test Agent'
        )
        
        self.assertTrue(sesion.activa)
        
        # Cerrar sesión
        sesion.cerrar_sesion()
        self.assertFalse(sesion.activa)
    
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    def test_rate_limiting(self):
        """Test rate limiting básico"""
        # Simular múltiples requests
        cache_key = 'rate_limit:127.0.0.1'
        
        # Verificar que no esté bloqueado inicialmente
        self.assertIsNone(cache.get(cache_key))
        
        # Simular requests
        for i in range(5):
            cache.set(cache_key, i + 1, 60)
        
        # Verificar que el contador funciona
        self.assertEqual(cache.get(cache_key), 5)


class PermisosTest(TestCase):
    """
    Tests para sistema de permisos
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.empresa = Empresa.objects.create(
            ruc='20123456789',
            razon_social='Test Empresa',
            direccion='Lima'
        )
    
    def test_permisos_administrador(self):
        """Test permisos de administrador"""
        admin = Usuario.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            rol=RolUsuario.ADMINISTRADOR,
            empresa=self.empresa
        )
        
        # Administrador debe tener todos los permisos
        self.assertTrue(admin.tiene_permiso('facturacion', 'crear'))
        self.assertTrue(admin.tiene_permiso('contabilidad', 'editar'))
        self.assertTrue(admin.tiene_permiso('usuarios', 'eliminar'))
    
    def test_permisos_vendedor(self):
        """Test permisos de vendedor"""
        vendedor = Usuario.objects.create_user(
            username='vendedor',
            email='vendedor@test.com',
            password='vendedor123',
            rol=RolUsuario.VENDEDOR,
            empresa=self.empresa
        )
        
        # Vendedor debe tener permisos limitados
        self.assertTrue(vendedor.tiene_permiso('pos', 'crear'))
        self.assertTrue(vendedor.tiene_permiso('clientes', 'ver'))
        self.assertFalse(vendedor.tiene_permiso('contabilidad', 'ver'))
        self.assertFalse(vendedor.tiene_permiso('usuarios', 'crear'))
    
    def test_permisos_especiales(self):
        """Test permisos especiales personalizados"""
        usuario = Usuario.objects.create_user(
            username='usuario_especial',
            email='especial@test.com',
            password='especial123',
            rol=RolUsuario.VENDEDOR,
            empresa=self.empresa
        )
        
        # Agregar permisos especiales
        usuario.permisos_especiales = {
            'contabilidad': {
                'ver': True,
                'crear': False
            }
        }
        usuario.save()
        
        # Verificar permisos especiales
        self.assertTrue(usuario.tiene_permiso('contabilidad', 'ver'))
        self.assertFalse(usuario.tiene_permiso('contabilidad', 'crear'))


class ComandosTest(TestCase):
    """
    Tests para comandos de gestión
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.empresa = Empresa.objects.create(
            ruc='20123456789',
            razon_social='Test Empresa',
            direccion='Lima'
        )
    
    @patch('sys.stdout')
    def test_comando_crear_usuarios_demo(self, mock_stdout):
        """Test comando para crear usuarios demo"""
        from django.core.management import call_command
        
        # Ejecutar comando
        call_command('crear_usuarios_demo', empresa_id=self.empresa.id, password='test123')
        
        # Verificar que los usuarios se crearon
        self.assertTrue(Usuario.objects.filter(username='admin').exists())
        self.assertTrue(Usuario.objects.filter(username='contador').exists())
        self.assertTrue(Usuario.objects.filter(username='vendedor1').exists())
        
        # Verificar roles
        admin = Usuario.objects.get(username='admin')
        self.assertEqual(admin.rol, RolUsuario.ADMINISTRADOR)
        self.assertTrue(admin.is_superuser)
        
        contador = Usuario.objects.get(username='contador')
        self.assertEqual(contador.rol, RolUsuario.CONTADOR)
        self.assertFalse(contador.is_superuser)