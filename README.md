# Proyecto de Scraping Web con SQL Server y RabbitMQ

Este proyecto implementa un sistema de scraping web distribuido que utiliza RabbitMQ para la gestión de tareas y SQL Server para el almacenamiento de datos.

## 📁 Estructura del Proyecto

```
scraping_web/
├── src/                          # Código fuente principal
│   ├── __init__.py
│   ├── config.py                 # Configuración y variables de entorno
│   ├── database.py               # Gestión de conexión a SQL Server
│   ├── rabbitmq_client.py        # Cliente para RabbitMQ
│   ├── scraper.py                # Motor de scraping web
│   └── scraping_worker.py        # Worker principal que coordina todo
├── aseguradoras/                 # Procesadores específicos por aseguradora
│   └── pan_american_life_ecuador/
│       ├── implementacion_oauth2.py
│       └── config.py
├── run_production_worker.py      # Worker de producción principal (SIEMPRE ACTIVO)
├── requirements.txt              # Dependencias de Python
├── config_neptuno.env            # Configuración local específica
├── docker.env                       # Configuración para Docker (servicios externos)
├── docker-compose.yml            # Orquestación de servicios Docker (sin RabbitMQ)
├── Dockerfile                    # Imagen Docker del worker (con Chrome)
├── docker-entrypoint.sh          # Script de inicio Docker
├── start-docker.bat              # Script de inicio Windows
├── stop-docker.bat               # Script de parada Windows
├── DOCKER_README.md              # Documentación Docker
├── DOCKER_CONFIGURATION.md       # Documentación de configuración Docker
├── .dockerignore                 # Archivos a ignorar en Docker
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

## 📊 Estado Actual del Proyecto

### ✅ **Funcionando Correctamente**
- **Docker**: Imagen construida exitosamente
- **RabbitMQ**: Conexión establecida a servicio externo
- **SQL Server**: Motor inicializado correctamente
- **Worker**: Procesador funcionando con caché de URLs
- **Logging**: Sistema de logs detallado operativo

### ⚠️ **En Desarrollo**
- **Selenium/Chrome**: Requiere ajustes adicionales para funcionar en Docker
- **Navegador**: Configuración de ChromeDriver en progreso

### 🔧 **Configuración Actual**
- **Sin RabbitMQ interno**: Se conecta a servicio externo
- **SQL Server externo**: DESKTOP-BO3S185:1433
- **Docker optimizado**: Imagen con Chrome y ODBC Driver

## 📋 Requisitos Previos

### Software Necesario

1. **Docker Desktop** (instalado y ejecutándose)
2. **Docker Compose** (incluido con Docker Desktop)
3. **SQL Server** (DESKTOP-BO3S185:1433 - servicio externo)

### Servicios Externos Requeridos

- **SQL Server**: Debe estar ejecutándose en DESKTOP-BO3S185:1433
- **RabbitMQ**: Debe estar ejecutándose en otro proyecto (puerto 5672 y 15672)

### Configuración de SQL Server

El proyecto está configurado para conectarse a SQL Server externo:
- **Servidor**: `DESKTOP-BO3S185:1433`
- **Base de datos**: `NeptunoMedicalAutomatico`
- **Autenticación**: SQL Server (usuario: `sa`, contraseña: `M@st3r2023`)
- **Driver**: Microsoft ODBC Driver 17 for SQL Server (incluido en Docker)

## 🛠️ Instalación con Docker

### Prerrequisitos

- **Docker Desktop** instalado y ejecutándose
- **Docker Compose** instalado
- **SQL Server** ejecutándose en DESKTOP-BO3S185:1433
- **RabbitMQ** ejecutándose en otro proyecto (puerto 5672 y 15672)

### ⚠️ Configuración Actualizada

**IMPORTANTE**: Este proyecto se ejecuta **SIN RabbitMQ interno**. RabbitMQ debe estar ejecutándose en otro proyecto y ser accesible desde el worker.

### Instalación Rápida

1. **Clonar el repositorio**
   ```bash
   git clone <tu-repositorio>
   cd scraping_web
   ```

2. **Iniciar con Docker (Opción 1: Script de Windows)**
   ```bash
   # Ejecutar script de inicio
   start-docker.bat
   ```

3. **Iniciar con Docker (Opción 2: Comandos manuales)**
   ```bash
   # Construir e iniciar servicios
   docker-compose up -d
   
   # Ver logs del worker
   docker-compose logs -f scraping-worker
   ```

### Verificar Instalación

- **RabbitMQ Management**: http://localhost:15672 (admin/admin123) - **Servicio externo**
- **Logs del Worker**: `docker-compose logs -f scraping-worker`
- **Estado de Contenedores**: `docker-compose ps`

### ⚠️ Notas Importantes

1. **RabbitMQ externo**: Debe estar ejecutándose en otro proyecto
2. **SQL Server externo**: Debe estar ejecutándose en DESKTOP-BO3S185:1433
3. **Configuración**: Los archivos `.env` deben tener las credenciales correctas
4. **Logs**: Revisar logs para verificar conexiones exitosas

## ⚙️ Configuración

### Variables de Entorno (docker.env)

```env
# Configuración de SQL Server
SQL_SERVER_HOST=host.docker.internal
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=NeptunoMedicalAutomatico
SQL_SERVER_USERNAME=sa
SQL_SERVER_PASSWORD=M@st3r2023
SQL_SERVER_TRUSTED_CONNECTION=false

# Configuración de RabbitMQ (servicio en Docker)
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=admin123
RABBITMQ_QUEUE=aseguradora_queue
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

### Guía de Ejecución con Docker

#### Paso 1: Inicio Rápido
```bash
# Opción 1: Script de Windows
start-docker.bat

# Opción 2: Comandos manuales
docker-compose up -d
```

#### Paso 2: Verificar Servicios
```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs del worker
docker-compose logs -f scraping-worker

# Acceder a RabbitMQ Management
# http://localhost:15672 (admin/admin123)
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

### 🎯 Ejecución en Producción con Docker

#### **Opción 1: Docker Compose Básico (Sin Selenium)**
```bash
# Iniciar worker de producción (SIEMPRE ACTIVO)
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f scraping-worker

# Reiniciar worker si es necesario
docker-compose restart scraping-worker
```

#### **Opción 2: Docker Compose con Selenium Grid (RECOMENDADO)**
```bash
# Iniciar worker con Selenium Grid incluido
docker-compose -f docker-compose-selenium.yml up -d

# Ver logs en tiempo real
docker-compose -f docker-compose-selenium.yml logs -f scraping-worker

# Ver estado de todos los servicios
docker-compose -f docker-compose-selenium.yml ps

# Acceder a noVNC para ver el navegador
# Abrir: http://localhost:7900
```

#### **Scripts de Windows (Automáticos)**
```bash
# Iniciar todo el sistema
start-docker.bat

# Detener todo el sistema
stop-docker.bat

# Monitorear logs
monitor-worker.bat

# Desplegar cambios
deploy-changes.bat
```

### 🔄 Flujo de Trabajo del Sistema

1. **Recepción**: El worker recibe mensajes de aseguradoras desde RabbitMQ
2. **Procesamiento**: Extrae el `NombreCompleto` del mensaje
3. **Búsqueda**: Consulta la tabla `urls_automatizacion` en SQL Server
4. **Caché**: Almacena URLs en memoria para futuras consultas
5. **Resultado**: Combina información del mensaje con la URL encontrada

### 📋 Comandos de Docker

#### **Comandos Básicos (Sin Selenium)**
```bash
# Iniciar worker de producción
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f scraping-worker

# Detener servicios
docker-compose down

# Reiniciar solo el worker
docker-compose restart scraping-worker

# Ver estado de contenedores
docker-compose ps
```

#### **Comandos con Selenium Grid (RECOMENDADO)**
```bash
# Iniciar worker con Selenium Grid
docker-compose -f docker-compose-selenium.yml up -d

# Ver logs en tiempo real
docker-compose -f docker-compose-selenium.yml logs -f scraping-worker

# Ver logs de Selenium
docker-compose -f docker-compose-selenium.yml logs -f selenium

# Detener todos los servicios
docker-compose -f docker-compose-selenium.yml down

# Reiniciar solo el worker
docker-compose -f docker-compose-selenium.yml restart scraping-worker

# Ver estado de todos los contenedores
docker-compose -f docker-compose-selenium.yml ps

# Acceder a noVNC (ver navegador)
# Abrir: http://localhost:7900
```

#### **Comandos de Construcción**
```bash
# Construir imagen Docker básica
docker-compose build

# Construir imagen con Selenium Grid
docker-compose -f docker-compose-selenium.yml build

# Construir sin caché (si hay problemas)
docker-compose -f docker-compose-selenium.yml build --no-cache

# Construir imagen específica
docker build -t neptuno-scraping-worker .
```

#### **Comandos de Testing y Monitoreo**
```bash
# Enviar mensaje de prueba
python send_test_message.py

# Verificar estado de RabbitMQ
netstat -an | findstr :5672

# Acceder a noVNC (ver navegador en tiempo real)
# Abrir: http://localhost:7900

# Monitorear logs en tiempo real
docker-compose -f docker-compose-selenium.yml logs -f

# Ver logs específicos del worker
docker-compose -f docker-compose-selenium.yml logs -f scraping-worker

# Ver logs de Selenium
docker-compose -f docker-compose-selenium.yml logs -f selenium
```

#### **Comandos de Logs y Debugging**
```bash
# Ver logs del worker
docker-compose logs -f scraping-worker

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs con timestamp
docker-compose logs -f -t scraping-worker

# Ver solo errores
docker-compose logs scraping-worker | grep -E "(❌|ERROR|Error)"

# Ver conexiones exitosas
docker-compose logs scraping-worker | grep -E "(✅|Conectado|SUCCESS)"
```

#### **Comandos de Limpieza**
```bash
# Detener y eliminar contenedores
docker-compose down

# Detener y eliminar contenedores + volúmenes
docker-compose down -v

# Limpiar sistema Docker
docker system prune -a

# Limpiar imágenes no utilizadas
docker image prune -a
```

#### **Comandos de Monitoreo**
```bash
# Ver estado de contenedores
docker-compose ps

# Ver uso de recursos
docker stats

# Ver información del contenedor
docker inspect neptuno-scraping-worker

# Ejecutar comando dentro del contenedor
docker-compose exec scraping-worker bash
```

#### **Comandos de Troubleshooting**
```bash
# Verificar configuración
docker-compose config

# Ver variables de entorno
docker-compose exec scraping-worker env

# Verificar conectividad
docker-compose exec scraping-worker ping host.docker.internal

# Ver logs de construcción
docker-compose build --progress=plain
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

### **Comandos Docker (Recomendado)**
| Comando | Descripción |
|---------|-------------|
| `start-docker.bat` | Iniciar worker con Docker (Windows) |
| `docker-compose up -d` | Iniciar worker con Docker |
| `docker-compose logs -f scraping-worker` | Ver logs del worker |
| `docker-compose ps` | Ver estado de contenedores |
| `docker-compose restart scraping-worker` | Reiniciar worker |
| `docker-compose down` | Detener worker |

### **Comandos Locales (Sin Docker)**
| Comando | Descripción |
|---------|-------------|
| `python test_connection.py` | Probar conexiones a SQL Server y RabbitMQ |
| `python run_production_worker.py` | Iniciar el worker de scraping |
| `python publisher.py --url "URL"` | Publicar tarea única |
| `python publisher.py --file archivo.txt` | Publicar múltiples URLs |
| `python quick_start.py` | Prueba rápida completa del sistema |

### **Comandos de Construcción Docker**
| Comando | Descripción |
|---------|-------------|
| `docker-compose build` | Construir imagen Docker |
| `docker-compose build --no-cache` | Construir sin caché |
| `docker build -t neptuno-scraping-worker .` | Construir imagen específica |

### **Comandos de Limpieza**
| Comando | Descripción |
|---------|-------------|
| `docker-compose down -v` | Detener y limpiar volúmenes |
| `docker system prune -a` | Limpiar sistema Docker |
| `docker image prune -a` | Limpiar imágenes no utilizadas |

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

### Escenario 4: Ejecución con Docker (Recomendado)
```bash
# 1. Configurar docker.env con servicios externos
# 2. Ejecutar con Docker
docker-compose up -d

# 3. Ver logs
docker-compose logs -f scraping-worker

# 4. Acceder a RabbitMQ Management
# http://localhost:15672 (admin/admin123)
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

## 🐳 Docker Setup

### Archivos de Docker

- **`Dockerfile`**: Imagen del worker con todas las dependencias
- **`docker-compose.yml`**: Orquestación de servicios (worker + RabbitMQ)
- **`docker.env`**: Variables de entorno para Docker
- **`docker-entrypoint.sh`**: Script de inicio con health checks
- **`start-docker.bat`**: Script de inicio para Windows
- **`stop-docker.bat`**: Script de parada para Windows
- **`DOCKER_README.md`**: Documentación completa de Docker

### Comandos Docker Principales

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs del worker
docker-compose logs -f scraping-worker

# Reiniciar worker
docker-compose restart scraping-worker

# Detener servicios
docker-compose down

# Limpiar volúmenes
docker-compose down -v
```

### Accesos

- **RabbitMQ Management**: http://localhost:15672 (admin/admin123)
- **SQL Server**: DESKTOP-BO3S185:1433 (desde el host)

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

## 🛠️ Comandos Útiles para Troubleshooting

### **Verificar Estado del Sistema**
```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f scraping-worker

# Ver uso de recursos
docker stats

# Verificar configuración
docker-compose config
```

### **Debugging de Conexiones**
```bash
# Ver logs de conexión a RabbitMQ
docker-compose logs scraping-worker | grep -E "(RabbitMQ|rabbitmq)"

# Ver logs de conexión a SQL Server
docker-compose logs scraping-worker | grep -E "(SQL|sql|database)"

# Ver solo errores
docker-compose logs scraping-worker | grep -E "(❌|ERROR|Error|Exception)"

# Ver conexiones exitosas
docker-compose logs scraping-worker | grep -E "(✅|SUCCESS|Conectado)"
```

### **Comandos de Limpieza y Mantenimiento**
```bash
# Detener y limpiar todo
docker-compose down -v

# Limpiar sistema Docker
docker system prune -a

# Limpiar imágenes no utilizadas
docker image prune -a

# Reconstruir sin caché
docker-compose build --no-cache
```

### **Comandos de Monitoreo Avanzado**
```bash
# Ver información detallada del contenedor
docker inspect neptuno-scraping-worker

# Ejecutar bash dentro del contenedor
docker-compose exec scraping-worker bash

# Ver variables de entorno
docker-compose exec scraping-worker env

# Verificar conectividad de red
docker-compose exec scraping-worker ping host.docker.internal
```

### **Comandos de Logs Específicos**
```bash
# Ver logs con timestamp
docker-compose logs -f -t scraping-worker

# Ver logs de los últimos 100 líneas
docker-compose logs --tail=100 scraping-worker

# Ver logs de una fecha específica
docker-compose logs --since="2025-01-09T10:00:00" scraping-worker

# Ver logs hasta una fecha específica
docker-compose logs --until="2025-01-09T18:00:00" scraping-worker
```

### **Comandos de Reinicio y Recuperación**
```bash
# Reiniciar solo el worker
docker-compose restart scraping-worker

# Detener y volver a iniciar
docker-compose down && docker-compose up -d

# Forzar recreación del contenedor
docker-compose up -d --force-recreate scraping-worker
```