# 🐳 Docker Setup para Neptuno Scraping Worker

## 📋 Prerrequisitos

- Docker Desktop instalado
- Docker Compose instalado
- Acceso a la base de datos SQL Server (DESKTOP-BO3S185)

## 🚀 Instrucciones de Instalación

### 1. Construir la imagen Docker

```bash
docker-compose build
```

### 2. Iniciar los servicios

```bash
docker-compose up -d
```

### 3. Ver logs del worker

```bash
docker-compose logs -f scraping-worker
```

### 4. Ver logs de RabbitMQ

```bash
docker-compose logs -f rabbitmq
```

## 🔧 Configuración

### Variables de Entorno

Las variables de entorno se configuran en el archivo `docker.env`:

- **SQL_SERVER_HOST**: `host.docker.internal` (para acceder al host desde Docker)
- **RABBITMQ_HOST**: `rabbitmq` (nombre del servicio en Docker)

### Acceso a Servicios

- **RabbitMQ Management**: http://localhost:15672
  - Usuario: `admin`
  - Contraseña: `admin123`

- **SQL Server**: Acceso directo desde el host (DESKTOP-BO3S185:1433)

## 📊 Comandos Útiles

### Ver estado de contenedores
```bash
docker-compose ps
```

### Reiniciar el worker
```bash
docker-compose restart scraping-worker
```

### Detener todos los servicios
```bash
docker-compose down
```

### Detener y eliminar volúmenes
```bash
docker-compose down -v
```

### Reconstruir solo el worker
```bash
docker-compose build scraping-worker
docker-compose up -d scraping-worker
```

## 🐛 Troubleshooting

### Problemas de Conexión a SQL Server

Si el worker no puede conectarse a SQL Server:

1. Verificar que SQL Server esté ejecutándose en DESKTOP-BO3S185
2. Verificar que el puerto 1433 esté abierto
3. Verificar credenciales en `docker.env`

### Problemas de Conexión a RabbitMQ

Si hay problemas con RabbitMQ:

1. Verificar que el contenedor esté ejecutándose: `docker-compose ps`
2. Verificar logs: `docker-compose logs rabbitmq`
3. Acceder a la interfaz web: http://localhost:15672

### Problemas con Selenium

Si hay problemas con el navegador:

1. Verificar que el contenedor tenga suficientes recursos
2. Aumentar `shm_size` en docker-compose.yml si es necesario

## 📁 Estructura de Archivos

```
├── Dockerfile                 # Imagen del worker
├── docker-compose.yml         # Orquestación de servicios
├── docker.env                 # Variables de entorno para Docker
├── docker-entrypoint.sh       # Script de inicio
├── .dockerignore              # Archivos a ignorar en build
└── DOCKER_README.md           # Este archivo
```

## 🔄 Actualizaciones

Para actualizar el worker:

1. Hacer cambios en el código
2. Reconstruir: `docker-compose build scraping-worker`
3. Reiniciar: `docker-compose restart scraping-worker`

## 📝 Logs

Los logs se almacenan en:
- Contenedor: `/app/logs/`
- Host: `./logs/` (mapeado como volumen)
