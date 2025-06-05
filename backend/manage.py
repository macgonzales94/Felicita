#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.
FELICITA - Sistema de Facturación Electrónica para Perú
"""
import os
import sys


def main():
    """Run administrative tasks."""
    # Configurar el settings module por defecto
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'felicita.settings.local')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Estás seguro de que está instalado y "
            "disponible en tu variable de entorno PYTHONPATH? ¿Olvidaste "
            "activar un entorno virtual?"
        ) from exc
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()