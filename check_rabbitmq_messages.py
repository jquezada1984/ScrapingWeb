#!/usr/bin/env python3
"""
Script para consultar y visualizar mensajes en la cola de RabbitMQ
"""

import json
import pika
from src.config import Config

def get_messages_from_queue():
    """Obtiene y muestra los mensajes de la cola de RabbitMQ"""
    try:
        # Conectar a RabbitMQ
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
        channel.exchange_declare(exchange=Config.RABBITMQ_EXCHANGE, exchange_type='direct', durable=True)
        
        # Vincular la cola al exchange
        channel.queue_bind(
            exchange=Config.RABBITMQ_EXCHANGE,
            queue=Config.RABBITMQ_QUEUE,
            routing_key=Config.RABBITMQ_ROUTING_KEY
        )
        
        print("🔍 Conectado a RabbitMQ exitosamente")
        print(f"📊 Exchange: {Config.RABBITMQ_EXCHANGE}")
        print(f"📊 Cola: {Config.RABBITMQ_QUEUE}")
        print(f"📊 Routing Key: {Config.RABBITMQ_ROUTING_KEY}")
        print("=" * 60)
        
        # Obtener información de la cola
        queue_info = channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True, passive=True)
        message_count = queue_info.method.message_count
        consumer_count = queue_info.method.consumer_count
        
        print(f"📈 Mensajes en cola: {message_count}")
        print(f"👥 Consumidores activos: {consumer_count}")
        print("=" * 60)
        
        if message_count == 0:
            print("ℹ️  No hay mensajes en la cola")
            return
        
        # Función para procesar mensajes
        def process_message(ch, method, properties, body):
            try:
                # Decodificar el mensaje
                message_text = body.decode('utf-8')
                
                print(f"\n📨 MENSAJE #{method.delivery_tag}")
                print(f"🔑 Routing Key: {method.routing_key}")
                print(f"📅 Timestamp: {properties.timestamp if properties.timestamp else 'N/A'}")
                print(f"📋 Headers: {properties.headers if properties.headers else 'N/A'}")
                print(f"📝 Contenido:")
                
                # Intentar parsear como JSON
                try:
                    message_json = json.loads(message_text)
                    print(json.dumps(message_json, indent=2, ensure_ascii=False))
                except json.JSONDecodeError:
                    print(f"   {message_text}")
                
                print("-" * 40)
                
                # Acknowledge el mensaje
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                print(f"❌ Error procesando mensaje: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        # Configurar QoS para procesar un mensaje a la vez
        channel.basic_qos(prefetch_count=1)
        
        # Consumir mensajes
        print("🔄 Consumiendo mensajes...")
        print("💡 Presiona Ctrl+C para detener")
        print("=" * 60)
        
        channel.basic_consume(
            queue=Config.RABBITMQ_QUEUE,
            on_message_callback=process_message
        )
        
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            print("\n⏹️  Deteniendo consumo de mensajes...")
            channel.stop_consuming()
        
    except Exception as e:
        print(f"❌ Error conectando a RabbitMQ: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
            print("🔌 Conexión cerrada")

if __name__ == "__main__":
    print("🚀 Iniciando consulta de mensajes en RabbitMQ...")
    get_messages_from_queue()
