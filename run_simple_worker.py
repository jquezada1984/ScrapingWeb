#!/usr/bin/env python3
"""
Worker simplificado para procesar mensajes sin Selenium (solo para verificar conexión)
"""
import time
import logging
import json
import pika
import os
from datetime import datetime
from src.config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleWorker:
    def __init__(self):
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        
    def conectar_rabbitmq(self):
        """Conecta a RabbitMQ con credenciales"""
        try:
            logger.info("🔗 Conectando a RabbitMQ...")
            credentials = pika.PlainCredentials(Config.RABBITMQ_USERNAME, Config.RABBITMQ_PASSWORD)
            self.rabbitmq_connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=Config.RABBITMQ_HOST,
                    port=Config.RABBITMQ_PORT,
                    virtual_host='/',
                    credentials=credentials
                )
            )
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            
            # Declarar cola
            self.rabbitmq_channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True)
            
            # Declarar exchange
            self.rabbitmq_channel.exchange_declare(
                exchange=Config.RABBITMQ_EXCHANGE, 
                exchange_type='direct', 
                durable=True
            )
            
            # Bind cola al exchange
            self.rabbitmq_channel.queue_bind(
                exchange=Config.RABBITMQ_EXCHANGE,
                queue=Config.RABBITMQ_QUEUE,
                routing_key=Config.RABBITMQ_ROUTING_KEY
            )
            
            logger.info("✅ Conectado a RabbitMQ exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando a RabbitMQ: {e}")
            return False
    
    def procesar_mensaje(self, mensaje):
        """Procesa un mensaje simple"""
        try:
            logger.info("📨 MENSAJE RECIBIDO:")
            logger.info(f"   • Tipo: {type(mensaje)}")
            logger.info(f"   • Claves: {list(mensaje.keys()) if isinstance(mensaje, dict) else 'No es dict'}")
            
            if 'Clientes' in mensaje:
                total_clientes = len(mensaje['Clientes'])
                logger.info(f"   • Total clientes: {total_clientes}")
                
                if mensaje['Clientes']:
                    primer_cliente = mensaje['Clientes'][0]
                    logger.info(f"   • Primer cliente: {primer_cliente.get('NombreCompleto', 'Sin nombre')}")
            
            logger.info("✅ Mensaje procesado exitosamente (sin Selenium)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            return False
    
    def iniciar_procesamiento(self):
        """Inicia el procesamiento de mensajes"""
        logger.info("📨 Iniciando procesamiento de mensajes...")
        
        # Configurar el prefetch_count para procesar un mensaje a la vez
        self.rabbitmq_channel.basic_qos(prefetch_count=1)
        
        # Definir el callback para procesar mensajes
        def callback(ch, method, properties, body):
            logger.info(f"📨 Mensaje recibido: {method.delivery_tag}")
            try:
                mensaje = json.loads(body.decode('utf-8'))
                if self.procesar_mensaje(mensaje):
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"✅ Mensaje {method.delivery_tag} procesado y confirmado")
                else:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    logger.error(f"❌ Mensaje {method.delivery_tag} rechazado")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error decodificando JSON: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except Exception as e:
                logger.error(f"❌ Error general: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.rabbitmq_channel.basic_consume(
            queue=Config.RABBITMQ_QUEUE,
            on_message_callback=callback
        )
        
        logger.info("⏳ Esperando mensajes...")
        logger.info("🔄 Worker simplificado - solo recibe y procesa mensajes")
        
        # Procesar mensajes disponibles
        mensajes_procesados = 0
        
        while True:
            try:
                # Obtener un mensaje de la cola (no bloqueante)
                method, properties, body = self.rabbitmq_channel.basic_get(queue=Config.RABBITMQ_QUEUE)
                
                if method is None:
                    # No hay más mensajes en la cola
                    if mensajes_procesados > 0:
                        logger.info(f"📊 RESUMEN: {mensajes_procesados} mensajes procesados")
                        logger.info("🛑 Worker completó el procesamiento de todos los mensajes disponibles")
                        logger.info("⏳ Esperando nuevos mensajes...")
                    else:
                        logger.info("📭 No hay mensajes en la cola, esperando...")
                    
                    # Esperar nuevos mensajes (modo bloqueante)
                    self.rabbitmq_channel.start_consuming()
                    break
                
                # Hay un mensaje, procesarlo
                mensajes_procesados += 1
                logger.info(f"📨 PROCESANDO MENSAJE {mensajes_procesados}...")
                
                # Procesar el mensaje
                mensaje = json.loads(body.decode('utf-8'))
                if self.procesar_mensaje(mensaje):
                    # Confirmar que el mensaje fue procesado exitosamente
                    self.rabbitmq_channel.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"✅ Mensaje {mensajes_procesados} procesado y confirmado")
                else:
                    # Rechazar el mensaje si hubo error
                    self.rabbitmq_channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    logger.error(f"❌ Mensaje {mensajes_procesados} rechazado")
                    
            except KeyboardInterrupt:
                logger.info("⏹️ Deteniendo worker...")
                break
            except Exception as e:
                logger.error(f"❌ Error procesando mensaje: {e}")
                time.sleep(5)
    
    def cerrar_conexiones(self):
        """Cierra las conexiones"""
        try:
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                self.rabbitmq_connection.close()
                logger.info("✅ Conexiones cerradas")
        except Exception as e:
            logger.error(f"❌ Error cerrando conexiones: {e}")

def main():
    """Función principal"""
    logger.info("🚀 Iniciando worker simplificado...")
    
    # Validar configuración
    errores = Config.validar_configuracion()
    if errores:
        logger.error("❌ Errores en la configuración:")
        for error in errores:
            logger.error(f"   • {error}")
        return
    
    worker = SimpleWorker()
    
    try:
        # Conectar a RabbitMQ
        if not worker.conectar_rabbitmq():
            logger.error("❌ No se pudo conectar a RabbitMQ")
            return
        
        # Iniciar procesamiento
        worker.iniciar_procesamiento()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Deteniendo worker por interrupción del usuario...")
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
    finally:
        worker.cerrar_conexiones()

if __name__ == "__main__":
    main()
