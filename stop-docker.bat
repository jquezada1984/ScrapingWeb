@echo off
echo 🛑 Deteniendo Neptuno Scraping Worker...
echo.

echo 📋 Deteniendo servicios...
docker-compose down

echo.
echo ✅ Servicios detenidos correctamente!
echo.
echo 🧹 Para limpiar volúmenes y datos:
echo    docker-compose down -v
echo.
pause
