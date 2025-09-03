#!/usr/bin/env python3
"""
Script para enviar mensaje de prueba con NumDocIdentidad a RabbitMQ
"""

import json
import pika
import sys
from src.config import Config

def enviar_mensaje_prueba():
    """Envía un mensaje de prueba a RabbitMQ"""
    
    # Mensaje de prueba con NumDocIdentidad
    mensaje_prueba = {
        "Clientes": [
            {
                "NombreCompleto": "PAN AMERICAN LIFE DE ECUADOR",
                "NumDocIdentidad": "0102158896",  # Usar el mismo número que aparece en el HTML
                "TipoDocumento": "Cédula",
                "FechaNacimiento": "1985-03-15",
                "Genero": "F",
                "EstadoCivil": "Soltero",
                "Direccion": "Av. Amazonas N45-123",
                "Ciudad": "Quito",
                "Provincia": "Pichincha",
                "Telefono": "0987654321",
                "Email": "cliente@ejemplo.com",
                "Ocupacion": "Ingeniero",
                "IngresosMensuales": 2500.00,
                "FechaSolicitud": "2025-09-02"
            }
        ],
        "FechaProcesamiento": "2025-09-02T15:30:00",
        "TotalClientes": 1,
        "Origen": "Script de Prueba",
        "Version": "1.0"
    }
    
    try:
        # Conectar a RabbitMQ
        print("🔌 Conectando a RabbitMQ...")
        credentials = pika.PlainCredentials(Config.RABBITMQ_USERNAME, Config.RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=credentials
            )
        )
        
        channel = connection.channel()
        
        # Declarar la cola y el exchange
        channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True)
        channel.exchange_declare(
            exchange=Config.RABBITMQ_EXCHANGE, 
            exchange_type='direct', 
            durable=True
        )
        
        # Vincular la cola al exchange
        channel.queue_bind(
            exchange=Config.RABBITMQ_EXCHANGE,
            queue=Config.RABBITMQ_QUEUE,
            routing_key=Config.RABBITMQ_ROUTING_KEY
        )
        
        print("✅ Conectado a RabbitMQ exitosamente")
        
        # Enviar mensaje
        mensaje_json = json.dumps(mensaje_prueba, ensure_ascii=False, indent=2)
        print(f"📨 Enviando mensaje:")
        print(f"   • NumDocIdentidad: {mensaje_prueba['Clientes'][0]['NumDocIdentidad']}")
        print(f"   • Aseguradora: {mensaje_prueba['Clientes'][0]['NombreCompleto']}")
        
        channel.basic_publish(
            exchange=Config.RABBITMQ_EXCHANGE,
            routing_key=Config.RABBITMQ_ROUTING_KEY,
            body=mensaje_json,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Hacer el mensaje persistente
                content_type='application/json'
            )
        )
        
        print("✅ Mensaje enviado exitosamente a RabbitMQ")
        print("🔄 Ahora ejecuta el worker para procesar el mensaje:")
        print("   python run_production_worker.py")
        
        # Cerrar conexión
        connection.close()
        
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Enviando mensaje de prueba a RabbitMQ...")
    print("=" * 60)
    enviar_mensaje_prueba()
    print("=" * 60)
    print("✅ Script completado")
