#!/usr/bin/env python3
"""
Script de prueba para verificar las correcciones implementadas
"""

import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_correcciones.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_correcciones():
    """Prueba las correcciones implementadas"""
    
    logger.info("🧪 PROBANDO CORRECCIONES IMPLEMENTADAS")
    logger.info("=" * 60)
    
    # Configurar Edge
    edge_options = Options()
    # edge_options.add_argument("--headless")  # Comentar para ver el navegador
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        # Crear driver
        driver = webdriver.Edge(options=edge_options)
        driver.set_page_load_timeout(30)
        
        # Simular datos del mensaje RabbitMQ
        datos_mensaje = {
            'IdFactura': 12345,
            'IdAseguradora': 67890,
            'NumDocIdentidad': '0102158896',
            'PersonaPrimerNombre': 'FABIAN',
            'PersonaSegundoNombre': 'MAURICIO',
            'PersonaPrimerApellido': 'BELTRAN',
            'PersonaSegundoApellido': 'NARVAEZ'
        }
        
        logger.info("📋 DATOS DEL MENSAJE RABBITMQ:")
        for campo, valor in datos_mensaje.items():
            logger.info(f"   • {campo}: '{valor}'")
        
        # PASO 1: Construir nombre completo
        logger.info("=" * 60)
        logger.info("🔍 PASO 1: Construyendo nombre completo del cliente...")
        
        nombre_completo = construir_nombre_completo(datos_mensaje)
        logger.info(f"✅ Nombre completo construido: '{nombre_completo}'")
        
        # PASO 2: Navegar directamente a la página de búsqueda
        logger.info("=" * 60)
        logger.info("🔍 PASO 2: Navegando directamente a página de búsqueda...")
        
        url_busqueda = "https://benefitsdirect.palig.com/Inicio/Contenido/InfoAsegurado/MisPolizasPVR.aspx"
        logger.info(f"🌐 Navegando a: {url_busqueda}")
        driver.get(url_busqueda)
        
        # Esperar a que cargue la página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("✅ Página de búsqueda cargada")
        
        # PASO 3: Probar la lógica de reintento
        logger.info("=" * 60)
        logger.info("🔍 PASO 3: Probando lógica de reintento...")
        
        # Simular búsqueda de elemento con reintento
        selector_campo = 'input[name="ctl00$ContenidoPrincipal$CtrlBuscaAseguradoProv$txtIdentificacionAseg"]'
        selector_boton = 'a[id="ContenidoPrincipal_CtrlBuscaAseguradoProv_lnkBuscar"]'
        
        try:
            # Buscar campo con reintento
            logger.info("🔍 Buscando campo de identificación...")
            campo = buscar_elemento_con_reintento(driver, selector_campo, "Campo de Identificación")
            
            if campo:
                logger.info("✅ Campo encontrado - Llenando con datos...")
                campo.clear()
                campo.send_keys(datos_mensaje['NumDocIdentidad'])
                logger.info(f"✅ Campo llenado con: {datos_mensaje['NumDocIdentidad']}")
                
                # Buscar botón con reintento
                logger.info("🔍 Buscando botón de búsqueda...")
                boton = buscar_boton_con_reintento(driver, selector_boton, "Botón de Búsqueda")
                
                if boton:
                    logger.info("✅ Botón encontrado - Haciendo clic...")
                    boton.click()
                    logger.info("✅ Click ejecutado")
                    
                    # Esperar resultados
                    time.sleep(5)
                    logger.info("✅ Búsqueda completada")
                else:
                    logger.error("❌ Botón no encontrado")
            else:
                logger.error("❌ Campo no encontrado")
                
        except Exception as e:
            logger.error(f"❌ Error en prueba: {e}")
        
        # Resumen final
        logger.info("=" * 60)
        logger.info("🎯 RESUMEN DE LA PRUEBA:")
        logger.info(f"   📍 URL final: {driver.current_url}")
        logger.info(f"   📄 Título final: {driver.title}")
        logger.info("✅ Prueba completada")
        
    except Exception as e:
        logger.error(f"❌ Error en prueba: {e}")
        logger.error(f"   📍 Error tipo: {type(e).__name__}")
        
    finally:
        if driver:
            logger.info("🔌 Cerrando navegador...")
            driver.quit()

def construir_nombre_completo(datos_mensaje):
    """Construye el nombre completo del cliente"""
    primer_nombre = datos_mensaje.get('PersonaPrimerNombre', '').strip()
    segundo_nombre = datos_mensaje.get('PersonaSegundoNombre', '').strip()
    primer_apellido = datos_mensaje.get('PersonaPrimerApellido', '').strip()
    segundo_apellido = datos_mensaje.get('PersonaSegundoApellido', '').strip()
    
    nombre_completo = f"{primer_nombre} {segundo_nombre} {primer_apellido} {segundo_apellido}".strip()
    return nombre_completo

def buscar_elemento_con_reintento(driver, selector, nombre_campo, max_reintentos=2):
    """Busca un elemento con reintento de recarga de página si no se encuentra"""
    for intento in range(1, max_reintentos + 1):
        try:
            logger.info(f"🔍 Buscando elemento '{nombre_campo}' (intento {intento}/{max_reintentos})...")
            logger.info(f"   📍 Selector: {selector}")
            
            # Intentar encontrar el elemento
            elemento = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            logger.info(f"✅ Elemento '{nombre_campo}' encontrado en intento {intento}")
            return elemento
            
        except Exception as e:
            logger.warning(f"⚠️ Elemento '{nombre_campo}' no encontrado en intento {intento}")
            logger.warning(f"   📍 Error: {e}")
            
            if intento < max_reintentos:
                logger.info(f"🔄 Recargando página para intento {intento + 1}...")
                logger.info(f"   📍 URL actual: {driver.current_url}")
                
                # Recargar la página
                driver.refresh()
                time.sleep(3)  # Esperar a que se recargue
                
                logger.info(f"✅ Página recargada - URL: {driver.current_url}")
            else:
                logger.error(f"❌ Elemento '{nombre_campo}' no encontrado después de {max_reintentos} intentos")
                return None
    
    return None

def buscar_boton_con_reintento(driver, selector, nombre_campo, max_reintentos=2):
    """Busca un botón con reintento de recarga de página si no se encuentra"""
    for intento in range(1, max_reintentos + 1):
        try:
            logger.info(f"🔍 Buscando botón '{nombre_campo}' (intento {intento}/{max_reintentos})...")
            logger.info(f"   📍 Selector: {selector}")
            
            # Intentar encontrar el botón
            boton = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            logger.info(f"✅ Botón '{nombre_campo}' encontrado en intento {intento}")
            return boton
            
        except Exception as e:
            logger.warning(f"⚠️ Botón '{nombre_campo}' no encontrado en intento {intento}")
            logger.warning(f"   📍 Error: {e}")
            
            if intento < max_reintentos:
                logger.info(f"🔄 Recargando página para intento {intento + 1}...")
                logger.info(f"   📍 URL actual: {driver.current_url}")
                
                # Recargar la página
                driver.refresh()
                time.sleep(3)  # Esperar a que se recargue
                
                logger.info(f"✅ Página recargada - URL: {driver.current_url}")
            else:
                logger.error(f"❌ Botón '{nombre_campo}' no encontrado después de {max_reintentos} intentos")
                return None
    
    return None

if __name__ == "__main__":
    test_correcciones()
