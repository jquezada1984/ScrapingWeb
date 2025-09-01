#!/usr/bin/env python3
"""
Worker de producción para procesar mensajes de aseguradoras continuamente
"""

import time
import logging
import signal
import sys
from datetime import datetime
from process_aseguradora_messages import AseguradoraProcessor

# Configurar logging más detallado para producción
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('production_worker.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class ProductionWorker:
    def __init__(self):
        self.processor = None
        self.running = False
        self.start_time = None
        self.message_count = 0
        
        # Configurar señales para shutdown graceful
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Maneja señales de interrupción"""
        logger.info(f"📡 Señal recibida: {signum}")
        self.shutdown()
    
    def startup(self):
        """Inicia el worker"""
        try:
            logger.info("🚀 Iniciando Worker de Producción...")
            logger.info("=" * 60)
            logger.info("📋 Configuración del Sistema:")
            logger.info("   • RabbitMQ: aseguradora_queue")
            logger.info("   • Base de Datos: SQL Server")
            logger.info("   • Caché: URLs de aseguradoras")
            logger.info("   • Logs: Archivo + Consola")
            logger.info("   • Modo: SIEMPRE ACTIVO - Esperando mensajes")
            logger.info("=" * 60)
            
            self.start_time = datetime.now()
            self.running = True
            
            # Crear procesador
            self.processor = AseguradoraProcessor()
            
            # Mostrar estadísticas iniciales
            self.show_status()
            
            logger.info("🔄 Iniciando procesador de mensajes...")
            logger.info("⏳ Worker en modo PRODUCCIÓN - Siempre activo")
            logger.info("💡 Presiona Ctrl+C para detener")
            logger.info("=" * 60)
            
            # Iniciar consumo de mensajes (SIEMPRE ACTIVO)
            self.processor.start_consuming()
            
        except Exception as e:
            logger.error(f"❌ Error en startup: {e}")
            self.shutdown()
    
    def show_status(self):
        """Muestra el estado actual del worker"""
        if self.start_time:
            uptime = datetime.now() - self.start_time
            logger.info(f"📊 Estado del Worker:")
            logger.info(f"   • Tiempo activo: {uptime}")
            logger.info(f"   • Mensajes procesados: {self.message_count}")
            logger.info(f"   • Estado: {'🟢 Activo' if self.running else '🔴 Detenido'}")
    
    def shutdown(self):
        """Detiene el worker de forma graceful"""
        logger.info("⏹️  Iniciando shutdown graceful...")
        self.running = False
        
        if self.processor:
            try:
                self.processor.cleanup()
            except Exception as e:
                logger.error(f"❌ Error en cleanup: {e}")
        
        logger.info("🔌 Worker detenido correctamente")
        sys.exit(0)

def main():
    """Función principal"""
    worker = ProductionWorker()
    
    try:
        worker.startup()
    except KeyboardInterrupt:
        logger.info("⏹️  Interrupción por teclado")
        worker.shutdown()
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        worker.shutdown()

if __name__ == "__main__":
    main()
