#!/usr/bin/env python3
"""
Paquete para PAN AMERICAN LIFE DE ECUADOR
"""

from .config import (
    ASEGURADORA_INFO,
    URLS,
    CAMPOS_LOGIN,
    ACCIONES_POST_LOGIN,
    get_config_completa,
    get_config_login,
    get_config_selenium,
    validar_configuracion
)

from .implementacion import (
    PanAmericanLifeEcuadorProcessor,
    crear_procesador,
    get_info_aseguradora
)

__version__ = "1.0.0"
__author__ = "Sistema de Automatización"
__description__ = "Procesador específico para PAN AMERICAN LIFE DE ECUADOR"

# Exportar funciones principales
__all__ = [
    # Configuración
    'ASEGURADORA_INFO',
    'URLS', 
    'CAMPOS_LOGIN',
    'ACCIONES_POST_LOGIN',
    'get_config_completa',
    'get_config_login',
    'get_config_selenium',
    'validar_configuracion',
    
    # Implementación
    'PanAmericanLifeEcuadorProcessor',
    'crear_procesador',
    'get_info_aseguradora'
]

# Información del paquete
PACKAGE_INFO = {
    'nombre': 'pan_american_life_ecuador',
    'version': __version__,
    'aseguradora': 'PAN AMERICAN LIFE DE ECUADOR',
    'codigo': 'PALE_EC',
    'pais': 'Ecuador',
    'descripcion': 'Procesador específico para automatización de login en PAN AMERICAN LIFE DE ECUADOR',
    'funcionalidades': [
        'Login automático',
        'Validación de elementos',
        'Manejo de errores',
        'Métricas y reportes',
        'Configuración flexible'
    ]
}

def get_package_info():
    """Retorna información del paquete"""
    return PACKAGE_INFO

def get_aseguradora_info():
    """Retorna información de la aseguradora"""
    return ASEGURADORA_INFO

def test_package():
    """Prueba básica del paquete"""
    try:
        # Probar configuración
        config = get_config_completa()
        print("✅ Configuración cargada correctamente")
        
        # Probar validación
        errores = validar_configuracion()
        if not errores:
            print("✅ Configuración válida")
        else:
            print(f"❌ Errores en configuración: {errores}")
        
        # Probar creación de procesador
        procesador = crear_procesador()
        print("✅ Procesador creado correctamente")
        
        # Mostrar información
        info = get_aseguradora_info()
        print(f"📋 Aseguradora: {info['nombre']}")
        print(f"🌐 URL Login: {config['urls']['login'][:50]}...")
        print(f"🔐 Campos de login: {len(config['campos_login'])}")
        print(f"🎯 Acciones post-login: {len(config['acciones_post_login'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando paquete: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Probando paquete PAN AMERICAN LIFE DE ECUADOR...")
    test_package()
