#!/usr/bin/env python3
"""
Script para enviar un mensaje de prueba a RabbitMQ
"""
import pika
import json
import sys
from src.config import Config

def enviar_mensaje_prueba():
    """Envía un mensaje de prueba a RabbitMQ"""
    try:
        print("🔍 Enviando mensaje de prueba a RabbitMQ...")
        print(f"   Host: {Config.RABBITMQ_HOST}")
        print(f"   Port: {Config.RABBITMQ_PORT}")
        print(f"   Queue: {Config.RABBITMQ_QUEUE}")
        print(f"   Exchange: {Config.RABBITMQ_EXCHANGE}")
        print(f"   Routing Key: {Config.RABBITMQ_ROUTING_KEY}")
        
        # Crear parámetros de conexión
        credentials = pika.PlainCredentials(Config.RABBITMQ_USERNAME, Config.RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=Config.RABBITMQ_HOST,
            port=Config.RABBITMQ_PORT,
            virtual_host='/',
            credentials=credentials
        )
        
        # Conectar
        print("\n🔄 Conectando a RabbitMQ...")
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        print("✅ Conexión exitosa!")
        
        # Declarar exchange y cola
        channel.exchange_declare(
            exchange=Config.RABBITMQ_EXCHANGE,
            exchange_type='direct',
            durable=True
        )
        
        channel.queue_declare(
            queue=Config.RABBITMQ_QUEUE,
            durable=True
        )
        
        # Hacer binding
        channel.queue_bind(
            exchange=Config.RABBITMQ_EXCHANGE,
            queue=Config.RABBITMQ_QUEUE,
            routing_key=Config.RABBITMQ_ROUTING_KEY
        )
        
        # Crear mensaje de prueba
        mensaje_prueba = {
            "IdFactura": "TEST-001",
            "NombreCompleto": "PAN AMERICAN LIFE DE ECUADOR",
            "Clientes": [
                {
                    "IdFactura": "TEST-001",
                    "NumDocIdentidad": "1234567890",
                    "PersonaPrimerNombre": "Juan",
                    "PersonaSegundoNombre": "Carlos",
                    "PersonaPrimerApellido": "Pérez",
                    "PersonaSegundoApellido": "García"
                }
            ]
        }
        
        # Enviar mensaje
        print(f"\n📤 Enviando mensaje de prueba...")
        message_body = json.dumps(mensaje_prueba, ensure_ascii=False)
        
        channel.basic_publish(
            exchange=Config.RABBITMQ_EXCHANGE,
            routing_key=Config.RABBITMQ_ROUTING_KEY,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Hacer el mensaje persistente
                content_type='application/json'
            )
        )
        
        print("✅ Mensaje enviado exitosamente!")
        print(f"   • Contenido: {json.dumps(mensaje_prueba, indent=2, ensure_ascii=False)}")
        
        # Verificar estado de la cola después de enviar
        queue_info = channel.queue_declare(queue=Config.RABBITMQ_QUEUE, passive=True)
        print(f"\n📊 Estado de la cola después de enviar:")
        print(f"   • Mensajes en cola: {queue_info.method.message_count}")
        print(f"   • Consumidores activos: {queue_info.method.consumer_count}")
        
        # Cerrar conexión
        connection.close()
        print("\n✅ Conexión cerrada correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = enviar_mensaje_prueba()
    sys.exit(0 if success else 1)
