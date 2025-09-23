# Configuración Docker - Sin RabbitMQ

## 📋 Cambios Realizados

Se ha modificado la configuración de Docker para **eliminar RabbitMQ** del proyecto, ya que se ejecuta en otro proyecto.

### 🔧 Archivos Modificados

#### 1. `docker-compose.yml`
- ❌ **Eliminado**: Servicio `rabbitmq`
- ❌ **Eliminado**: Dependencia `depends_on: rabbitmq`
- ❌ **Eliminado**: Volumen `rabbitmq_data`
- ✅ **Agregado**: Red externa `external_network` para conectar con RabbitMQ externo

#### 2. `docker.env`
- 🔄 **Modificado**: `RABBITMQ_HOST=host.docker.internal` (apunta al host)
- ✅ **Mantenido**: Resto de configuración de RabbitMQ

#### 3. `start-docker.bat`
- 🔄 **Actualizado**: Mensajes para reflejar que RabbitMQ es externo
- ✅ **Agregado**: Nota sobre RabbitMQ externo

## 🚀 Cómo Ejecutar

### Prerrequisitos
1. **RabbitMQ** debe estar ejecutándose en otro proyecto
2. **SQL Server** debe estar ejecutándose en `DESKTOP-BO3S185:1433`

### Inicio del Worker
```bash
# Opción 1: Script de Windows
start-docker.bat

# Opción 2: Comandos manuales
docker-compose up -d
```

### Verificar Estado
```bash
# Ver logs del worker
docker-compose logs -f scraping-worker

# Ver estado de contenedores
docker-compose ps
```

## 🔗 Conexiones Externas

### RabbitMQ
- **Host**: `host.docker.internal` (desde Docker)
- **Puerto**: 5672
- **Management**: http://localhost:15672
- **Credenciales**: admin/admin123

### SQL Server
- **Host**: `host.docker.internal` (desde Docker)
- **Puerto**: 1433
- **Base de datos**: NeptunoMedicalAutomatico
- **Credenciales**: sa/M@st3r2023

## 📊 Estructura Final

```
scraping_web/
├── docker-compose.yml          # Solo worker de scraping
├── docker.env                  # Configuración para servicios externos
├── start-docker.bat           # Script de inicio actualizado
└── DOCKER_CONFIGURATION.md    # Esta documentación
```

## ⚠️ Notas Importantes

1. **RabbitMQ externo**: Debe estar ejecutándose en otro proyecto
2. **Red externa**: El worker se conecta a la red externa donde está RabbitMQ
3. **Configuración**: Los archivos `.env` deben tener las credenciales correctas
4. **Logs**: Revisar logs para verificar conexiones exitosas

## 🔍 Troubleshooting

### Error de conexión a RabbitMQ
```bash
# Verificar que RabbitMQ esté ejecutándose
docker ps | grep rabbitmq

# Verificar logs del worker
docker-compose logs -f scraping-worker
```

### Error de conexión a SQL Server
```bash
# Verificar que SQL Server esté ejecutándose
# Desde el host: DESKTOP-BO3S185:1433
```

## 📝 Comandos Útiles

```bash
# Iniciar worker
docker-compose up -d

# Ver logs
docker-compose logs -f scraping-worker

# Reiniciar worker
docker-compose restart scraping-worker

# Detener worker
docker-compose down

# Ver estado
docker-compose ps
```
