#!/usr/bin/env python3
"""
Script para debuggear la conexión y consumo de mensajes de RabbitMQ
"""
import pika
import json
import time
import sys
from src.config import Config

def debug_rabbitmq_consumer():
    """Debug de la conexión y consumo de mensajes"""
    try:
        print("🔍 DEBUG: Verificando conexión y consumo de RabbitMQ...")
        print(f"   Host: {Config.RABBITMQ_HOST}")
        print(f"   Port: {Config.RABBITMQ_PORT}")
        print(f"   Username: {Config.RABBITMQ_USERNAME}")
        print(f"   Password: {'*' * len(Config.RABBITMQ_PASSWORD) if Config.RABBITMQ_PASSWORD else 'None'}")
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
        
        # Verificar estado de la cola
        print(f"\n📊 Verificando cola '{Config.RABBITMQ_QUEUE}'...")
        queue_info = channel.queue_declare(queue=Config.RABBITMQ_QUEUE, passive=True)
        message_count = queue_info.method.message_count
        consumer_count = queue_info.method.consumer_count
        
        print(f"   • Mensajes en cola: {message_count}")
        print(f"   • Consumidores activos: {consumer_count}")
        
        # Verificar exchange
        print(f"\n📊 Verificando exchange '{Config.RABBITMQ_EXCHANGE}'...")
        try:
            exchange_info = channel.exchange_declare(
                exchange=Config.RABBITMQ_EXCHANGE,
                exchange_type='direct',
                passive=True
            )
            print("✅ Exchange existe y es accesible")
        except Exception as e:
            print(f"⚠️ Exchange no existe o no es accesible: {e}")
            print("🔄 Creando exchange...")
            channel.exchange_declare(
                exchange=Config.RABBITMQ_EXCHANGE,
                exchange_type='direct',
                durable=True
            )
            print("✅ Exchange creado")
        
        # Verificar binding
        print(f"\n📊 Verificando binding...")
        try:
            # Intentar hacer el binding
            channel.queue_bind(
                exchange=Config.RABBITMQ_EXCHANGE,
                queue=Config.RABBITMQ_QUEUE,
                routing_key=Config.RABBITMQ_ROUTING_KEY
            )
            print("✅ Binding configurado correctamente")
        except Exception as e:
            print(f"⚠️ Error en binding: {e}")
        
        # Configurar QoS
        print(f"\n📊 Configurando QoS...")
        channel.basic_qos(prefetch_count=1)
        print("✅ QoS configurado")
        
        # Función callback para mensajes
        def callback(ch, method, properties, body):
            try:
                print(f"\n📨 MENSAJE RECIBIDO:")
                print(f"   • Delivery tag: {method.delivery_tag}")
                print(f"   • Routing key: {method.routing_key}")
                print(f"   • Exchange: {method.exchange}")
                print(f"   • Redelivered: {method.redelivered}")
                
                # Decodificar mensaje
                mensaje = json.loads(body.decode('utf-8'))
                print(f"   • Contenido: {json.dumps(mensaje, indent=2, ensure_ascii=False)}")
                
                # Confirmar mensaje
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print("✅ Mensaje confirmado")
                
            except Exception as e:
                print(f"❌ Error procesando mensaje: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        # Configurar consumo
        print(f"\n📊 Configurando consumo de mensajes...")
        channel.basic_consume(
            queue=Config.RABBITMQ_QUEUE,
            on_message_callback=callback
        )
        print("✅ Consumo configurado")
        
        # Verificar estado final
        queue_info_final = channel.queue_declare(queue=Config.RABBITMQ_QUEUE, passive=True)
        print(f"\n📊 Estado final de la cola:")
        print(f"   • Mensajes en cola: {queue_info_final.method.message_count}")
        print(f"   • Consumidores activos: {queue_info_final.method.consumer_count}")
        
        if queue_info_final.method.message_count > 0:
            print(f"\n⏳ Iniciando consumo de {queue_info_final.method.message_count} mensaje(s)...")
            print("   (Presiona Ctrl+C para detener)")
            channel.start_consuming()
        else:
            print(f"\n⏳ No hay mensajes en la cola, esperando nuevos mensajes...")
            print("   (Presiona Ctrl+C para detener)")
            channel.start_consuming()
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Deteniendo consumo...")
        try:
            channel.stop_consuming()
            connection.close()
            print("✅ Conexión cerrada correctamente")
        except:
            pass
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = debug_rabbitmq_consumer()
    sys.exit(0 if success else 1)
