@echo off
echo 🚀 Iniciando Neptuno Scraping Worker con Docker...
echo.

echo 📦 Construyendo imagen Docker...
docker-compose build

echo.
echo 🎯 Iniciando worker de scraping...
docker-compose up -d

echo.
echo ✅ Worker iniciado correctamente!
echo.
echo 📊 Para ver logs del worker:
echo    docker-compose logs -f scraping-worker
echo.
echo 🌐 RabbitMQ Management (servicio externo):
echo    http://localhost:15672
echo    Usuario: admin
echo    Contraseña: admin123
echo.
echo 📋 Para ver estado de contenedores:
echo    docker-compose ps
echo.
echo ⚠️  NOTA: RabbitMQ debe estar ejecutándose en otro proyecto
echo.
pause
