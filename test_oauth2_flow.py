#!/usr/bin/env python3
"""
Script de prueba para el flujo OAuth2 mejorado de PAN AMERICAN LIFE DE ECUADOR
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_oauth2_flow():
    """Prueba el flujo OAuth2 completo"""
    
    # Configurar Edge
    edge_options = Options()
    # edge_options.add_argument("--headless")  # Comentar para ver el navegador
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--window-size=1920,1080")
    edge_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
    
    driver = None
    try:
        logger.info("🚀 Iniciando prueba del flujo OAuth2...")
        
        # Crear driver
        driver = webdriver.Edge(options=edge_options)
        driver.set_page_load_timeout(30)
        
        # URL de login
        url_login = "https://attest.palig.com/as/authorization.oauth2?client_id=cf7770f3699048ca9c61358b4dff25f5&redirect_uri=https%3A%2F%2Fbenefitsdirect.palig.com%2FInicio%2FLogin.aspx&response_type=code%20id_token&scope=openid%20profile%20email%20phone&state=OpenIdConnect.AuthenticationProperties%3DEXT82eDzm70H4FnxSn_OSRdC0ztASLp7Bvg8yLL52IEtIBpUyjD0IgIAK2j3eotEFyvMduisG7lsrN_jS47FwqP1Ye8RmSvSCWGJztHD53DbYlBg6Si-9zzt_8Efapm7-7fpkkxkUMhcPLmiLc54y6uQoA-d6uJ9jwBtbN00C1RguGixAAIRtMHyLWPVpBEQPpVPzS-6duAbBzUrsj9DrHDwEUlLYKM_XwLKtTN2C3kFXgQ6w5TVEjc7erJO16I1mxb4sAur-MV7SQAJNVbSg0smGa8JTlVV37t3I2zgvVeE1c44Hp4R72C9ivX23Ai0&response_mode=form_post&nonce=638918216386869899.ODZmNTA2ZDQtZDIwZi00MTE0LTk1NjItMjI0YWFlYzMyNzQ4MGE5YjVhOTgtMzNjNS00NDBmLTllMjAtYzg0NDY2MDkwNDc5&x-client-SKU=ID_NET451&x-client-ver=5.6.0.0"
        
        logger.info(f"🌐 Navegando a: {url_login}")
        driver.get(url_login)
        
        # Esperar a que cargue la página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("✅ Página de login cargada")
        
        # Llenar campos de login
        logger.info("🔐 Llenando campos de login...")
        
        # Campo de contraseña
        campo_password = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#password"))
        )
        campo_password.clear()
        campo_password.send_keys("Mediglobal1")
        logger.info("✅ Campo contraseña completado")
        
        # Campo de usuario
        campo_username = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
        )
        campo_username.clear()
        campo_username.send_keys("conveniosyseguros@mediglobal.com.ec")
        logger.info("✅ Campo usuario completado")
        
        # Hacer clic en el botón de login
        boton_login = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Inicio de sesión"]'))
        )
        boton_login.click()
        logger.info("✅ Botón de login clickeado")
        
        # 🚀 ESPERAR A QUE SE COMPLETE LA REDIRECCIÓN OAUTH2
        logger.info("⏳ Esperando a que se complete la redirección OAuth2...")
        
        # Variable para controlar reintentos de login
        intentos_login = 0
        max_intentos_login = 2
        
        # Esperar hasta que llegue a la página final (máximo 120 segundos)
        for intento in range(1, 41):  # 40 intentos * 3 segundos = 120 segundos
            time.sleep(3)
            
            url_actual = driver.current_url
            titulo_actual = driver.title
            
            logger.info(f"   ⏳ Intento {intento}/40 - URL: {url_actual[:80]}...")
            logger.info(f"      Título: {titulo_actual}")
            
            # 🔍 DETECTAR SI VOLVIMOS AL LOGIN Y REINTENTAR
            if "authorization.oauth2" in url_actual and intentos_login < max_intentos_login:
                intentos_login += 1
                logger.warning(f"🔄 ¡VOLVIMOS AL LOGIN! (Intento {intentos_login}/{max_intentos_login})")
                logger.info("🔄 Reintentando login...")
                
                try:
                    # Esperar a que se recargue la página
                    time.sleep(2)
                    
                    # Llenar campos de login nuevamente
                    logger.info("🔐 Reintentando login - llenando campos...")
                    
                    # Campo de contraseña
                    campo_password = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#password"))
                    )
                    campo_password.clear()
                    campo_password.send_keys("Mediglobal1")
                    logger.info("✅ Campo contraseña completado (reintento)")
                    
                    # Campo de usuario
                    campo_username = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
                    )
                    campo_username.clear()
                    campo_username.send_keys("conveniosyseguros@mediglobal.com.ec")
                    logger.info("✅ Campo usuario completado (reintento)")
                    
                    # Hacer clic en el botón de login nuevamente
                    boton_login = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Inicio de sesión"]'))
                    )
                    boton_login.click()
                    logger.info("✅ Botón de login clickeado (reintento)")
                    
                    # Continuar con el siguiente intento
                    continue
                    
                except Exception as e:
                    logger.error(f"❌ Error en reintento de login: {e}")
                    if intentos_login >= max_intentos_login:
                        logger.error("❌ Máximo de reintentos de login alcanzado")
                        break
            
            # Verificar si llegamos a la página final de beneficios
            if "benefitsdirect.palig.com" in url_actual:
                logger.info(f"✅ ¡Primera redirección detectada en intento {intento}!")
                logger.info(f"   🎯 Página intermedia alcanzada: {url_actual}")
                
                # Esperar más tiempo para que se complete la segunda redirección
                logger.info("⏳ Esperando segunda redirección a MisPolizasPVR.aspx...")
                for intento2 in range(1, 21):  # Esperar 60 segundos más
                    time.sleep(3)
                    url_actual2 = driver.current_url
                    titulo_actual2 = driver.title
                    
                    logger.info(f"      ⏳ Intento 2.{intento2}/20 - URL: {url_actual2[:80]}...")
                    logger.info(f"         Título: {titulo_actual2}")
                    
                    # Verificar si llegamos a la página final
                    if "MisPolizasPVR.aspx" in url_actual2:
                        logger.info(f"🎯 ¡Redirección OAuth2 COMPLETAMENTE terminada en intento 2.{intento2}!")
                        logger.info(f"   🎯 Página final alcanzada: {url_actual2}")
                        break
                
                break
            
            # Verificar si estamos en la página de autorización.ping (estado intermedio)
            if "authorization.ping" in url_actual:
                logger.info(f"🔄 Estado intermedio OAuth2 detectado en intento {intento}")
                logger.info(f"   📍 Página de autorización.ping: {url_actual}")
                logger.info("   ⏳ Esperando continuación del flujo OAuth2...")
                
                # Verificar si hay algún botón o enlace para continuar
                try:
                    # Buscar botones o enlaces que puedan continuar el flujo
                    botones_continuar = driver.find_elements(By.CSS_SELECTOR, 
                        'button, input[type="submit"], a, [role="button"], .btn, .button')
                    
                    if botones_continuar:
                        logger.info(f"🔍 Encontrados {len(botones_continuar)} elementos clickeables")
                        for i, boton in enumerate(botones_continuar[:3]):  # Mostrar solo los primeros 3
                            texto = boton.text.strip() or boton.get_attribute('value') or 'sin-texto'
                            logger.info(f"   {i+1}. {boton.tag_name} - Texto: '{texto}'")
                        
                        # Intentar hacer clic en el primer botón visible
                        for boton in botones_continuar:
                            try:
                                if boton.is_displayed() and boton.is_enabled():
                                    logger.info(f"🎯 Intentando hacer clic en botón: {boton.tag_name} - '{boton.text.strip()}'")
                                    boton.click()
                                    logger.info("✅ Clic ejecutado, esperando redirección...")
                                    time.sleep(3)  # Esperar a que se procese
                                    break
                            except Exception as e:
                                logger.info(f"⚠️ No se pudo hacer clic en botón: {e}")
                                continue
                    else:
                        logger.info("ℹ️ No se encontraron elementos clickeables en la página de autorización.ping")
                        
                except Exception as e:
                    logger.info(f"ℹ️ Error buscando elementos clickeables: {e}")
                
                # Continuar esperando, no salir del bucle
            
            # Verificar si hay algún error
            try:
                errores = driver.find_elements(By.CSS_SELECTOR, '.error, .alert, .message, [class*="error"], [class*="alert"]')
                if errores:
                    for error in errores[:2]:
                        texto = error.text.strip()
                        if texto:
                            logger.warning(f"⚠️ Error detectado: {texto}")
                            
                            # Si hay error de autenticación, considerar reintento
                            if any(palabra in texto.lower() for palabra in ['invalid', 'incorrect', 'failed', 'error', 'incorrecto', 'invalido', 'fallido']):
                                logger.warning("⚠️ Error de autenticación detectado - considerando reintento")
            except:
                pass
        
        # Verificar URL final
        url_final = driver.current_url
        titulo_final = driver.title
        
        logger.info(f"✅ Redirección OAuth2 completada!")
        logger.info(f"   📍 URL final: {url_final}")
        logger.info(f"   📄 Título final: {titulo_final}")
        
        # Verificar si llegamos a la página correcta
        if "benefitsdirect.palig.com" in url_final:
            logger.info("🎯 ¡Página de beneficios alcanzada correctamente!")
            
            # Navegar a la página de búsqueda si no estamos ya ahí
            if "MisPolizasPVR.aspx" not in url_final:
                logger.info("🔄 Navegando a la página de búsqueda...")
                url_busqueda = "https://benefitsdirect.palig.com/Inicio/Contenido/InfoAsegurado/MisPolizasPVR.aspx"
                driver.get(url_busqueda)
                time.sleep(5)
                
                url_despues_navegacion = driver.current_url
                if "MisPolizasPVR.aspx" in url_despues_navegacion:
                    logger.info("✅ Página de búsqueda cargada exitosamente")
                else:
                    logger.warning("⚠️ No se pudo cargar la página de búsqueda")
            else:
                logger.info("✅ Ya estamos en la página de búsqueda correcta")
            
            # Probar búsqueda
            logger.info("🔍 Probando búsqueda...")
            try:
                # Buscar campo de búsqueda
                campo_busqueda = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"], input[placeholder*="documento"], input[name*="documento"]'))
                )
                
                # Llenar con un número de documento de prueba
                numero_prueba = "1234567890"
                campo_busqueda.clear()
                campo_busqueda.send_keys(numero_prueba)
                logger.info(f"✅ Campo de búsqueda llenado con: {numero_prueba}")
                
                # Buscar botón de búsqueda
                boton_buscar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"], .btn-primary, .btn-buscar'))
                )
                boton_buscar.click()
                logger.info("✅ Botón de búsqueda clickeado")
                
                # Esperar resultados
                time.sleep(5)
                logger.info("✅ Búsqueda completada")
                
            except Exception as e:
                logger.warning(f"⚠️ No se pudo completar la búsqueda: {e}")
                
        else:
            logger.warning("⚠️ No se llegó a la página de beneficios esperada")
            logger.info("🔄 Intentando navegar manualmente...")
            
            try:
                url_beneficios = "https://benefitsdirect.palig.com/Inicio/Contenido/InfoAsegurado/MisPolizasPVR.aspx"
                driver.get(url_beneficios)
                time.sleep(5)
                
                if "MisPolizasPVR.aspx" in driver.current_url:
                    logger.info("✅ Página de beneficios alcanzada manualmente")
                else:
                    logger.error("❌ No se pudo alcanzar la página de beneficios")
            except Exception as e:
                logger.error(f"❌ Error en navegación manual: {e}")
        
        logger.info("🎯 Prueba del flujo OAuth2 completada")
        logger.info(f"📊 Resumen de reintentos de login: {intentos_login}/{max_intentos_login}")
        
    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        
    finally:
        if driver:
            logger.info("🔌 Cerrando navegador...")
            driver.quit()

if __name__ == "__main__":
    test_oauth2_flow()
