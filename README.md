# Proyecto de Scraping Web con SQL Server y RabbitMQ

Este proyecto implementa un sistema de scraping web distribuido que utiliza RabbitMQ para la gestión de tareas y SQL Server para el almacenamiento de datos.

## 📁 Estructura del Proyecto

```
scraping_web/
├── src/                          # Código fuente principal
│   ├── __init__.py
│   ├── config.py                 # Configuración y variables de entorno
│   ├── database.py               # Gestión de conexión a SQL Server externo
│   ├── rabbitmq_client.py        # Cliente para RabbitMQ externo
│   ├── scraper.py                # Motor de scraping web
│   └── scraping_worker.py        # Worker principal que coordina todo
├── run_production_worker.py      # Worker de producción principal (SIEMPRE ACTIVO)
├── requirements.txt              # Dependencias de Python
├── config.env.example            # Ejemplo de configuración local
├── docker.env.example            # Ejemplo de configuración Docker
├── docker-compose.yml            # Configuración Docker (solo app Python)
├── Dockerfile                    # Dockerfile para containerización
├── README.md                     # Documentación completa
└── .gitignore                    # Archivos a ignorar en Git
```

## 🚀 Características

- **Scraping Web**: Extracción de datos usando requests/BeautifulSoup y Selenium
- **Cola de Mensajes**: RabbitMQ para gestionar tareas de scraping de forma asíncrona
- **Base de Datos**: SQL Server para almacenar resultados del scraping
- **Escalabilidad**: Arquitectura distribuida que permite múltiples workers
- **Configuración Flexible**: Variables de entorno para personalizar el comportamiento
- **Logging Completo**: Registro detallado de todas las operaciones

## 📋 Requisitos Previos

### Software Necesario

1. **Python 3.8+**
2. **SQL Server** (servicio externo en otro proyecto)
3. **RabbitMQ Server** (servicio externo en otro proyecto)
4. **Microsoft Edge** (recomendado) o **Chrome/Chromium** (para Selenium)

### Servicios Externos Requeridos

- **SQL Server**: Debe estar ejecutándose en otro proyecto/contenedor
- **RabbitMQ**: Debe estar ejecutándose en otro proyecto/contenedor con usuario `admin` y contraseña `admin123`

### Drivers de SQL Server

Para Windows, instala el driver ODBC:
- [Microsoft ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### Autenticación de Windows

El proyecto está configurado para usar **autenticación de Windows** (Trusted Connection) con SQL Server:
- **Instancia**: `localhost\MSSQLSERVER01`
- **Autenticación**: Windows (sin usuario/contraseña)
- **Permisos**: El usuario de Windows debe tener acceso a la base de datos

## 🛠️ Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <tu-repositorio>
   cd scraping_web
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   # Copiar archivo de ejemplo
   copy config.env.example .env
   
   # Editar .env con tus configuraciones
   ```

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# Configuración de SQL Server (servicio externo)
SQL_SERVER_HOST=localhost\MSSQLSERVER01
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=scraping_db
SQL_SERVER_USERNAME=
SQL_SERVER_PASSWORD=
SQL_SERVER_TRUSTED_CONNECTION=yes

# Configuración de RabbitMQ (servicio externo)
RABBITMQ_HOST=rabbitmq_externo
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=admin123
RABBITMQ_QUEUE=scraping_tasks
RABBITMQ_EXCHANGE=aseguradora_exchange

# Configuración de la aplicación
LOG_LEVEL=INFO
SCRAPING_DELAY=2
MAX_RETRIES=3
```

### Servicios Externos

1. **SQL Server**: Debe estar ejecutándose en `localhost\MSSQLSERVER01`
   - **Autenticación**: Windows (Trusted Connection)
   - **Base de datos**: Crear `scraping_db`
   ```sql
   CREATE DATABASE scraping_db;
   ```

2. **RabbitMQ**: Debe estar ejecutándose en otro proyecto con:
   - Usuario: `admin`
   - Contraseña: `admin123`

3. **La tabla se creará automáticamente** cuando ejecutes el worker por primera vez.

## 🚀 Uso

### Guía de Ejecución Paso a Paso

#### Paso 1: Preparación del Entorno
```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy config.env.example .env
# Editar .env con tus credenciales
```

#### Paso 2: Verificar Conexiones
```bash
# Probar que SQL Server y RabbitMQ estén funcionando
python test_connection.py
```

#### Paso 3: Iniciar el Worker
```bash
# En una terminal, ejecutar el worker
python main.py
```

El worker se conectará a RabbitMQ y SQL Server, y comenzará a procesar tareas de scraping.

#### Paso 4: Publicar Tareas de Scraping

#### Tarea Única
```bash
python publisher.py --url "https://ejemplo.com" --selenium
```

#### Múltiples URLs desde archivo
```bash
# Crear archivo urls.txt con URLs (una por línea)
echo "https://ejemplo1.com" > urls.txt
echo "https://ejemplo2.com" >> urls.txt

# Publicar tareas
python publisher.py --file urls.txt --selenium
```

#### Con Selectores CSS Personalizados
```bash
# Crear archivo selectors.json
{
    "titulo": "h1.title",
    "contenido": "div.content",
    "fecha": "span.date"
}

# Publicar con selectores
python publisher.py --url "https://ejemplo.com" --selectors selectors.json
```

### 🎯 Ejecución en Producción
```bash
# Ejecutar worker de producción (SIEMPRE ACTIVO)
python run_production_worker.py
```

### 🔄 Flujo de Trabajo del Sistema

1. **Recepción**: El worker recibe mensajes de aseguradoras desde RabbitMQ
2. **Procesamiento**: Extrae el `NombreCompleto` del mensaje
3. **Búsqueda**: Consulta la tabla `urls_automatizacion` en SQL Server
4. **Caché**: Almacena URLs en memoria para futuras consultas
5. **Resultado**: Combina información del mensaje con la URL encontrada

### 📋 Comandos de Ejemplo

```bash
# Iniciar worker de producción (SIEMPRE ACTIVO)
python run_production_worker.py

# El worker estará siempre esperando mensajes
# Presiona Ctrl+C para detenerlo de forma graceful
```

## 📊 Estructura de la Base de Datos

### Tabla: urls_automatizacion

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UNIQUEIDENTIFIER | ID único de la aseguradora |
| nombre | NVARCHAR(255) | Nombre completo de la aseguradora |
| url_login | TEXT | URL de login de la aseguradora |
| url_destino | TEXT | URL de destino (opcional) |
| descripcion | NTEXT | Descripción de la aseguradora |
| fecha_creacion | DATETIME | Fecha de creación del registro |

### Formato de Mensajes RabbitMQ

Los mensajes deben contener el campo `NombreCompleto` que se usará para buscar en la tabla:

```json
{
    "NombreCompleto": "PAN AMERICAN LIFE DE ECUADOR",
    "IdFactura": "FACT001",
    "IdAseguradora": 14,
    "NumDocIdentidad": "1234567890",
    "PersonaPrimerNombre": "JUAN",
    "PersonaPrimerApellido": "PEREZ",
    "FechaProcesamiento": "2025-01-09T15:00:00Z"
}
```

## 📁 Características del Worker

### 🚀 Modo SIEMPRE ACTIVO
- El worker está configurado para estar **siempre esperando** mensajes
- No se cierra cuando la cola está vacía
- Procesa mensajes de forma continua y asíncrona

### 💾 Sistema de Caché
- Almacena URLs de aseguradoras en memoria
- Evita consultas repetidas a la base de datos
- Mejora significativamente el rendimiento

### 🔄 Procesamiento Robusto
- Manejo de errores sin interrumpir el worker
- Acknowledgment manual de mensajes
- Reconexión automática en caso de fallos

### 📊 Logging Detallado
- Logs en consola y archivo (`production_worker.log`)
- Estadísticas del caché al iniciar y detener
- Información detallada de cada mensaje procesado

## 🔧 Configuración Avanzada

### Variables de Entorno

El worker lee la configuración desde el archivo `.env`:

```bash
# SQL Server
SQL_SERVER_HOST=localhost\MSSQLSERVER01
SQL_SERVER_DATABASE=NeptunoMedicalAutomatico
SQL_SERVER_TRUSTED_CONNECTION=yes

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=admin123
RABBITMQ_QUEUE=aseguradora_queue
RABBITMQ_EXCHANGE=aseguradora_exchange
RABBITMQ_ROUTING_KEY=aseguradora

# Aplicación
LOG_LEVEL=INFO
SCRAPING_DELAY=1
MAX_RETRIES=3
```

### Selenium vs Requests

- **Requests/BeautifulSoup**: Más rápido, ideal para páginas estáticas
- **Selenium**: Necesario para páginas con JavaScript dinámico

## 📝 Logs

Los logs se guardan en:
- **Consola**: Salida en tiempo real
- **Archivo**: `scraping_worker.log`

## 🐛 Solución de Problemas

### Error de Conexión a SQL Server
- Verificar que SQL Server esté ejecutándose en `localhost\MSSQLSERVER01`
- Comprobar que la autenticación de Windows esté habilitada
- Asegurar que el usuario de Windows tenga permisos en la base de datos
- Verificar que el driver ODBC esté instalado
- Para Docker: usar `host.docker.internal\MSSQLSERVER01`

### Error de Conexión a RabbitMQ
- Verificar que RabbitMQ esté ejecutándose
- Comprobar credenciales en `.env`
- Verificar que el puerto 5672 esté abierto

### Error de Selenium
- Instalar Chrome/Chromium
- Verificar que el ChromeDriver esté en el PATH
- Para headless, asegurar que no haya problemas de permisos

## 🐳 Uso con Docker

### Ejecutar Solo la Aplicación Python
```bash
# Construir y ejecutar la aplicación
docker-compose up -d

# Ver logs de la aplicación
docker-compose logs -f scraping_app

# Detener la aplicación
docker-compose down
```

### Configuración para Servicios Externos
La aplicación se conecta a servicios externos (SQL Server y RabbitMQ) que deben estar ejecutándose en otros proyectos. Asegúrate de que:

1. **SQL Server** esté ejecutándose y accesible
2. **RabbitMQ** esté ejecutándose con usuario `admin` y contraseña `admin123`
3. Los hosts en el archivo `.env` apunten a los servicios correctos

### Variables de Entorno para Docker
```bash
# Crear archivo .env con las configuraciones de tus servicios externos
cp docker.env.example .env

# Editar .env con tus configuraciones:
SQL_SERVER_HOST=host.docker.internal\MSSQLSERVER01
SQL_SERVER_TRUSTED_CONNECTION=yes
RABBITMQ_HOST=tu_rabbitmq_host
```

**Nota**: Para Docker, usa `host.docker.internal\MSSQLSERVER01` para conectar al SQL Server del host con autenticación de Windows.

### Conectar a Red Externa
Si tus servicios externos están en otra red Docker, puedes conectar la aplicación:

```yaml
# En docker-compose.yml, descomenta y configura:
networks:
  - external_network

# Luego ejecutar:
docker network connect external_network scraping_app
```

## 🔄 Escalabilidad

Para ejecutar múltiples workers:

1. **Ejecutar múltiples instancias** del worker en diferentes terminales
2. **Usar Docker** para containerizar la aplicación
3. **Implementar balanceo de carga** con múltiples servidores

## 📈 Monitoreo

### Estado de la Cola
```python
from src.scraping_worker import ScrapingWorker

worker = ScrapingWorker()
worker.initialize()
status = worker.get_queue_status()
print(f"Mensajes en cola: {status['message_count']}")
```

### Consultas SQL Útiles

```sql
-- Últimos resultados
SELECT TOP 10 * FROM scraping_results ORDER BY timestamp DESC;

-- Estadísticas por día
SELECT 
    CAST(timestamp AS DATE) as fecha,
    COUNT(*) as total,
    AVG(processing_time) as tiempo_promedio
FROM scraping_results 
GROUP BY CAST(timestamp AS DATE)
ORDER BY fecha DESC;

-- URLs con errores
SELECT url, error_message, timestamp 
FROM scraping_results 
WHERE error_message IS NOT NULL;
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisar los logs en `scraping_worker.log`
2. Verificar la configuración en `.env`
3. Comprobar que todos los servicios estén ejecutándose
4. Abrir un issue en el repositorio

## 📋 Resumen de Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `python test_connection.py` | Probar conexiones a SQL Server y RabbitMQ |
| `python main.py` | Iniciar el worker de scraping |
| `python publisher.py --url "URL"` | Publicar tarea única |
| `python publisher.py --file archivo.txt` | Publicar múltiples URLs |
| `python quick_start.py` | Prueba rápida completa del sistema |
| `docker-compose up -d` | Iniciar todo con Docker |

## 🎯 Casos de Uso Típicos

### Escenario 1: Prueba Inicial
```bash
# 1. Asegurar que SQL Server y RabbitMQ estén ejecutándose en otros proyectos
# 2. Configurar .env con las credenciales correctas
# 3. Probar conexiones
python test_connection.py

# 4. Ejecutar prueba rápida
python quick_start.py
```

### Escenario 2: Scraping de Sitio Web
```bash
# 1. Iniciar worker
python main.py

# 2. Publicar tarea con selectores
python publisher.py --url "https://ejemplo.com" --selectors selectors.json
```

### Escenario 3: Procesamiento Masivo
```bash
# 1. Crear archivo con URLs
echo "https://sitio1.com" > urls.txt
echo "https://sitio2.com" >> urls.txt

# 2. Iniciar worker
python main.py

# 3. Publicar tareas masivas
python publisher.py --file urls.txt --selenium
```

### Escenario 4: Ejecución con Docker
```bash
# 1. Configurar .env con servicios externos
# 2. Ejecutar con Docker
docker-compose up -d

# 3. Ver logs
docker-compose logs -f scraping_app
```

## 🔄 Cambios Implementados

### 1. Migración de Chrome a Microsoft Edge
- **Cambio de navegador**: Migrado de Google Chrome a Microsoft Edge para mejor estabilidad en Windows
- **Selenium actualizado**: Actualizado de Selenium 3.141.0 a Selenium 4.35.0 para compatibilidad con Edge
- **Mejor rendimiento**: Edge suele ser más estable y compatible con Selenium en entornos Windows
- **Configuración optimizada**: Opciones específicas de Edge para reducir logs y mejorar rendimiento

### 2. Aumento de Tiempos de Espera OAuth2
- **Primera redirección**: Aumentada de 60 segundos (20 intentos × 3s) a **120 segundos (40 intentos × 3s)**
- **Segunda redirección**: Aumentada de 30 segundos (10 intentos × 3s) a **60 segundos (20 intentos × 3s)**

### 2. Detección y Manejo de Página `authorization.ping`
- **Detección automática**: El sistema ahora detecta cuando se queda en la página intermedia `authorization.ping`
- **Búsqueda activa de elementos**: Busca botones, enlaces y elementos clickeables para continuar el flujo OAuth2
- **Múltiples selectores**: Busca en `button`, `input[type="submit"]`, `a`, `[role="button"]`, `.btn`, `.button`
- **Logging detallado**: Registra todos los elementos encontrados y los intentos de clic

### 3. Navegación Manual como Fallback
- **Redirección automática**: Si el flujo OAuth2 no llega a `benefitsdirect.palig.com`, se intenta navegación manual
- **URL objetivo**: `https://benefitsdirect.palig.com/Inicio/Contenido/InfoAsegurado/MisPolizasPVR.aspx`
- **Verificación**: Se confirma que la navegación manual fue exitosa

### 4. Mejoras en Navegación a Página de Búsqueda
- **Verificación de estado**: Después del login, se verifica si ya estamos en la página correcta
- **Navegación directa**: Si no estamos en la página correcta, se intenta navegación directa
- **Reintentos**: Si falla, se reintenta la navegación
- **Verificación de carga**: Se espera explícitamente a que `document.readyState == "complete"`

### 5. Manejo de Redirección a Página Principal
- **Detección**: Se detecta cuando el sistema aterriza en la página principal en lugar de la de búsqueda
- **Múltiples estrategias de redirección**:
  - **Estrategia 1**: Navegación directa a la URL objetivo
  - **Estrategia 2**: Búsqueda y clic en enlaces relevantes en la página principal
  - **Estrategia 3**: Navegación a URLs alternativas como último recurso
- **Logging detallado**: Se registra cada estrategia y su resultado
- **Fallback inteligente**: Si una estrategia falla, se intenta la siguiente

### 6. Sistema de Logging Detallado de URLs 🆕
- **Rastreo de cambios de URL**: Se detecta y registra cada cambio de URL durante el flujo OAuth2
- **Logs antes y después**: Se registra la URL antes y después de cada navegación
- **Detección de estados intermedios**: Se identifica claramente cuando se está en `authorization.ping`
- **Seguimiento de estrategias**: Cada estrategia de navegación registra su URL objetivo y resultado
- **Verificación de resultados**: Se confirma la URL final después de cada operación
- **Logs estructurados**: Formato consistente con emojis y jerarquía visual para fácil lectura

## 🧪 Scripts de Prueba

### `test_oauth2_flow.py`
Script independiente para probar solo el flujo OAuth2 mejorado:
```bash
python test_oauth2_flow.py
```

### `test_complete_flow.py`
Script independiente para probar el flujo completo incluyendo navegación post-login:
```bash
python test_complete_flow.py
```

### `test_url_logging.py` 🆕
Script independiente para verificar el sistema de logging de URLs:
```bash
python test_url_logging.py
```

## 📝 Notas de Implementación

### Logging de URLs
El sistema ahora registra detalladamente:
- **URL inicial** antes de cada operación
- **URL después** de cada operación
- **Cambios detectados** durante el flujo OAuth2
- **Resultado de cada estrategia** de navegación
- **URLs finales** después de cada proceso

### Formato de Logs
Los logs utilizan un formato estructurado con:
- Emojis para identificación visual rápida
- Jerarquía clara con indentación
- Información de URL antes y después
- Estados y transiciones claramente marcados

### Beneficios del Nuevo Sistema
1. **Trazabilidad completa**: Se puede seguir exactamente el flujo de navegación
2. **Debugging mejorado**: Identificación rápida de dónde se queda el proceso
3. **Control de flujo**: Visibilidad total de las redirecciones OAuth2
4. **Análisis de fallos**: Fácil identificación de qué estrategia falló
5. **Monitoreo en tiempo real**: Seguimiento del progreso durante la ejecución