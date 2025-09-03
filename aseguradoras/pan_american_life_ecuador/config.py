#!/usr/bin/env python3
"""
Configuración específica para PAN AMERICAN LIFE DE ECUADOR

IMPORTANTE: Todas las configuraciones se obtienen del archivo .env principal del proyecto.
No hay valores hardcodeados en este archivo. Si una variable no está definida en .env,
el sistema fallará con un error claro indicando qué variable falta.

Variables requeridas:
- PALE_EC_LOGIN_URL: URL de login de la aseguradora
- PALE_EC_USERNAME: Usuario para el login
- PALE_EC_PASSWORD: Contraseña para el login
- PALE_EC_USERNAME_SELECTOR: Selector CSS del campo usuario
- PALE_EC_PASSWORD_SELECTOR: Selector CSS del campo contraseña
- PALE_EC_TIMEOUT_CARGA_PAGINA: Timeout para carga de página
- PALE_EC_SELENIUM_TIMEOUT_PAGINA: Timeout de Selenium para página

Ver archivo env.example para todas las variables disponibles.
"""

import os

# Información básica de la aseguradora
ASEGURADORA_INFO = {
    'nombre': 'PAN AMERICAN LIFE DE ECUADOR',
    'codigo': 'PALE_EC',
    'pais': 'Ecuador',
    'descripcion': 'Aseguradora Pan American Life en Ecuador',
    'activa': True
}

# URLs de la aseguradora
URLS = {
    'login': os.getenv('PALE_EC_LOGIN_URL'),
    'destino': os.getenv('PALE_EC_DESTINO_URL'),
    'base': os.getenv('PALE_EC_BASE_URL'),
    'portal': os.getenv('PALE_EC_PORTAL_URL')
}

# Campos de login (selectores HTML y valores)
CAMPOS_LOGIN = [
    {
        'selector': os.getenv('PALE_EC_USERNAME_SELECTOR'),
        'valor': os.getenv('PALE_EC_USERNAME'),
        'tipo': 'input',
        'descripcion': 'Campo de usuario/email',
        'requerido': True,
        'orden': 1
    },
    {
        'selector': os.getenv('PALE_EC_PASSWORD_SELECTOR'),
        'valor': os.getenv('PALE_EC_PASSWORD'),
        'tipo': 'input',
        'descripcion': 'Campo de contraseña',
        'requerido': True,
        'orden': 2
    }
]

# Acciones post-login
ACCIONES_POST_LOGIN = [
    {
        'tipo': 'click',
        'selector': os.getenv('PALE_EC_LOGIN_BUTTON_SELECTOR'),
        'descripcion': 'Botón de inicio de sesión',
        'espera_despues': int(os.getenv('PALE_EC_LOGIN_BUTTON_WAIT', '2')),
        'orden': 1
    }
]

# Configuración de Selenium específica para esta aseguradora
SELENIUM_CONFIG = {
    'timeout_pagina': int(os.getenv('PALE_EC_SELENIUM_TIMEOUT_PAGINA')),
    'timeout_elementos': int(os.getenv('PALE_EC_SELENIUM_TIMEOUT_ELEMENTOS')),
    'espera_post_login': int(os.getenv('PALE_EC_SELENIUM_ESPERA_POST_LOGIN')),
    'user_agent': os.getenv('PALE_EC_SELENIUM_USER_AGENT'),
    'window_size': os.getenv('PALE_EC_SELENIUM_WINDOW_SIZE'),
    'headless': os.getenv('PALE_EC_SELENIUM_HEADLESS', 'true').lower() == 'true',
    'opciones_especiales': os.getenv('PALE_EC_SELENIUM_OPCIONES_ESPECIALES', '').split(',') if os.getenv('PALE_EC_SELENIUM_OPCIONES_ESPECIALES') else []
}

# Configuración de esperas y timeouts
TIMEOUTS = {
    'carga_pagina': int(os.getenv('PALE_EC_TIMEOUT_CARGA_PAGINA')),
    'elemento_visible': int(os.getenv('PALE_EC_TIMEOUT_ELEMENTO_VISIBLE')),
    'elemento_clicable': int(os.getenv('PALE_EC_TIMEOUT_ELEMENTO_CLICABLE')),
    'procesamiento_login': int(os.getenv('PALE_EC_TIMEOUT_PROCESAMIENTO_LOGIN')),
    'navegacion': int(os.getenv('PALE_EC_TIMEOUT_NAVEGACION'))
}

# Validaciones post-login
VALIDACIONES = {
    'url_exito': os.getenv('PALE_EC_URL_EXITO'),
    'titulo_exito': os.getenv('PALE_EC_TITULO_EXITO'),
    'elementos_esperados': os.getenv('PALE_EC_ELEMENTOS_ESPERADOS', '').split(',') if os.getenv('PALE_EC_ELEMENTOS_ESPERADOS') else [],
    'elementos_no_esperados': os.getenv('PALE_EC_ELEMENTOS_NO_ESPERADOS', '').split(',') if os.getenv('PALE_EC_ELEMENTOS_NO_ESPERADOS') else []
}

# Manejo de errores específicos
MANEJO_ERRORES = {
    'errores_conocidos': os.getenv('PALE_EC_ERRORES_CONOCIDOS', '').split(',') if os.getenv('PALE_EC_ERRORES_CONOCIDOS') else [],
    'reintentos': int(os.getenv('PALE_EC_ERRORES_REINTENTOS', '3')),
    'espera_entre_reintentos': int(os.getenv('PALE_EC_ERRORES_ESPERA_ENTRE_REINTENTOS', '5')),
    'acciones_error': os.getenv('PALE_EC_ERRORES_ACCIONES', '').split(',') if os.getenv('PALE_EC_ERRORES_ACCIONES') else []
}

# Configuración de logging específica
LOGGING = {
    'nivel': os.getenv('PALE_EC_LOG_LEVEL'),
    'archivo': os.getenv('PALE_EC_LOG_ARCHIVO'),
    'formato': os.getenv('PALE_EC_LOG_FORMATO'),
    'rotacion': os.getenv('PALE_EC_LOG_ROTACION'),
    'max_size': os.getenv('PALE_EC_LOG_MAX_SIZE')
}

# Configuración de caché
CACHE = {
    'habilitado': os.getenv('PALE_EC_CACHE_HABILITADO', 'true').lower() == 'true',
    'tiempo_vida': int(os.getenv('PALE_EC_CACHE_TIEMPO_VIDA', '3600')),
    'max_elementos': int(os.getenv('PALE_EC_CACHE_MAX_ELEMENTOS', '100')),
    'limpiar_automatico': os.getenv('PALE_EC_CACHE_LIMPIAR_AUTOMATICO', 'true').lower() == 'true'
}

# Configuración de monitoreo
MONITOREO = {
    'habilitado': os.getenv('PALE_EC_MONITOREO_HABILITADO', 'true').lower() == 'true',
    'intervalo_verificacion': int(os.getenv('PALE_EC_MONITOREO_INTERVALO', '300')),
    'metricas': os.getenv('PALE_EC_MONITOREO_METRICAS', '').split(',') if os.getenv('PALE_EC_MONITOREO_METRICAS') else [],
    'alertas': {
        'tiempo_login_max': int(os.getenv('PALE_EC_MONITOREO_TIEMPO_MAX', '30')),
        'tasa_exito_min': float(os.getenv('PALE_EC_MONITOREO_TASA_EXITO_MIN', '0.95')),
        'errores_consecutivos_max': int(os.getenv('PALE_EC_MONITOREO_ERRORES_MAX', '5'))
    }
}

# Configuración de seguridad
SEGURIDAD = {
    'encriptar_credenciales': os.getenv('PALE_EC_SEGURIDAD_ENCRIPTAR', 'true').lower() == 'true',
    'log_credenciales': os.getenv('PALE_EC_SEGURIDAD_LOG_CREDENCIALES', 'false').lower() == 'true',
    'validar_ssl': os.getenv('PALE_EC_SEGURIDAD_VALIDAR_SSL', 'true').lower() == 'true',
    'timeout_conexion': int(os.getenv('PALE_EC_SEGURIDAD_TIMEOUT_CONEXION', '30')),
    'max_intentos_conexion': int(os.getenv('PALE_EC_SEGURIDAD_MAX_INTENTOS', '3'))
}

# Configuración de notificaciones
NOTIFICACIONES = {
    'habilitadas': os.getenv('PALE_EC_NOTIFICACIONES_HABILITADAS', 'true').lower() == 'true',
    'canales': os.getenv('PALE_EC_NOTIFICACIONES_CANALES', '').split(',') if os.getenv('PALE_EC_NOTIFICACIONES_CANALES') else [],
    'eventos': os.getenv('PALE_EC_NOTIFICACIONES_EVENTOS', '').split(',') if os.getenv('PALE_EC_NOTIFICACIONES_EVENTOS') else [],
    'destinatarios': os.getenv('PALE_EC_NOTIFICACIONES_DESTINATARIOS', '').split(',') if os.getenv('PALE_EC_NOTIFICACIONES_DESTINATARIOS') else []
}

# Configuración de backup y recuperación
BACKUP = {
    'habilitado': os.getenv('PALE_EC_BACKUP_HABILITADO', 'true').lower() == 'true',
    'frecuencia': os.getenv('PALE_EC_BACKUP_FRECUENCIA'),
    'retener_dias': int(os.getenv('PALE_EC_BACKUP_RETENER_DIAS', '30')),
    'comprimir': os.getenv('PALE_EC_BACKUP_COMPRIMIR', 'true').lower() == 'true',
    'ubicacion': os.getenv('PALE_EC_BACKUP_UBICACION')
}

# Configuración de reportes
REPORTES = {
    'habilitados': os.getenv('PALE_EC_REPORTES_HABILITADOS', 'true').lower() == 'true',
    'frecuencia': os.getenv('PALE_EC_REPORTES_FRECUENCIA'),
    'formato': os.getenv('PALE_EC_REPORTES_FORMATO'),
    'incluir_logs': os.getenv('PALE_EC_REPORTES_INCLUIR_LOGS', 'true').lower() == 'true',
    'incluir_metricas': os.getenv('PALE_EC_REPORTES_INCLUIR_METRICAS', 'true').lower() == 'true',
    'enviar_automatico': os.getenv('PALE_EC_REPORTES_ENVIAR_AUTOMATICO', 'true').lower() == 'true'
}

# Función para obtener configuración completa
def get_config_completa():
    """Retorna la configuración completa de la aseguradora"""
    return {
        'info': ASEGURADORA_INFO,
        'urls': URLS,
        'campos_login': CAMPOS_LOGIN,
        'acciones_post_login': ACCIONES_POST_LOGIN,
        'selenium': SELENIUM_CONFIG,
        'timeouts': TIMEOUTS,
        'validaciones': VALIDACIONES,
        'manejo_errores': MANEJO_ERRORES,
        'logging': LOGGING,
        'cache': CACHE,
        'monitoreo': MONITOREO,
        'seguridad': SEGURIDAD,
        'notificaciones': NOTIFICACIONES,
        'backup': BACKUP,
        'reportes': REPORTES
    }

# Función para validar configuración
def validar_configuracion():
    """Valida que la configuración esté completa y correcta"""
    errores = []
    
    # Validar campos requeridos
    if not ASEGURADORA_INFO.get('nombre'):
        errores.append("Nombre de aseguradora no definido")
    
    # Validar URLs requeridas
    if not URLS.get('login'):
        errores.append("Variable PALE_EC_LOGIN_URL no definida en .env")
    if not URLS.get('destino'):
        errores.append("Variable PALE_EC_DESTINO_URL no definida en .env")
    
    # Validar campos de login
    if not CAMPOS_LOGIN:
        errores.append("No hay campos de login definidos")
    
    for campo in CAMPOS_LOGIN:
        if not campo.get('selector'):
            errores.append(f"Variable PALE_EC_USERNAME_SELECTOR o PALE_EC_PASSWORD_SELECTOR no definida en .env")
        if not campo.get('valor') and campo.get('requerido'):
            errores.append(f"Variable PALE_EC_USERNAME o PALE_EC_PASSWORD no definida en .env")
    
    # Validar timeouts
    if not TIMEOUTS.get('carga_pagina'):
        errores.append("Variable PALE_EC_TIMEOUT_CARGA_PAGINA no definida en .env")
    if not TIMEOUTS.get('elemento_visible'):
        errores.append("Variable PALE_EC_TIMEOUT_ELEMENTO_VISIBLE no definida en .env")
    
    # Validar configuración de Selenium
    if not SELENIUM_CONFIG.get('timeout_pagina'):
        errores.append("Variable PALE_EC_SELENIUM_TIMEOUT_PAGINA no definida en .env")
    
    return errores

# Función para obtener configuración de login
def get_config_login():
    """Retorna la configuración específica para el login"""
    return {
        'url': URLS['login'],
        'campos': sorted(CAMPOS_LOGIN, key=lambda x: x.get('orden', 0)),
        'acciones': sorted(ACCIONES_POST_LOGIN, key=lambda x: x.get('orden', 0)),
        'timeouts': TIMEOUTS,
        'validaciones': VALIDACIONES
    }

# Función para obtener configuración de Selenium
def get_config_selenium():
    """Retorna la configuración específica de Selenium"""
    return SELENIUM_CONFIG

if __name__ == "__main__":
    # Validar configuración al ejecutar directamente
    errores = validar_configuracion()
    if errores:
        print("❌ Errores en la configuración:")
        for error in errores:
            print(f"   • {error}")
    else:
        print("✅ Configuración válida")
        print(f"📋 Aseguradora: {ASEGURADORA_INFO['nombre']}")
        print(f"🌐 URL Login: {URLS['login'][:50]}...")
        print(f"🔐 Campos de login: {len(CAMPOS_LOGIN)}")
        print(f"🎯 Acciones post-login: {len(ACCIONES_POST_LOGIN)}")
