#!/bin/bash

# Script de entrada para Docker
set -e

echo "🚀 Iniciando Neptuno Scraping Worker..."

# Esperar a que RabbitMQ esté disponible
echo "⏳ Esperando a que RabbitMQ esté disponible..."
while ! nc -z $RABBITMQ_HOST $RABBITMQ_PORT; do
  echo "   • RabbitMQ no está disponible aún, esperando..."
  sleep 2
done
echo "✅ RabbitMQ está disponible"

# Esperar a que SQL Server esté disponible (si está en Docker)
if [ "$SQL_SERVER_HOST" != "host.docker.internal" ]; then
    echo "⏳ Esperando a que SQL Server esté disponible..."
    while ! nc -z $SQL_SERVER_HOST $SQL_SERVER_PORT; do
        echo "   • SQL Server no está disponible aún, esperando..."
        sleep 2
    done
    echo "✅ SQL Server está disponible"
fi

# Crear directorio de logs si no existe
mkdir -p /app/logs

# Ejecutar el worker
echo "🎯 Iniciando worker de scraping..."
exec "$@"
