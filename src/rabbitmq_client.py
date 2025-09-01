import pika
import json
import logging
from typing import Callable, Optional, Dict, Any
from .config import Config

logger = logging.getLogger(__name__)

class RabbitMQClient:
    """Clase para manejar la conexión y operaciones con RabbitMQ"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = Config.RABBITMQ_QUEUE
        self.exchange_name = Config.RABBITMQ_EXCHANGE
        self._connect()
    
    def _connect(self):
        """Establece la conexión con RabbitMQ"""
        try:
            # Crear parámetros de conexión
            credentials = pika.PlainCredentials(
                Config.RABBITMQ_USERNAME, 
                Config.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            # Establecer conexión
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declarar exchange y cola
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='direct',
                durable=True
            )
            
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=Config.RABBITMQ_ROUTING_KEY
            )
            
            logger.info("Conexión a RabbitMQ establecida correctamente")
            
        except Exception as e:
            logger.error(f"Error al conectar con RabbitMQ: {e}")
            raise
    
    def publish_message(self, message: Dict[str, Any], routing_key: str = None):
        """Publica un mensaje en la cola de RabbitMQ"""
        try:
            if not self.connection or self.connection.is_closed:
                self._connect()
            
            # Usar el routing_key de la configuración si no se especifica uno
            if routing_key is None:
                routing_key = Config.RABBITMQ_ROUTING_KEY
            
            message_body = json.dumps(message, ensure_ascii=False)
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Hacer el mensaje persistente
                    content_type='application/json'
                )
            )
            logger.info(f"Mensaje publicado exitosamente: {message.get('url', 'N/A')}")
            return True
            
        except Exception as e:
            logger.error(f"Error al publicar mensaje: {e}")
            return False
    
    def consume_messages(self, callback: Callable, auto_ack: bool = False):
        """Consume mensajes de la cola de RabbitMQ"""
        try:
            if not self.connection or self.connection.is_closed:
                self._connect()
            
            # Configurar QoS
            self.channel.basic_qos(prefetch_count=1)
            
            # Configurar callback
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=auto_ack
            )
            
            logger.info("Iniciando consumo de mensajes de RabbitMQ...")
            self.channel.start_consuming()
            
        except Exception as e:
            logger.error(f"Error al consumir mensajes: {e}")
            raise
    
    def ack_message(self, delivery_tag: int):
        """Confirma el procesamiento de un mensaje"""
        try:
            self.channel.basic_ack(delivery_tag=delivery_tag)
            logger.debug(f"Mensaje confirmado: {delivery_tag}")
        except Exception as e:
            logger.error(f"Error al confirmar mensaje: {e}")
    
    def nack_message(self, delivery_tag: int, requeue: bool = True):
        """Rechaza un mensaje y opcionalmente lo reencola"""
        try:
            self.channel.basic_nack(delivery_tag=delivery_tag, requeue=requeue)
            logger.debug(f"Mensaje rechazado: {delivery_tag}")
        except Exception as e:
            logger.error(f"Error al rechazar mensaje: {e}")
    
    def get_queue_info(self) -> Optional[Dict]:
        """Obtiene información sobre la cola"""
        try:
            if not self.connection or self.connection.is_closed:
                self._connect()
            
            method_frame = self.channel.queue_declare(
                queue=self.queue_name,
                passive=True
            )
            
            return {
                'queue_name': method_frame.method.queue,
                'message_count': method_frame.method.message_count,
                'consumer_count': method_frame.method.consumer_count
            }
        except Exception as e:
            logger.error(f"Error al obtener información de la cola: {e}")
            return None
    
    def close(self):
        """Cierra la conexión con RabbitMQ"""
        try:
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()
            logger.info("Conexión a RabbitMQ cerrada")
        except Exception as e:
            logger.error(f"Error al cerrar conexión con RabbitMQ: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
