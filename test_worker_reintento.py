#!/usr/bin/env python3
"""
Script de prueba para verificar la lógica de reintento de login en el worker principal
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
        logging.FileHandler('test_worker_reintento.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_worker_reintento():
    """Prueba la lógica de reintento de login del worker principal"""
    
    # Configurar Edge
    edge_options = Options()
    # edge_options.add_argument("--headless")  # Comentar para ver el navegador
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        logger.info("🚀 INICIANDO PRUEBA DE REINTENTO DE LOGIN DEL WORKER")
        logger.info("=" * 60)
        
        # Crear driver
        driver = webdriver.Edge(options=edge_options)
        driver.set_page_load_timeout(30)
        
        # Simular la configuración del worker
        url_info = {
            'nombre': 'PAN AMERICAN LIFE DE ECUADOR',
            'campos_login': [
                {'selector_html': '#username', 'valor_dinamico': 'conveniosyseguros@mediglobal.com.ec'},
                {'selector_html': '#password', 'valor_dinamico': 'Mediglobal1'}
            ],
            'acciones_post_login': [
                {'tipo_accion': 'click', 'selector_html': 'a[title="Inicio de sesión"]'}
            ]
        }
        
        # Variable para controlar reintentos de login
        intentos_login = 0
        max_intentos_login = 2
        
        # URL de login
        url_login = "https://attest.palig.com/as/authorization.oauth2?client_id=cf7770f3699048ca9c61358b4dff25f5&redirect_uri=https%3A%2F%2Fbenefitsdirect.palig.com%2FInicio%2FLogin.aspx&response_type=code%20id_token&scope=openid%20profile%20email%20phone&state=OpenIdConnect.AuthenticationProperties%3DEXT82eDzm70H4FnxSn_OSRdC0ztASLp7Bvg8yLL52IEtIBpUyjD0IgIAK2j3eotEFyvMduisG7lsrN_jS47FwqP1Ye8RmSvSCWGJztHD53DbYlBg6Si-9zzt_8Efapm7-7fpkkxkUMhcPLmiLc54y6uQoA-d6uJ9jwBtbN00C1RguGixAAIRtMHyLWPVpBEQPpVPzS-6duAbBzUrsj9DrHDwEUlLYKM_XwLKtTN2C3kFXgQ6w5TVEjc7erJO16I1mxb4sAur-MV7SQAJNVbSg0smGa8JTlVV37t3I2zgvVeE1c44Hp4R72C9ivX23Ai0&response_mode=form_post&nonce=638918216386869899.ODZmNTA2ZDQtZDIwZi00MTE0LTk1NjItMjI0YWFlYzMyNzQ4MGE5YjVhOTgtMzNjNS00NDBmLTllMjAtYzg0NDY2MDkwNDc5&x-client-SKU=ID_NET451&x-client-ver=5.6.0.0"
        
        logger.info(f"🌐 Navegando a: {url_login}")
        driver.get(url_login)
        
        # Esperar a que cargue la página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("✅ Página de login cargada")
        
        # Simular el proceso del worker: llenar campos y ejecutar acciones
        logger.info("🔐 Ejecutando campos de login...")
        for campo in url_info['campos_login']:
            selector = campo['selector_html']
            valor = campo['valor_dinamico']
            
            elemento = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            elemento.clear()
            elemento.send_keys(valor)
            logger.info(f"✅ Campo {selector} completado con: {valor}")
        
        logger.info("🎯 Ejecutando acciones post-login...")
        for accion in url_info['acciones_post_login']:
            tipo = accion['tipo_accion']
            selector = accion['selector_html']
            
            elemento = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            if tipo.lower() == 'click':
                elemento.click()
                logger.info(f"✅ Click ejecutado en: {selector}")
        
        # Esperar a que se procese
        time.sleep(2)
        
        # Simular el bucle de espera OAuth2 del worker
        logger.info("⏳ Esperando redirección OAuth2...")
        url_anterior = driver.current_url
        
        for intento in range(1, 21):  # 20 intentos para la prueba
            time.sleep(3)
            
            url_actual = driver.current_url
            titulo_actual = driver.title
            
            # Verificar si la URL cambió
            if url_actual != url_anterior:
                logger.info(f"🔄 CAMBIO DE URL DETECTADO en intento {intento}/20")
                logger.info(f"   📍 URL anterior: {url_anterior}")
                logger.info(f"   📍 URL actual: {url_actual}")
                logger.info(f"   📄 Título: {titulo_actual}")
                url_anterior = url_actual
            else:
                logger.info(f"   ⏳ Intento {intento}/20 - URL: {url_actual[:80]}...")
                logger.info(f"      Título: {titulo_actual}")
            
            # 🔍 DETECTAR SI VOLVIMOS AL LOGIN Y REINTENTAR (lógica del worker)
            if "authorization.oauth2" in url_actual and intentos_login < max_intentos_login:
                intentos_login += 1
                logger.warning(f"🔄 ¡VOLVIMOS AL LOGIN! (Intento {intentos_login}/{max_intentos_login})")
                logger.info("🔄 Reintentando login automáticamente...")
                
                try:
                    # Esperar a que se recargue la página
                    time.sleep(2)
                    
                    # Reintentar campos de login
                    logger.info("🔐 Reintentando login - llenando campos...")
                    for campo in url_info['campos_login']:
                        selector = campo['selector_html']
                        valor = campo['valor_dinamico']
                        
                        elemento = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        elemento.clear()
                        elemento.send_keys(valor)
                        logger.info(f"✅ Campo {selector} completado (reintento)")
                    
                    # Reintentar acciones post-login
                    logger.info("🎯 Reintentando acciones post-login...")
                    for accion in url_info['acciones_post_login']:
                        tipo = accion['tipo_accion']
                        selector = accion['selector_html']
                        
                        elemento = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        
                        if tipo.lower() == 'click':
                            elemento.click()
                            logger.info(f"✅ Click ejecutado (reintento) en: {selector}")
                        
                        time.sleep(2)
                    
                    logger.info("✅ Reintento de login completado, continuando...")
                    
                except Exception as e:
                    logger.error(f"❌ Error en reintento de login: {e}")
                    if intentos_login >= max_intentos_login:
                        logger.error("❌ Máximo de reintentos de login alcanzado")
                        break
                
                # Continuar con el siguiente intento
                continue
            
            # Verificar si llegamos a la página final
            if "benefitsdirect.palig.com" in url_actual:
                logger.info(f"✅ ¡Redirección detectada en intento {intento}!")
                logger.info(f"   🎯 Página alcanzada: {url_actual}")
                break
        
        # Resumen final
        url_final = driver.current_url
        titulo_final = driver.title
        
        logger.info("=" * 60)
        logger.info("🎯 PRUEBA DE REINTENTO COMPLETADA")
        logger.info(f"📊 Resumen de reintentos de login: {intentos_login}/{max_intentos_login}")
        logger.info(f"📍 URL final: {url_final}")
        logger.info(f"📄 Título final: {titulo_final}")
        
        if "benefitsdirect.palig.com" in url_final:
            logger.info("✅ ¡ÉXITO! Página de beneficios alcanzada")
        else:
            logger.warning("⚠️ No se llegó a la página de beneficios esperada")
        
    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        
    finally:
        if driver:
            logger.info("🔌 Cerrando navegador...")
            driver.quit()

if __name__ == "__main__":
    test_worker_reintento()
