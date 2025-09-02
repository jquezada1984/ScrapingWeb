# PAN AMERICAN LIFE DE ECUADOR - Procesador de Login Automático

## 📋 Información General

- **Nombre**: PAN AMERICAN LIFE DE ECUADOR
- **Código**: PALE_EC
- **País**: Ecuador
- **Versión**: 1.0.0
- **Estado**: Activa

## 🚀 Funcionalidades

### ✅ Implementadas
- **Login automático** con credenciales configuradas
- **Validación de elementos** de la página
- **Manejo de errores** y reintentos
- **Métricas y reportes** del proceso
- **Configuración flexible** y parametrizable

### 🔄 Proceso de Login

1. **Navegación**: Accede a la URL de login configurada
2. **Campos de Login**: Completa automáticamente usuario y contraseña
3. **Acciones Post-Login**: Ejecuta clicks o submits necesarios
4. **Validación**: Verifica que el login sea exitoso
5. **Reporte**: Genera métricas y reportes del proceso

## ⚙️ Configuración

### Variables de Entorno
Todas las configuraciones se pueden personalizar a través de variables de entorno. El sistema busca estas variables en el archivo `.env` principal del proyecto.

### URLs
- **Login**: `PALE_EC_LOGIN_URL` (por defecto: `https://attest.palig.com/as/authorization.oauth2?...`)
- **Destino**: `PALE_EC_DESTINO_URL` (por defecto: `https://paligdirect.com/PortalWeb/callback`)
- **Base**: `PALE_EC_BASE_URL` (por defecto: `https://attest.palig.com`)
- **Portal**: `PALE_EC_PORTAL_URL` (por defecto: `https://paligdirect.com`)

### Campos de Login
| Selector | Valor | Tipo | Descripción | Orden | Variable ENV |
|----------|-------|------|-------------|-------|--------------|
| `#username` | `conveniosyseguros@mediglobal.com.ec` | input | Usuario/Email | 1 | `PALE_EC_USERNAME` |
| `#password` | `Mediglobal1` | input | Contraseña | 2 | `PALE_EC_PASSWORD` |

**Selectores personalizables:**
- `PALE_EC_USERNAME_SELECTOR`: Selector del campo usuario
- `PALE_EC_PASSWORD_SELECTOR`: Selector del campo contraseña

### Acciones Post-Login
| Tipo | Selector | Descripción | Espera | Variable ENV |
|------|----------|-------------|---------|--------------|
| `click` | `a[title="Inicio de sesión"]` | Botón de inicio de sesión | 2s | `PALE_EC_LOGIN_BUTTON_SELECTOR` |

**Configuración personalizable:**
- `PALE_EC_LOGIN_BUTTON_SELECTOR`: Selector del botón de login
- `PALE_EC_LOGIN_BUTTON_WAIT`: Tiempo de espera después del click (en segundos)

### Timeouts
- **Carga de página**: `PALE_EC_TIMEOUT_CARGA_PAGINA` (por defecto: 30 segundos)
- **Elementos visibles**: `PALE_EC_TIMEOUT_ELEMENTO_VISIBLE` (por defecto: 10 segundos)
- **Elementos clicables**: `PALE_EC_TIMEOUT_ELEMENTO_CLICABLE` (por defecto: 10 segundos)
- **Procesamiento login**: `PALE_EC_TIMEOUT_PROCESAMIENTO_LOGIN` (por defecto: 3 segundos)
- **Navegación**: `PALE_EC_TIMEOUT_NAVEGACION` (por defecto: 5 segundos)

## 🔧 Uso

### Importación Básica
```python
from aseguradoras.pan_american_life_ecuador import crear_procesador

# Crear procesador
procesador = crear_procesador()

# Procesar login
resultado = procesador.procesar_login_especifico(driver)
```

### Configuración Completa
```python
from aseguradoras.pan_american_life_ecuador import get_config_completa

# Obtener toda la configuración
config = get_config_completa()

# Acceder a secciones específicas
urls = config['urls']
campos = config['campos_login']
acciones = config['acciones_post_login']
```

### Validación
```python
from aseguradoras.pan_american_life_ecuador import validar_configuracion

# Validar configuración
errores = validar_configuracion()
if not errores:
    print("✅ Configuración válida")
else:
    print(f"❌ Errores: {errores}")
```

## 📊 Monitoreo y Métricas

### Métricas Disponibles
- Tiempo total de login
- Tiempo de inicio y fin
- Estado del proceso
- Configuración utilizada

### Alertas Configuradas
- **Tiempo máximo de login**: 30 segundos
- **Tasa mínima de éxito**: 95%
- **Errores consecutivos máximos**: 5

### Reportes
- **Formato**: PDF
- **Frecuencia**: Diaria
- **Incluye**: Logs, métricas y configuración
- **Envío**: Automático

## 🛡️ Seguridad

### Características
- ✅ Credenciales encriptadas
- ✅ Logs sin información sensible
- ✅ Validación SSL
- ✅ Timeouts de conexión
- ✅ Reintentos limitados

### Configuración de Seguridad
```python
SEGURIDAD = {
    'encriptar_credenciales': True,
    'log_credenciales': False,
    'validar_ssl': True,
    'timeout_conexion': 30,
    'max_intentos_conexion': 3
}
```

## 🔄 Manejo de Errores

### Errores Conocidos
- Usuario o contraseña incorrectos
- Sesión expirada
- Mantenimiento del sistema
- Servicio no disponible

### Acciones de Recuperación
- Limpiar campos
- Recargar página
- Verificar conectividad
- Reintentos automáticos

### Configuración de Reintentos
```python
MANEJO_ERRORES = {
    'reintentos': 3,
    'espera_entre_reintentos': 5,
    'acciones_error': [
        'limpiar_campos',
        'recargar_pagina',
        'verificar_conectividad'
    ]
}
```

## 📁 Estructura de Archivos

```
pan_american_life_ecuador/
├── __init__.py              # Paquete principal
├── config.py                # Configuración específica
├── implementacion.py        # Lógica de implementación
└── README.md                # Este archivo
```

## 🧪 Pruebas

### Prueba del Paquete
```bash
cd aseguradoras/pan_american_life_ecuador
python __init__.py
```

### Prueba de Configuración
```bash
python config.py
```

### Prueba de Implementación
```bash
python implementacion.py
```

## 📝 Logs

### Archivo de Log
- **Nombre**: `pan_american_life_ecuador.log`
- **Formato**: `%(asctime)s - %(levelname)s - [PALE_EC] - %(message)s`
- **Rotación**: Diaria
- **Tamaño máximo**: 10MB

### Niveles de Log
- **INFO**: Proceso normal
- **WARNING**: Advertencias
- **ERROR**: Errores del sistema
- **DEBUG**: Información detallada

## 🔗 Integración

### Con el Worker Principal
Este procesador se integra con el worker principal a través del sistema de aseguradoras:

```python
from aseguradoras import crear_procesador

# Crear procesador para esta aseguradora
procesador = crear_procesador('pan_american_life_ecuador')

# Usar en el worker principal
if nombre_aseguradora == 'PAN AMERICAN LIFE DE ECUADOR':
    resultado = procesador.procesar_login_especifico(driver)
```

### Con la Base de Datos
- Lee configuración desde `urls_automatizacion`
- Obtiene campos desde `campos_login`
- Lee acciones desde `acciones_post_login`

## 🚀 Despliegue

### Variables de Entorno
Para personalizar la configuración, agrega estas variables a tu archivo `.env` principal:

```bash
# Ejemplo de variables personalizadas
PALE_EC_USERNAME=tu_usuario@ejemplo.com
PALE_EC_PASSWORD=tu_contraseña
PALE_EC_TIMEOUT_CARGA_PAGINA=45
PALE_EC_SELENIUM_HEADLESS=false
```

**Archivo de ejemplo completo**: `aseguradoras/pan_american_life_ecuador/env.example`

### Requisitos
- Python 3.8+
- Selenium WebDriver
- Chrome/Chromium
- Conexión a SQL Server
- Acceso a RabbitMQ

### Instalación
```bash
# El paquete se instala automáticamente al importar
from aseguradoras.pan_american_life_ecuador import crear_procesador
```

### Configuración del Entorno
```bash
# Variables de entorno (opcionales)
export PALE_EC_DEBUG=true
export PALE_EC_LOG_LEVEL=DEBUG
```

## 📞 Soporte

### Contacto
- **Admin**: admin@mediglobal.com.ec
- **Soporte**: soporte@mediglobal.com.ec

### Canales de Notificación
- Email
- Webhook

### Eventos Monitoreados
- Login exitoso
- Login fallido
- Error del sistema
- Mantenimiento

## 🔄 Actualizaciones

### Versión 1.0.0
- ✅ Implementación inicial
- ✅ Login automático funcional
- ✅ Validaciones básicas
- ✅ Manejo de errores
- ✅ Métricas y reportes

### Próximas Versiones
- 🔄 Soporte para múltiples navegadores
- 🔄 Validaciones avanzadas
- 🔄 Integración con sistemas externos
- 🔄 Dashboard de monitoreo

---

**Desarrollado por**: Sistema de Automatización  
**Última actualización**: Enero 2025  
**Estado**: Activo y Funcional ✅
