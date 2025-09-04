#!/usr/bin/env python3
"""
Script de prueba para verificar las mejoras en el manejo de OAuth2
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
        logging.FileHandler('test_mejoras_oauth2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_mejoras_oauth2():
    """Prueba las mejoras en el manejo de OAuth2"""
    
    logger.info("🧪 PROBANDO MEJORAS EN MANEJO DE OAUTH2")
    logger.info("=" * 60)
    
    # Configurar Edge
    edge_options = Options()
    # edge_options.add_argument("--headless")  # Comentar para ver el navegador
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--window-size=1920,1080")
    edge_options.add_argument("--disable-blink-features=AutomationControlled")
    edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    edge_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        # Crear driver
        driver = webdriver.Edge(options=edge_options)
        driver.set_page_load_timeout(30)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("✅ Driver de Edge configurado correctamente")
        
        # PASO 1: Navegar a la página de login
        logger.info("=" * 60)
        logger.info("🔍 PASO 1: Navegando a página de login...")
        
        url_login = "https://attest.palig.com/as/authorization.oauth2?client_id=cf7770f3699048ca9c61358b4dff25f5&redirect_uri=https%3A%2F%2Fbenefitsdirect.palig.com%2FInicio%2FLogin.aspx&response_type=code%20id_token&scope=openid%20profile%20email%20phone&state=OpenIdConnect.AuthenticationProperties%3DEXT82eDzm70H4FnxSn_OSRdC0ztASLp7Bvg8yLL52IEtIBpUyjD0IgIAK2j3eotEFyvMduisG7lsrN_jS47FwqP1Ye8RmSvSCWGJztHD53DbYlBg6Si-9zzt_8Efapm7-7fpkkxkUMhcPLmiLc54y6uQoA-d6uJ9jwBtbN00C1RguGixAAIRtMHyLWPVpBEQPpVPzS-6duAbBzUrsj9DrHDwEUlLYKM_XwLKtTN2C3kFXgQ6w5TVEjc7erJO16I1mxb4sAur-MV7SQAJNVbSg0smGa8JTlVV37t3I2zgvVeE1c44Hp4R72C9ivX23Ai0&response_mode=form_post&nonce=638918216386869899.ODZmNTA2ZDQtZDIwZi00MTE0LTk1NjItMjI0YWFlYzMyNzQ4MGE5YjVhOTgtMzNjNS00NDBmLTllMjAtYzg0NDY2MDkwNDc5&x-client-SKU=ID_NET451&x-client-ver=5.6.0.0"
        
        logger.info(f"🌐 Navegando a: {url_login}")
        driver.get(url_login)
        
        # Esperar a que cargue la página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("✅ Página de login cargada")
        
        # PASO 2: Llenar campos de login
        logger.info("=" * 60)
        logger.info("🔍 PASO 2: Llenando campos de login...")
        
        # Usuario
        usuario = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#username'))
        )
        usuario.clear()
        usuario.send_keys('conveniosyseguros@mediglobal.com.ec')
        logger.info("✅ Usuario ingresado")
        
        # Contraseña
        password = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#password'))
        )
        password.clear()
        password.send_keys('Mediglobal1')
        logger.info("✅ Contraseña ingresada")
        
        # Click en login
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Inicio de sesión"]'))
        )
        login_btn.click()
        logger.info("✅ Click en botón de login ejecutado")
        
        # PASO 3: Esperar redirección OAuth2 con mejoras
        logger.info("=" * 60)
        logger.info("🔍 PASO 3: Esperando redirección OAuth2 con mejoras...")
        
        url_anterior = driver.current_url
        logger.info(f"📍 URL inicial: {url_anterior}")
        
        # Variables para control de timeout
        timeout_authorization_ping = 30  # 30 segundos máximo en authorization.ping
        tiempo_inicio_ping = None
        
        for intento in range(1, 41):  # 40 intentos = 120 segundos
            time.sleep(3)
            
            url_actual = driver.current_url
            titulo_actual = driver.title
            
            if url_actual != url_anterior:
                logger.info(f"🔄 CAMBIO DE URL DETECTADO en intento {intento}/40")
                logger.info(f"   📍 URL anterior: {url_anterior}")
                logger.info(f"   📍 URL actual: {url_actual}")
                logger.info(f"   📄 Título: {titulo_actual}")
                url_anterior = url_actual
            else:
                logger.info(f"   ⏳ Intento {intento}/40 - URL: {url_actual[:80]}...")
                logger.info(f"      Título: {titulo_actual}")
            
            # 🔍 DETECTAR PÁGINA DE AUTORIZACIÓN.PING Y MANEJARLA
            if "authorization.ping" in url_actual:
                # Iniciar timer si es la primera vez que detectamos esta página
                if tiempo_inicio_ping is None:
                    tiempo_inicio_ping = time.time()
                    logger.info(f"🔄 ESTADO INTERMEDIO OAUTH2 DETECTADO en intento {intento}")
                    logger.info(f"   📍 Página de autorización.ping: {url_actual}")
                    logger.info(f"   📄 Título de la página: {titulo_actual}")
                    logger.info(f"   ⏳ Esperando continuación del flujo OAuth2...")
                else:
                    # Verificar timeout
                    tiempo_transcurrido = time.time() - tiempo_inicio_ping
                    if tiempo_transcurrido > timeout_authorization_ping:
                        logger.warning(f"⚠️ TIMEOUT en página authorization.ping después de {timeout_authorization_ping} segundos")
                        logger.warning(f"   🔄 Recargando página para forzar continuación...")
                        
                        try:
                            driver.refresh()
                            time.sleep(5)
                            tiempo_inicio_ping = None  # Resetear timer
                            continue
                        except Exception as e:
                            logger.error(f"❌ Error recargando página: {e}")
                            break
                
                # Buscar elementos para continuar el flujo
                logger.info(f"   🔍 Buscando elementos para continuar el flujo...")
                try:
                    # Buscar botones o enlaces para continuar
                    elementos_continuar = driver.find_elements(By.CSS_SELECTOR, 
                        'input[type="submit"], button, a, input[value*="continuar"], input[value*="siguiente"]')
                    
                    if elementos_continuar:
                        logger.info(f"   ✅ Encontrados {len(elementos_continuar)} elementos para continuar")
                        for i, elem in enumerate(elementos_continuar):
                            try:
                                texto = elem.text or elem.get_attribute('value') or elem.get_attribute('title') or 'sin-texto'
                                logger.info(f"      {i+1}. {elem.tag_name} - Texto: '{texto}'")
                                
                                # Intentar hacer clic en el primer elemento clickeable
                                if elem.is_enabled() and elem.is_displayed():
                                    logger.info(f"   🎯 Haciendo clic en elemento {i+1} para continuar...")
                                    elem.click()
                                    logger.info(f"   ✅ Click ejecutado, esperando continuación...")
                                    time.sleep(2)
                                    tiempo_inicio_ping = None  # Resetear timer después del click
                                    break
                            except Exception as e:
                                logger.warning(f"   ⚠️ No se pudo hacer clic en elemento {i+1}: {e}")
                    else:
                        logger.info(f"   ℹ️ No se encontraron elementos clickeables en la página de autorización.ping")
                        
                except Exception as e:
                    logger.warning(f"   ⚠️ Error buscando elementos de continuación: {e}")
                
                # Continuar esperando
                continue
            
            # Verificar si llegamos a la página final
            if "benefitsdirect.palig.com" in url_actual:
                logger.info(f"✅ ¡Redirección detectada en intento {intento}!")
                logger.info(f"   🎯 Página alcanzada: {url_actual}")
                break
        
        # Resumen final
        logger.info("=" * 60)
        logger.info("🎯 RESUMEN DE LA PRUEBA:")
        logger.info(f"   📍 URL final: {driver.current_url}")
        logger.info(f"   📄 Título final: {driver.title}")
        
        if "benefitsdirect.palig.com" in driver.current_url:
            logger.info("✅ ¡ÉXITO! Página de beneficios alcanzada")
        else:
            logger.warning("⚠️ No se llegó a la página de beneficios esperada")
        
        logger.info("✅ Prueba completada")
        
    except Exception as e:
        logger.error(f"❌ Error en prueba: {e}")
        logger.error(f"   📍 Error tipo: {type(e).__name__}")
        
    finally:
        if driver:
            logger.info("🔌 Cerrando navegador...")
            driver.quit()

if __name__ == "__main__":
    test_mejoras_oauth2()
