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
├── examples/                     # Archivos de ejemplo
│   ├── __init__.py
│   ├── urls_example.txt          # URLs de prueba
│   └── selectors_example.json    # Selectores CSS de ejemplo
├── main.py                       # Script principal para ejecutar el worker
├── publisher.py                  # Script para publicar tareas
├── test_connection.py            # Script para probar conexiones
├── quick_start.py                # Script de inicio rápido
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
4. **Chrome/Chromium** (para Selenium)

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

### 🎯 Prueba Rápida Completa
```bash
# Ejecutar prueba completa del sistema
python quick_start.py
```

### 🔄 Flujo de Trabajo del Sistema

1. **Publicación**: Las tareas se publican en RabbitMQ usando `publisher.py`
2. **Procesamiento**: El worker (`main.py`) consume mensajes de la cola
3. **Scraping**: Se extraen datos de las URLs especificadas usando `scraper.py`
4. **Almacenamiento**: Los resultados se guardan en SQL Server usando `database.py`
5. **Confirmación**: Se confirma el procesamiento exitoso

### 📋 Comandos de Ejemplo

```bash
# Probar conexiones
python test_connection.py

# Iniciar worker
python main.py

# Publicar tarea única
python publisher.py --url "https://httpbin.org/html"

# Publicar múltiples URLs
python publisher.py --file examples/urls_example.txt

# Publicar con Selenium
python publisher.py --url "https://ejemplo.com" --selenium

# Publicar con selectores personalizados
python publisher.py --url "https://ejemplo.com" --selectors examples/selectors_example.json

# Prueba rápida completa
python quick_start.py
```

## 📊 Estructura de la Base de Datos

### Tabla: scraping_results

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT | ID único autoincremental |
| url | NVARCHAR(500) | URL procesada |
| title | NVARCHAR(500) | Título de la página |
| content | NVARCHAR(MAX) | Contenido extraído |
| status_code | INT | Código de respuesta HTTP |
| error_message | NVARCHAR(1000) | Mensaje de error (si aplica) |
| selenium_used | BIT | Si se usó Selenium |
| timestamp | DATETIME2 | Fecha/hora del procesamiento |
| processing_time | FLOAT | Tiempo de procesamiento en segundos |
| extracted_data | NVARCHAR(MAX) | Datos extraídos en formato JSON |

## 📁 Archivos de Ejemplo

### URLs de Prueba (`examples/urls_example.txt`)
```
https://httpbin.org/html
https://httpbin.org/json
https://httpbin.org/xml
https://example.com
https://httpbin.org/headers
```

### Selectores CSS (`examples/selectors_example.json`)
```json
{
    "titulo": "h1",
    "subtitulo": "h2",
    "parrafo": "p",
    "enlaces": "a",
    "lista": "ul li",
    "tabla": "table",
    "imagenes": "img",
    "div_contenido": "div.content",
    "span_fecha": "span.date",
    "clase_especial": ".special-class"
}
```

## 🔧 Configuración Avanzada

### Selectores CSS

Puedes especificar selectores CSS para extraer datos específicos:

```json
{
    "titulo": "h1.article-title",
    "autor": "span.author-name",
    "fecha": "time.published-date",
    "contenido": "div.article-content",
    "etiquetas": "div.tags a"
}
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
