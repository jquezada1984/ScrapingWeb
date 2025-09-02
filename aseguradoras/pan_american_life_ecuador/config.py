#!/usr/bin/env python3
"""
Configuración específica para PAN AMERICAN LIFE DE ECUADOR
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
    'login': os.getenv('PALE_EC_LOGIN_URL', 'https://attest.palig.com/as/authorization.oauth2?client_id=cf7770f3699048ca9c61358b4dff25f5&redirect_uri=https%3A%2F%2Fbenefitsdirect.palig.com%2FInicio%2FLogin.aspx&response_type=code%20id_token&scope=openid%20profile%20email%20phone&state=OpenIdConnect.AuthenticationProperties%3DTBYyPWZT_d1ZE_uAG3CKh3HsoxTt77sdU39y8JDs7IOuNQ90L-8LKm0LywIZTuOPxnSIZ3tQ280RiX9A7UhlbevOoIWavNKgzA4ZMdbeXsll9vvQYwGEZ-wsT_V6XBo_n6rvja_bvMdoSTLq9qZNpRunGJp5OAURWnVJ64vS_7M3A6nDhPnwa-f97XD50MvEduGmNxJU4c4GTKZX7baDKXCit8orDw2iJfjFaaiXmgssMdAaTYs8Dj3c7Jvm7KshZhcC9nXdk9KnB2i0t&response_mode=form_post&nonce=638919538746530905.MzI3NGIzOTItZTA3OS00YmUwLThkZTQtNDg2N2NiOGU1NzMyMDNjMmZlNTMtN2E3Yy00ZjM2LTg0YWEtM2YwMDUyMjY4MTM0&x-client-SKU=ID_NET451&x-client-ver=5.6.0.0'),
    'destino': os.getenv('PALE_EC_DESTINO_URL', 'https://paligdirect.com/PortalWeb/callback'),
    'base': os.getenv('PALE_EC_BASE_URL', 'https://attest.palig.com'),
    'portal': os.getenv('PALE_EC_PORTAL_URL', 'https://paligdirect.com')
}

# Campos de login (selectores HTML y valores)
CAMPOS_LOGIN = [
    {
        'selector': os.getenv('PALE_EC_USERNAME_SELECTOR', '#username'),
        'valor': os.getenv('PALE_EC_USERNAME', 'conveniosyseguros@mediglobal.com.ec'),
        'tipo': 'input',
        'descripcion': 'Campo de usuario/email',
        'requerido': True,
        'orden': 1
    },
    {
        'selector': os.getenv('PALE_EC_PASSWORD_SELECTOR', '#password'),
        'valor': os.getenv('PALE_EC_PASSWORD', 'Mediglobal1'),
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
        'selector': os.getenv('PALE_EC_LOGIN_BUTTON_SELECTOR', 'a[title="Inicio de sesión"]'),
        'descripcion': 'Botón de inicio de sesión',
        'espera_despues': int(os.getenv('PALE_EC_LOGIN_BUTTON_WAIT', '2')),
        'orden': 1
    }
]

# Configuración de Selenium específica para esta aseguradora
SELENIUM_CONFIG = {
    'timeout_pagina': int(os.getenv('PALE_EC_SELENIUM_TIMEOUT_PAGINA', '30')),
    'timeout_elementos': int(os.getenv('PALE_EC_SELENIUM_TIMEOUT_ELEMENTOS', '10')),
    'espera_post_login': int(os.getenv('PALE_EC_SELENIUM_ESPERA_POST_LOGIN', '3')),
    'user_agent': os.getenv('PALE_EC_SELENIUM_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
    'window_size': os.getenv('PALE_EC_SELENIUM_WINDOW_SIZE', '1920,1080'),
    'headless': os.getenv('PALE_EC_SELENIUM_HEADLESS', 'true').lower() == 'true',
    'opciones_especiales': os.getenv('PALE_EC_SELENIUM_OPCIONES_ESPECIALES', '--no-sandbox,--disable-dev-shm-usage,--disable-gpu,--disable-web-security,--allow-running-insecure-content').split(',')
}

# Configuración de esperas y timeouts
TIMEOUTS = {
    'carga_pagina': int(os.getenv('PALE_EC_TIMEOUT_CARGA_PAGINA', '30')),
    'elemento_visible': int(os.getenv('PALE_EC_TIMEOUT_ELEMENTO_VISIBLE', '10')),
    'elemento_clicable': int(os.getenv('PALE_EC_TIMEOUT_ELEMENTO_CLICABLE', '10')),
    'procesamiento_login': int(os.getenv('PALE_EC_TIMEOUT_PROCESAMIENTO_LOGIN', '3')),
    'navegacion': int(os.getenv('PALE_EC_TIMEOUT_NAVEGACION', '5'))
}

# Validaciones post-login
VALIDACIONES = {
    'url_exito': os.getenv('PALE_EC_URL_EXITO', 'paligdirect.com'),
    'titulo_exito': os.getenv('PALE_EC_TITULO_EXITO', 'Pan-American Life Insurance Group'),
    'elementos_esperados': os.getenv('PALE_EC_ELEMENTOS_ESPERADOS', 'body,main,nav').split(','),
    'elementos_no_esperados': os.getenv('PALE_EC_ELEMENTOS_NO_ESPERADOS', 'error,invalid,failed').split(',')
}

# Manejo de errores específicos
MANEJO_ERRORES = {
    'errores_conocidos': os.getenv('PALE_EC_ERRORES_CONOCIDOS', 'Usuario o contraseña incorrectos,Sesión expirada,Mantenimiento del sistema,Servicio no disponible').split(','),
    'reintentos': int(os.getenv('PALE_EC_ERRORES_REINTENTOS', '3')),
    'espera_entre_reintentos': int(os.getenv('PALE_EC_ERRORES_ESPERA_ENTRE_REINTENTOS', '5')),
    'acciones_error': os.getenv('PALE_EC_ERRORES_ACCIONES', 'limpiar_campos,recargar_pagina,verificar_conectividad').split(',')
}

# Configuración de logging específica
LOGGING = {
    'nivel': os.getenv('PALE_EC_LOG_LEVEL', 'INFO'),
    'archivo': os.getenv('PALE_EC_LOG_ARCHIVO', 'pan_american_life_ecuador.log'),
    'formato': os.getenv('PALE_EC_LOG_FORMATO', '%(asctime)s - %(levelname)s - [PALE_EC] - %(message)s'),
    'rotacion': os.getenv('PALE_EC_LOG_ROTACION', 'daily'),
    'max_size': os.getenv('PALE_EC_LOG_MAX_SIZE', '10MB')
}

# Configuración de caché
CACHE = {
    'habilitado': os.getenv('PALE_EC_CACHE_HABILITADO', 'true').lower() == 'true',
    'tiempo_vida': int(os.getenv('PALE_EC_CACHE_TIEMPO_VIDA', '3600')),  # 1 hora en segundos
    'max_elementos': int(os.getenv('PALE_EC_CACHE_MAX_ELEMENTOS', '100')),
    'limpiar_automatico': os.getenv('PALE_EC_CACHE_LIMPIAR_AUTOMATICO', 'true').lower() == 'true'
}

# Configuración de monitoreo
MONITOREO = {
    'habilitado': os.getenv('PALE_EC_MONITOREO_HABILITADO', 'true').lower() == 'true',
    'intervalo_verificacion': int(os.getenv('PALE_EC_MONITOREO_INTERVALO', '300')),  # 5 minutos
    'metricas': os.getenv('PALE_EC_MONITOREO_METRICAS', 'tiempo_login,tasa_exito,errores_frecuentes,performance').split(','),
    'alertas': {
        'tiempo_login_max': int(os.getenv('PALE_EC_MONITOREO_TIEMPO_MAX', '30')),  # segundos
        'tasa_exito_min': float(os.getenv('PALE_EC_MONITOREO_TASA_EXITO_MIN', '0.95')),  # 95%
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
    'canales': os.getenv('PALE_EC_NOTIFICACIONES_CANALES', 'email,webhook').split(','),
    'eventos': os.getenv('PALE_EC_NOTIFICACIONES_EVENTOS', 'login_exitoso,login_fallido,error_sistema,mantenimiento').split(','),
    'destinatarios': os.getenv('PALE_EC_NOTIFICACIONES_DESTINATARIOS', 'admin@mediglobal.com.ec,soporte@mediglobal.com.ec').split(',')
}

# Configuración de backup y recuperación
BACKUP = {
    'habilitado': os.getenv('PALE_EC_BACKUP_HABILITADO', 'true').lower() == 'true',
    'frecuencia': os.getenv('PALE_EC_BACKUP_FRECUENCIA', 'daily'),
    'retener_dias': int(os.getenv('PALE_EC_BACKUP_RETENER_DIAS', '30')),
    'comprimir': os.getenv('PALE_EC_BACKUP_COMPRIMIR', 'true').lower() == 'true',
    'ubicacion': os.getenv('PALE_EC_BACKUP_UBICACION', './backups/pan_american_life_ecuador/')
}

# Configuración de reportes
REPORTES = {
    'habilitados': os.getenv('PALE_EC_REPORTES_HABILITADOS', 'true').lower() == 'true',
    'frecuencia': os.getenv('PALE_EC_REPORTES_FRECUENCIA', 'daily'),
    'formato': os.getenv('PALE_EC_REPORTES_FORMATO', 'PDF'),
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
    
    if not URLS.get('login'):
        errores.append("URL de login no definida")
    
    if not CAMPOS_LOGIN:
        errores.append("No hay campos de login definidos")
    
    # Validar campos de login
    for campo in CAMPOS_LOGIN:
        if not campo.get('selector'):
            errores.append(f"Selector no definido para campo: {campo.get('descripcion', 'Desconocido')}")
        if not campo.get('valor') and campo.get('requerido'):
            errores.append(f"Valor requerido no definido para campo: {campo.get('selector')}")
    
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
