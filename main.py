#!/usr/bin/env python3
"""
Script principal para ejecutar el ScrapingWorker
"""

import sys
import signal
import logging
from src.scraping_worker import ScrapingWorker
from src.config import Config

def signal_handler(signum, frame):
    """Maneja las señales de interrupción"""
    print("\nDetención solicitada...")
    sys.exit(0)

def main():
    """Función principal"""
    # Configurar manejo de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraping_worker.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Iniciando ScrapingWorker...")
        
        # Crear y inicializar el worker
        worker = ScrapingWorker()
        
        if not worker.initialize():
            logger.error("No se pudo inicializar el ScrapingWorker")
            sys.exit(1)
        
        logger.info("ScrapingWorker inicializado correctamente")
        logger.info("Presiona Ctrl+C para detener el worker")
        
        # Iniciar consumo de mensajes
        worker.start_consuming()
        
    except Exception as e:
        logger.error(f"Error en la aplicación principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
