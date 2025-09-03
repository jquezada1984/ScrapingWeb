#!/usr/bin/env python3
"""
Script simple para probar la conexión a RabbitMQ
"""

import logging
import pika
from src.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_rabbitmq():
    """Prueba la conexión a RabbitMQ"""
    
    logger.info("🚀 INICIANDO PRUEBA DE CONEXIÓN A RABBITMQ")
    logger.info("=" * 60)
    
    try:
        # Mostrar configuración
        logger.info("📋 Configuración RabbitMQ:")
        logger.info(f"   • Host: {Config.RABBITMQ_HOST}")
        logger.info(f"   • Puerto: {Config.RABBITMQ_PORT}")
        logger.info(f"   • Usuario: {Config.RABBITMQ_USERNAME}")
        logger.info(f"   • Cola: {Config.RABBITMQ_QUEUE}")
        logger.info(f"   • Exchange: {Config.RABBITMQ_EXCHANGE}")
        
        # Probar conexión
        logger.info("🔌 Probando conexión a RabbitMQ...")
        
        credentials = pika.PlainCredentials(Config.RABBITMQ_USERNAME, Config.RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=credentials
            )
        )
        
        logger.info("✅ Conexión a RabbitMQ exitosa")
        
        # Crear canal
        channel = connection.channel()
        logger.info("✅ Canal creado exitosamente")
        
        # Declarar cola
        queue_info = channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True, passive=True)
        message_count = queue_info.method.message_count
        consumer_count = queue_info.method.consumer_count
        
        logger.info(f"📊 Estado de la cola:")
        logger.info(f"   • Mensajes en cola: {message_count}")
        logger.info(f"   • Consumidores activos: {consumer_count}")
        
        # Cerrar conexión
        connection.close()
        logger.info("✅ Conexión cerrada correctamente")
        
        logger.info("=" * 60)
        logger.info("🎯 CONEXIÓN A RABBITMQ VERIFICADA EXITOSAMENTE")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error conectando a RabbitMQ: {e}")
        return False

if __name__ == "__main__":
    success = test_rabbitmq()
    exit(0 if success else 1)
