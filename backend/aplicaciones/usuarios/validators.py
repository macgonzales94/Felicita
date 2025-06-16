"""
FELICITA - Validadores de Contraseña Personalizados
Sistema de Facturación Electrónica para Perú

Validadores personalizados para contraseñas seguras
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

# ===========================================
# VALIDADOR PERSONALIZADO PRINCIPAL
# ===========================================

class CustomPasswordValidator:
    """
    Validador personalizado para contraseñas de FELICITA
    
    Requiere:
    - Al menos 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial
    - No puede contener espacios
    - No puede ser una secuencia común
    """
    
    def __init__(self, 
                 min_length=8,
                 require_uppercase=True,
                 require_lowercase=True,
                 require_numbers=True,
                 require_special=True,
                 allow_spaces=False):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_special = require_special
        self.allow_spaces = allow_spaces
        
        # Caracteres especiales permitidos
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Secuencias comunes prohibidas
        self.common_sequences = [
            '12345', '54321', 'abcde', 'edcba',
            'qwerty', 'asdfg', 'zxcvb',
            '11111', '22222', '33333', '44444', '55555',
            '66666', '77777', '88888', '99999', '00000'
        ]
    
    def validate(self, password, user=None):
        """Validar contraseña"""
        errors = []
        
        # Verificar longitud mínima
        if len(password) < self.min_length:
            errors.append(_(f'La contraseña debe tener al menos {self.min_length} caracteres.'))
        
        # Verificar letra mayúscula
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append(_('La contraseña debe contener al menos una letra mayúscula.'))
        
        # Verificar letra minúscula
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append(_('La contraseña debe contener al menos una letra minúscula.'))
        
        # Verificar números
        if self.require_numbers and not re.search(r'\d', password):
            errors.append(_('La contraseña debe contener al menos un número.'))
        
        # Verificar caracteres especiales
        if self.require_special and not re.search(f'[{re.escape(self.special_chars)}]', password):
            errors.append(_('La contraseña debe contener al menos un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?).'))
        
        # Verificar espacios
        if not self.allow_spaces and ' ' in password:
            errors.append(_('La contraseña no puede contener espacios.'))
        
        # Verificar secuencias comunes
        password_lower = password.lower()
        for sequence in self.common_sequences:
            if sequence in password_lower:
                errors.append(_('La contraseña no puede contener secuencias comunes como "12345" o "qwerty".'))
                break
        
        # Verificar que no sea igual al username si hay user
        if user and hasattr(user, 'username'):
            if password.lower() == user.username.lower():
                errors.append(_('La contraseña no puede ser igual al nombre de usuario.'))
        
        # Verificar que no sea igual al email si hay user
        if user and hasattr(user, 'email'):
            if password.lower() == user.email.lower():
                errors.append(_('La contraseña no puede ser igual al correo electrónico.'))
        
        # Verificar repetición de caracteres consecutivos
        if self._has_too_many_repeated_chars(password):
            errors.append(_('La contraseña no puede tener más de 2 caracteres iguales consecutivos.'))
        
        if errors:
            raise ValidationError(errors)
    
    def _has_too_many_repeated_chars(self, password, max_repeat=2):
        """Verificar si hay demasiados caracteres repetidos consecutivos"""
        count = 1
        for i in range(1, len(password)):
            if password[i] == password[i-1]:
                count += 1
                if count > max_repeat:
                    return True
            else:
                count = 1
        return False
    
    def get_help_text(self):
        """Texto de ayuda para el validador"""
        help_texts = [
            f'La contraseña debe tener al menos {self.min_length} caracteres'
        ]
        
        if self.require_uppercase:
            help_texts.append('al menos una letra mayúscula')
        
        if self.require_lowercase:
            help_texts.append('al menos una letra minúscula')
        
        if self.require_numbers:
            help_texts.append('al menos un número')
        
        if self.require_special:
            help_texts.append('al menos un carácter especial')
        
        if not self.allow_spaces:
            help_texts.append('sin espacios')
        
        return _('Su contraseña debe contener: ') + ', '.join(help_texts) + '.'

# ===========================================
# VALIDADOR DE CONTRASEÑAS COMUNES
# ===========================================

class CommonPasswordValidator:
    """Validador para prevenir contraseñas comunes específicas del contexto peruano"""
    
    def __init__(self):
        # Contraseñas comunes en el contexto peruano/empresarial
        self.common_passwords = {
            # Contraseñas generales
            'password', 'contraseña', 'clave', 'admin', 'administrador',
            'usuario', 'user', 'felicita', 'sistema',
            
            # Fechas comunes
            '20242024', '20232023', '20222022', '20212021',
            '01012024', '31122023', '28071821',  # Independencia del Perú
            
            # Nombres comunes en Perú
            'maria123', 'carlos123', 'ana123', 'jose123', 'juan123',
            'luis123', 'rosa123', 'pedro123', 'carmen123',
            
            # Palabras relacionadas con Perú
            'peru123', 'lima123', 'inca123', 'machu123', 'picchu123',
            'cusco123', 'arequipa123', 'trujillo123',
            
            # Términos empresariales
            'empresa123', 'negocio123', 'oficina123', 'trabajo123',
            'factura123', 'sunat123', 'igv123', 'ruc123',
            
            # Secuencias de teclado
            'qwerty123', 'asdf123', 'zxcv123', '1qaz2wsx',
            'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
            
            # Patrones comunes
            'abc123', '123abc', 'a1b2c3', '1a2b3c',
            'password1', 'password123', 'admin123',
        }
    
    def validate(self, password, user=None):
        """Validar que la contraseña no sea común"""
        password_lower = password.lower()
        
        if password_lower in self.common_passwords:
            raise ValidationError(
                _('Esta contraseña es muy común. Por favor, elija una contraseña más segura.'),
                code='password_too_common'
            )
        
        # Verificar variaciones con números al final
        base_password = re.sub(r'\d+$', '', password_lower)
        if base_password in self.common_passwords:
            raise ValidationError(
                _('Esta contraseña es una variación de una contraseña común. Por favor, elija una contraseña más segura.'),
                code='password_too_common'
            )
    
    def get_help_text(self):
        """Texto de ayuda"""
        return _('Su contraseña no puede ser una contraseña común como "password123" o "admin123".')

# ===========================================
# VALIDADOR DE HISTORIAL DE CONTRASEÑAS
# ===========================================

class PasswordHistoryValidator:
    """Validador para prevenir reutilización de contraseñas anteriores"""
    
    def __init__(self, history_count=5):
        self.history_count = history_count
    
    def validate(self, password, user=None):
        """Validar contra historial de contraseñas"""
        if not user or not hasattr(user, 'pk') or not user.pk:
            return  # Usuario nuevo, no hay historial
        
        # Importar aquí para evitar circular import
        from .models import Usuario
        
        try:
            # Verificar si el usuario tiene historial de contraseñas
            if hasattr(user, 'password_history'):
                # Obtener las últimas contraseñas
                last_passwords = user.password_history.order_by('-created_at')[:self.history_count]
                
                for password_history in last_passwords:
                    if user.check_password(password):
                        raise ValidationError(
                            _(f'No puede reutilizar una de sus últimas {self.history_count} contraseñas.'),
                            code='password_recently_used'
                        )
        except Exception:
            # Si hay algún error, simplemente continuar
            pass
    
    def get_help_text(self):
        """Texto de ayuda"""
        return _(f'Su contraseña no puede ser igual a ninguna de sus últimas {self.history_count} contraseñas.')

# ===========================================
# VALIDADOR DE PALABRAS PROHIBIDAS
# ===========================================

class ForbiddenWordsValidator:
    """Validador para prevenir palabras específicamente prohibidas"""
    
    def __init__(self):
        # Palabras prohibidas en contraseñas
        self.forbidden_words = {
            # Información de la empresa
            'felicita', 'facturacion', 'electronica',
            
            # Términos técnicos que no deberían estar en contraseñas
            'database', 'servidor', 'backup', 'admin', 'root',
            'superuser', 'administrador', 'postgres', 'mysql',
            
            # Información sensible
            'sunat', 'afip', 'ruc', 'dni', 'cuit', 'cuil',
            'nubefact', 'api', 'token', 'secret', 'key',
            
            # Términos financieros
            'factura', 'boleta', 'credito', 'debito',
            'impuesto', 'igv', 'iva', 'precio', 'costo',
            
            # Palabras obvias
            'test', 'prueba', 'demo', 'ejemplo', 'sample',
            'default', 'temporal', 'temp', 'cambiar',
        }
    
    def validate(self, password, user=None):
        """Validar que no contenga palabras prohibidas"""
        password_lower = password.lower()
        
        for word in self.forbidden_words:
            if word in password_lower:
                raise ValidationError(
                    _(f'La contraseña no puede contener la palabra "{word}".'),
                    code='forbidden_word_in_password'
                )
    
    def get_help_text(self):
        """Texto de ayuda"""
        return _('Su contraseña no puede contener palabras relacionadas con el sistema o información sensible.')

# ===========================================
# VALIDADOR DE COMPLEJIDAD AVANZADA
# ===========================================

class AdvancedComplexityValidator:
    """Validador de complejidad avanzada que calcula un score"""
    
    def __init__(self, min_score=60):
        self.min_score = min_score
    
    def validate(self, password, user=None):
        """Validar complejidad usando un sistema de puntos"""
        score = self._calculate_password_score(password)
        
        if score < self.min_score:
            raise ValidationError(
                _(f'La contraseña no es lo suficientemente compleja. '
                  f'Puntuación actual: {score}. Mínimo requerido: {self.min_score}.'),
                code='password_not_complex_enough'
            )
    
    def _calculate_password_score(self, password):
        """Calcular puntuación de complejidad de la contraseña"""
        score = 0
        
        # Puntos por longitud
        length = len(password)
        if length >= 8:
            score += 10
        if length >= 12:
            score += 15
        if length >= 16:
            score += 20
        
        # Puntos por variedad de caracteres
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 15
        if re.search(r'\d', password):
            score += 15
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 25
        
        # Puntos por no tener patrones repetitivos
        if not self._has_repetitive_patterns(password):
            score += 10
        
        # Puntos por entropía
        entropy_score = self._calculate_entropy_score(password)
        score += entropy_score
        
        return min(score, 100)  # Máximo 100 puntos
    
    def _has_repetitive_patterns(self, password):
        """Verificar si tiene patrones repetitivos"""
        # Verificar secuencias ascendentes/descendentes
        for i in range(len(password) - 2):
            if (ord(password[i+1]) == ord(password[i]) + 1 and 
                ord(password[i+2]) == ord(password[i]) + 2):
                return True
            if (ord(password[i+1]) == ord(password[i]) - 1 and 
                ord(password[i+2]) == ord(password[i]) - 2):
                return True
        
        return False
    
    def _calculate_entropy_score(self, password):
        """Calcular puntuación basada en entropía"""
        unique_chars = len(set(password))
        total_chars = len(password)
        
        if total_chars == 0:
            return 0
        
        entropy_ratio = unique_chars / total_chars
        return int(entropy_ratio * 15)  # Máximo 15 puntos por entropía
    
    def get_help_text(self):
        """Texto de ayuda"""
        return _(f'Su contraseña debe alcanzar una puntuación mínima de complejidad de {self.min_score} puntos. '
                f'Use una combinación de letras mayúsculas, minúsculas, números y símbolos.')

# ===========================================
# VALIDADOR COMBINADO PARA FELICITA
# ===========================================

class FelicitaPasswordValidator:
    """Validador combinado que aplica todas las reglas de FELICITA"""
    
    def __init__(self):
        self.validators = [
            CustomPasswordValidator(),
            CommonPasswordValidator(),
            ForbiddenWordsValidator(),
            AdvancedComplexityValidator(),
        ]
    
    def validate(self, password, user=None):
        """Aplicar todos los validadores"""
        for validator in self.validators:
            validator.validate(password, user)
    
    def get_help_text(self):
        """Obtener texto de ayuda combinado"""
        help_texts = []
        for validator in self.validators:
            help_texts.append(validator.get_help_text())
        return ' '.join(help_texts)

# ===========================================
# FUNCIONES AUXILIARES
# ===========================================

def generate_password_suggestions():
    """Generar sugerencias de contraseñas seguras"""
    import secrets
    import string
    
    suggestions = []
    
    for _ in range(3):
        # Generar contraseña de 12 caracteres
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*"
        
        password = (
            secrets.choice(uppercase) +
            secrets.choice(lowercase) +
            secrets.choice(digits) +
            secrets.choice(special) +
            ''.join(secrets.choice(lowercase + uppercase + digits + special) for _ in range(8))
        )
        
        # Mezclar caracteres
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        password = ''.join(password_list)
        
        suggestions.append(password)
    
    return suggestions

def validate_password_strength(password, user=None):
    """Función utilitaria para validar fortaleza de contraseña"""
    validator = FelicitaPasswordValidator()
    
    try:
        validator.validate(password, user)
        return {
            'is_valid': True,
            'score': AdvancedComplexityValidator()._calculate_password_score(password),
            'suggestions': []
        }
    except ValidationError as e:
        return {
            'is_valid': False,
            'score': AdvancedComplexityValidator()._calculate_password_score(password),
            'errors': e.messages,
            'suggestions': generate_password_suggestions()
        }