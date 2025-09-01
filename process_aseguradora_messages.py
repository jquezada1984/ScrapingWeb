#!/usr/bin/env python3
"""
Script para procesar mensajes de aseguradoras desde RabbitMQ
y buscar las URLs correspondientes en la base de datos
"""

import json
import pika
import logging
import time
from datetime import datetime
from src.config import Config
from src.database import DatabaseManager

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AseguradoraProcessor:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        # Cache para URLs de aseguradoras (nombre -> url_info)
        self.url_cache = {}
        logger.info("🚀 Procesador inicializado con caché de URLs")
    
    def connect_rabbitmq(self):
        """Conecta a RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(Config.RABBITMQ_USERNAME, Config.RABBITMQ_PASSWORD)
            self.rabbitmq_connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=Config.RABBITMQ_HOST,
                    port=Config.RABBITMQ_PORT,
                    credentials=credentials
                )
            )
            
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            
            # Declarar la cola y el exchange
            self.rabbitmq_channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True)
            self.rabbitmq_channel.exchange_declare(
                exchange=Config.RABBITMQ_EXCHANGE, 
                exchange_type='direct', 
                durable=True
            )
            
            # Vincular la cola al exchange
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
    
    def get_url_by_aseguradora_name(self, nombre_aseguradora):
        """Busca la URL de una aseguradora por su nombre en la base de datos o caché"""
        try:
            # Primero verificar si ya está en caché
            if nombre_aseguradora in self.url_cache:
                logger.info(f"📋 URL encontrada en caché para: {nombre_aseguradora}")
                return self.url_cache[nombre_aseguradora]
            
            # Si no está en caché, buscar en la base de datos
            logger.info(f"🔍 Buscando URL en base de datos para: {nombre_aseguradora}")
            query = """
                SELECT id, nombre, url_login, url_destino, descripcion, fecha_creacion
                FROM urls_automatizacion 
                WHERE nombre = :nombre
            """
            
            # Usar el método correcto de DatabaseManager con parámetros nombrados
            results = self.db_manager.execute_query(query, {'nombre': nombre_aseguradora})
            
            if results and len(results) > 0:
                row = results[0]
                url_info = {
                    'id': str(row['id']),
                    'nombre': row['nombre'],
                    'url_login': row['url_login'],
                    'url_destino': row['url_destino'],
                    'descripcion': row['descripcion'],
                    'fecha_creacion': row['fecha_creacion'].isoformat() if row['fecha_creacion'] else None
                }
                
                # Guardar en caché para futuras consultas
                self.url_cache[nombre_aseguradora] = url_info
                logger.info(f"💾 URL guardada en caché para: {nombre_aseguradora}")
                
                return url_info
            else:
                logger.warning(f"⚠️  No se encontró URL para {nombre_aseguradora}")
                return None
                    
        except Exception as e:
            logger.error(f"❌ Error buscando URL para {nombre_aseguradora}: {e}")
            return None
    
    def process_aseguradora_message(self, message_data):
        """Procesa un mensaje de aseguradora"""
        try:
            nombre_aseguradora = message_data.get('NombreCompleto')
            if not nombre_aseguradora:
                logger.warning("⚠️  Mensaje sin NombreCompleto")
                return None
            
            logger.info(f"🔍 Procesando aseguradora: {nombre_aseguradora}")
            
            # Buscar URL en la base de datos
            url_info = self.get_url_by_aseguradora_name(nombre_aseguradora)
            
            if url_info:
                # Crear resultado combinado
                result = {
                    'aseguradora_info': message_data,
                    'url_info': url_info,
                    'procesado_en': datetime.now().isoformat()
                }
                
                logger.info(f"✅ URL encontrada para {nombre_aseguradora}: {url_info['url_login']}")
                return result
            else:
                logger.warning(f"⚠️  No se encontró URL para {nombre_aseguradora}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            return None
    
    def process_message(self, ch, method, properties, body):
        """Callback para procesar mensajes de RabbitMQ"""
        try:
            # Decodificar el mensaje
            message_text = body.decode('utf-8')
            logger.info(f"📨 Procesando mensaje #{method.delivery_tag}")
            
            # Parsear JSON
            try:
                message_data = json.loads(message_text)
                
                # Verificar si es un mensaje de aseguradora
                if 'NombreCompleto' in message_data:
                    # Procesar mensaje individual
                    result = self.process_aseguradora_message(message_data)
                    if result:
                        logger.info("✅ Mensaje procesado exitosamente")
                        # Aquí podrías guardar el resultado en otra tabla o hacer algo más
                elif 'Clientes' in message_data and isinstance(message_data['Clientes'], list):
                    # Procesar lista de clientes
                    logger.info(f"📋 Procesando lista de {len(message_data['Clientes'])} clientes")
                    
                    for i, cliente in enumerate(message_data['Clientes']):
                        logger.info(f"  🔍 Procesando cliente {i+1}/{len(message_data['Clientes'])}")
                        result = self.process_aseguradora_message(cliente)
                        if result:
                            logger.info(f"    ✅ Cliente {i+1} procesado")
                        else:
                            logger.warning(f"    ⚠️  Cliente {i+1} sin procesar")
                else:
                    logger.warning("⚠️  Formato de mensaje no reconocido")
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error parseando JSON: {e}")
            
            # Acknowledge el mensaje
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self):
        """Inicia el consumo de mensajes - SIEMPRE ACTIVO"""
        try:
            if not self.connect_rabbitmq():
                return
            
            # Obtener información de la cola
            queue_info = self.rabbitmq_channel.queue_declare(
                queue=Config.RABBITMQ_QUEUE, 
                durable=True, 
                passive=True
            )
            message_count = queue_info.method.message_count
            consumer_count = queue_info.method.consumer_count
            
            logger.info(f"📊 Cola: {Config.RABBITMQ_QUEUE}")
            logger.info(f"📊 Exchange: {Config.RABBITMQ_EXCHANGE}")
            logger.info(f"📊 Routing Key: {Config.RABBITMQ_ROUTING_KEY}")
            logger.info(f"📈 Mensajes en cola: {message_count}")
            logger.info(f"👥 Consumidores activos: {consumer_count}")
            
            # Configurar QoS para procesar un mensaje a la vez
            self.rabbitmq_channel.basic_qos(prefetch_count=1)
            
            # Consumir mensajes - SIEMPRE ACTIVO
            logger.info("🔄 Iniciando consumo de mensajes...")
            logger.info("💡 Presiona Ctrl+C para detener")
            logger.info("⏳ Worker activo esperando mensajes...")
            
            # Configurar el consumidor para estar siempre activo
            self.rabbitmq_channel.basic_consume(
                queue=Config.RABBITMQ_QUEUE,
                on_message_callback=self.process_message,
                auto_ack=False  # Acknowledgment manual para mejor control
            )
            
            try:
                # BUCLE INFINITO - SIEMPRE ESPERANDO MENSAJES
                logger.info("🔄 Worker iniciado - Esperando mensajes...")
                
                # Usar start_consuming() que mantiene el worker activo
                self.rabbitmq_channel.start_consuming()
                        
            except KeyboardInterrupt:
                logger.info("⏹️  Deteniendo consumo de mensajes...")
                self.rabbitmq_channel.stop_consuming()
                
        except Exception as e:
            logger.error(f"❌ Error en el consumo: {e}")
        finally:
            self.cleanup()
    
    def get_cache_stats(self):
        """Retorna estadísticas del caché"""
        return {
            'total_cached': len(self.url_cache),
            'cached_aseguradoras': list(self.url_cache.keys())
        }
    
    def show_cache_stats(self):
        """Muestra estadísticas del caché"""
        stats = self.get_cache_stats()
        logger.info(f"📊 Estadísticas del caché:")
        logger.info(f"   Total en caché: {stats['total_cached']}")
        if stats['cached_aseguradoras']:
            logger.info(f"   Aseguradoras en caché: {', '.join(stats['cached_aseguradoras'])}")
        else:
            logger.info("   Caché vacío")
    
    def cleanup(self):
        """Limpia las conexiones"""
        try:
            # Mostrar estadísticas del caché antes de limpiar
            self.show_cache_stats()
            
            if self.rabbitmq_channel and not self.rabbitmq_channel.is_closed:
                self.rabbitmq_channel.close()
            
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                self.rabbitmq_connection.close()
                
            logger.info("🔌 Conexiones cerradas")
            
        except Exception as e:
            logger.error(f"❌ Error cerrando conexiones: {e}")

def main():
    """Función principal"""
    logger.info("🚀 Iniciando procesador de mensajes de aseguradoras...")
    
    processor = AseguradoraProcessor()
    
    try:
        processor.start_consuming()
    except Exception as e:
        logger.error(f"❌ Error en el procesador: {e}")
    finally:
        processor.cleanup()

if __name__ == "__main__":
    main()
