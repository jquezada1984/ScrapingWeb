#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de logging de URLs en el flujo OAuth2
"""

import logging
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_url_logging.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_url_logging():
    """Prueba el sistema de logging de URLs"""
    
    logger.info("🚀 INICIANDO PRUEBA DE LOGGING DE URLs")
    logger.info("=" * 60)
    
    try:
        # Configurar Edge
        edge_options = Options()
        edge_options.add_argument("--headless")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--window-size=1920,1080")
        
        # Crear driver
        driver = webdriver.Edge(options=edge_options)
        driver.set_page_load_timeout(30)
        
        logger.info("✅ Driver de Edge configurado correctamente")
        
        # Simular navegación y cambios de URL
        urls_test = [
            "https://www.google.com",
            "https://www.google.com/search?q=test",
            "https://www.google.com/search?q=selenium",
            "https://www.google.com/search?q=python"
        ]
        
        for i, url in enumerate(urls_test, 1):
            logger.info(f"🔄 NAVEGACIÓN {i}/4")
            logger.info(f"   📍 URL objetivo: {url}")
            logger.info(f"   📍 URL actual antes de navegación: {driver.current_url}")
            
            driver.get(url)
            time.sleep(2)
            
            url_despues = driver.current_url
            titulo = driver.title
            
            logger.info(f"   📍 URL después de navegación: {url_despues}")
            logger.info(f"   📄 Título: {titulo}")
            
            if url_despues != url:
                logger.info(f"   ⚠️ URL cambió durante la navegación")
                logger.info(f"      📍 URL esperada: {url}")
                logger.info(f"      📍 URL actual: {url_despues}")
            else:
                logger.info(f"   ✅ Navegación exitosa a URL objetivo")
            
            logger.info("-" * 40)
        
        # Simular detección de cambios de URL
        logger.info("🔄 SIMULANDO DETECCIÓN DE CAMBIOS DE URL")
        url_anterior = driver.current_url
        logger.info(f"📍 URL inicial: {url_anterior}")
        
        for intento in range(1, 6):
            time.sleep(1)
            url_actual = driver.current_url
            
            if url_actual != url_anterior:
                logger.info(f"🔄 CAMBIO DE URL DETECTADO en intento {intento}/5")
                logger.info(f"   📍 URL anterior: {url_anterior}")
                logger.info(f"   📍 URL actual: {url_actual}")
                url_anterior = url_actual
            else:
                logger.info(f"   ⏳ Intento {intento}/5 - URL: {url_actual[:50]}...")
        
        logger.info("✅ PRUEBA DE LOGGING DE URLs COMPLETADA EXITOSAMENTE")
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de logging: {e}")
    finally:
        try:
            driver.quit()
            logger.info("✅ Driver cerrado correctamente")
        except:
            pass

if __name__ == "__main__":
    test_url_logging()
