import json
import logging
import time
from typing import Dict, Any
from .rabbitmq_client import RabbitMQClient
from .database import DatabaseManager
from .scraper import WebScraper
from .config import Config

logger = logging.getLogger(__name__)

class ScrapingWorker:
    """Worker principal que coordina el scraping, RabbitMQ y SQL Server"""
    
    def __init__(self):
        self.rabbitmq_client = None
        self.database_manager = None
        self.scraper = None
        self.is_running = False
        
        # Configurar logging
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def initialize(self):
        """Inicializa todas las conexiones y componentes"""
        try:
            logger.info("Inicializando ScrapingWorker...")
            
            # Inicializar conexiones
            self.rabbitmq_client = RabbitMQClient()
            self.database_manager = DatabaseManager()
            self.scraper = WebScraper()
            
            # Probar conexiones
            if not self.database_manager.test_connection():
                raise Exception("No se pudo conectar a la base de datos")
            
            # Crear tabla para almacenar resultados si no existe
            self._create_scraping_table()
            
            logger.info("ScrapingWorker inicializado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al inicializar ScrapingWorker: {e}")
            return False
    
    def _create_scraping_table(self):
        """Crea la tabla para almacenar los resultados del scraping"""
        table_columns = {
            'id': 'INT IDENTITY(1,1) PRIMARY KEY',
            'url': 'NVARCHAR(500) NOT NULL',
            'title': 'NVARCHAR(500)',
            'content': 'NVARCHAR(MAX)',
            'status_code': 'INT',
            'error_message': 'NVARCHAR(1000)',
            'selenium_used': 'BIT DEFAULT 0',
            'timestamp': 'DATETIME2 DEFAULT GETDATE()',
            'processing_time': 'FLOAT',
            'extracted_data': 'NVARCHAR(MAX)'  # JSON con datos extraídos
        }
        
        self.database_manager.create_table_if_not_exists('scraping_results', table_columns)
    
    def process_message(self, ch, method, properties, body):
        """Procesa un mensaje recibido de RabbitMQ"""
        start_time = time.time()
        
        try:
            # Decodificar mensaje
            message = json.loads(body.decode('utf-8'))
            logger.info(f"Procesando mensaje: {message.get('url', 'N/A')}")
            
            # Extraer parámetros del mensaje
            url = message.get('url')
            use_selenium = message.get('use_selenium', False)
            selectors = message.get('selectors', {})
            
            if not url:
                logger.error("URL no proporcionada en el mensaje")
                self.rabbitmq_client.nack_message(method.delivery_tag)
                return
            
            # Realizar scraping
            scraped_data = self.scraper.scrape_url(url, use_selenium, selectors)
            
            # Calcular tiempo de procesamiento
            processing_time = time.time() - start_time
            scraped_data['processing_time'] = processing_time
            
            # Guardar en base de datos
            self._save_scraping_result(scraped_data)
            
            # Confirmar mensaje
            self.rabbitmq_client.ack_message(method.delivery_tag)
            
            logger.info(f"Procesamiento completado para {url} en {processing_time:.2f}s")
            
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar mensaje JSON: {e}")
            self.rabbitmq_client.nack_message(method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error al procesar mensaje: {e}")
            self.rabbitmq_client.nack_message(method.delivery_tag, requeue=True)
    
    def _save_scraping_result(self, scraped_data: Dict[str, Any]):
        """Guarda el resultado del scraping en la base de datos"""
        try:
            # Preparar datos para inserción
            db_data = {
                'url': scraped_data.get('url', ''),
                'title': scraped_data.get('title', ''),
                'content': scraped_data.get('content', ''),
                'status_code': scraped_data.get('status_code'),
                'error_message': scraped_data.get('error', ''),
                'selenium_used': 1 if scraped_data.get('selenium_used', False) else 0,
                'processing_time': scraped_data.get('processing_time', 0),
                'extracted_data': json.dumps(scraped_data, ensure_ascii=False)
            }
            
            # Insertar en base de datos
            success = self.database_manager.insert_data('scraping_results', db_data)
            
            if success:
                logger.info(f"Datos guardados exitosamente para: {scraped_data.get('url', 'N/A')}")
            else:
                logger.error(f"Error al guardar datos para: {scraped_data.get('url', 'N/A')}")
                
        except Exception as e:
            logger.error(f"Error al guardar resultado en base de datos: {e}")
    
    def start_consuming(self):
        """Inicia el consumo de mensajes de RabbitMQ"""
        try:
            logger.info("Iniciando consumo de mensajes...")
            self.is_running = True
            
            # Configurar callback y comenzar consumo
            self.rabbitmq_client.consume_messages(
                callback=self.process_message,
                auto_ack=False
            )
            
        except KeyboardInterrupt:
            logger.info("Detención solicitada por el usuario")
        except Exception as e:
            logger.error(f"Error durante el consumo de mensajes: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Detiene el worker y cierra todas las conexiones"""
        logger.info("Deteniendo ScrapingWorker...")
        self.is_running = False
        
        try:
            if self.rabbitmq_client:
                self.rabbitmq_client.close()
            
            if self.database_manager:
                self.database_manager.close()
            
            if self.scraper:
                self.scraper.close()
                
            logger.info("ScrapingWorker detenido correctamente")
            
        except Exception as e:
            logger.error(f"Error al detener ScrapingWorker: {e}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Obtiene el estado de la cola de RabbitMQ"""
        try:
            queue_info = self.rabbitmq_client.get_queue_info()
            return {
                'queue_name': queue_info.get('queue_name', ''),
                'message_count': queue_info.get('message_count', 0),
                'consumer_count': queue_info.get('consumer_count', 0),
                'worker_running': self.is_running
            }
        except Exception as e:
            logger.error(f"Error al obtener estado de la cola: {e}")
            return {
                'error': str(e),
                'worker_running': self.is_running
            }
    
    def publish_scraping_task(self, url: str, use_selenium: bool = False, selectors: Dict[str, str] = None):
        """Publica una tarea de scraping en RabbitMQ"""
        try:
            message = {
                'url': url,
                'use_selenium': use_selenium,
                'selectors': selectors or {},
                'timestamp': time.time()
            }
            
            success = self.rabbitmq_client.publish_message(message)
            
            if success:
                logger.info(f"Tarea de scraping publicada para: {url}")
            else:
                logger.error(f"Error al publicar tarea de scraping para: {url}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error al publicar tarea de scraping: {e}")
            return False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
