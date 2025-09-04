#!/usr/bin/env python3
"""
Script de debug para validar paso a paso el flujo del worker
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
        logging.FileHandler('test_debug_worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def debug_worker_flow():
    """Debug del flujo completo del worker"""
    
    logger.info("🔍 INICIANDO DEBUG DEL FLUJO DEL WORKER")
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
            'NumDocIdentidad': '1234567890',
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
        
        # PASO 2: Simular login (simplificado para debug)
        logger.info("=" * 60)
        logger.info("🔍 PASO 2: Simulando proceso de login...")
        
        # URL de login
        url_login = "https://attest.palig.com/as/authorization.oauth2?client_id=cf7770f3699048ca9c61358b4dff25f5&redirect_uri=https%3A%2F%2Fbenefitsdirect.palig.com%2FInicio%2FLogin.aspx&response_type=code%20id_token&scope=openid%20profile%20email%20phone&state=OpenIdConnect.AuthenticationProperties%3DEXT82eDzm70H4FnxSn_OSRdC0ztASLp7Bvg8yLL52IEtIBpUyjD0IgIAK2j3eotEFyvMduisG7lsrN_jS47FwqP1Ye8RmSvSCWGJztHD53DbYlBg6Si-9zzt_8Efapm7-7fpkkxkUMhcPLmiLc54y6uQoA-d6uJ9jwBtbN00C1RguGixAAIRtMHyLWPVpBEQPpVPzS-6duAbBzUrsj9DrHDwEUlLYKM_XwLKzTN2C3kFXgQ6w5TVEjc7erJO16I1mxb4sAur-MV7SQAJNVbSg0smGa8JTlVV37t3I2zgvVeE1c44Hp4R72C9ivX23Ai0&response_mode=form_post&nonce=638918216386869899.ODZmNTA2ZDQtZDIwZi00MTE0LTk1NjItMjI0YWFlYzMyNzQ4MGE5YjVhOTgtMzNjNS00NDBmLTllMjAtYzg0NDY2MDkwNDc5&x-client-SKU=ID_NET451&x-client-ver=5.6.0.0"
        
        logger.info(f"🌐 Navegando a: {url_login}")
        driver.get(url_login)
        
        # Esperar a que cargue la página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("✅ Página de login cargada")
        
        # Llenar campos de login
        logger.info("🔐 Llenando campos de login...")
        
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
        
        # PASO 3: Esperar redirección OAuth2
        logger.info("=" * 60)
        logger.info("🔍 PASO 3: Esperando redirección OAuth2...")
        
        url_anterior = driver.current_url
        logger.info(f"📍 URL inicial: {url_anterior}")
        
        for intento in range(1, 21):  # 20 intentos
            time.sleep(3)
            
            url_actual = driver.current_url
            titulo_actual = driver.title
            
            if url_actual != url_anterior:
                logger.info(f"🔄 CAMBIO DE URL DETECTADO en intento {intento}/20")
                logger.info(f"   📍 URL anterior: {url_anterior}")
                logger.info(f"   📍 URL actual: {url_actual}")
                logger.info(f"   📄 Título: {titulo_actual}")
                url_anterior = url_actual
            else:
                logger.info(f"   ⏳ Intento {intento}/20 - URL: {url_actual[:80]}...")
                logger.info(f"      Título: {titulo_actual}")
            
            # Verificar si llegamos a la página final
            if "benefitsdirect.palig.com" in url_actual:
                logger.info(f"✅ ¡Redirección detectada en intento {intento}!")
                logger.info(f"   🎯 Página alcanzada: {url_actual}")
                break
        
        # PASO 4: Navegar a página de búsqueda
        logger.info("=" * 60)
        logger.info("🔍 PASO 4: Navegando a página de búsqueda...")
        
        url_busqueda = "https://benefitsdirect.palig.com/Inicio/Contenido/InfoAsegurado/MisPolizasPVR.aspx"
        logger.info(f"🌐 Navegando a: {url_busqueda}")
        driver.get(url_busqueda)
        
        # Esperar a que cargue la página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("✅ Página de búsqueda cargada")
        
        # PASO 5: Buscar por número de documento
        logger.info("=" * 60)
        logger.info("🔍 PASO 5: Buscando por número de documento...")
        
        # Buscar campo de búsqueda
        campo_busqueda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
        )
        campo_busqueda.clear()
        campo_busqueda.send_keys(datos_mensaje['NumDocIdentidad'])
        logger.info(f"✅ Número de documento ingresado: {datos_mensaje['NumDocIdentidad']}")
        
        # Buscar botón de búsqueda
        boton_busqueda = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"], button[type="submit"]'))
        )
        boton_busqueda.click()
        logger.info("✅ Click en botón de búsqueda ejecutado")
        
        # PASO 6: Esperar resultados
        logger.info("=" * 60)
        logger.info("🔍 PASO 6: Esperando resultados de búsqueda...")
        
        time.sleep(5)  # Esperar a que carguen los resultados
        
        # PASO 7: Buscar tabla de resultados
        logger.info("=" * 60)
        logger.info("🔍 PASO 7: Buscando tabla de resultados...")
        
        try:
            tabla = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.GridViewStylePV'))
            )
            logger.info("✅ Tabla GridViewStylePV encontrada")
            
            # Obtener filas
            filas = tabla.find_elements(By.CSS_SELECTOR, 'tr')
            logger.info(f"📋 Total de filas encontradas: {len(filas)}")
            
            if len(filas) > 1:
                logger.info("✅ Hay resultados en la tabla")
                
                # PASO 8: Buscar cliente específico
                logger.info("=" * 60)
                logger.info("🔍 PASO 8: Buscando cliente específico...")
                
                cliente_encontrado = buscar_cliente_en_tabla(filas, nombre_completo)
                
                if cliente_encontrado:
                    logger.info("✅ Cliente encontrado en la tabla")
                    
                    # PASO 9: Simular guardado en BD
                    logger.info("=" * 60)
                    logger.info("🔍 PASO 9: Simulando guardado en base de datos...")
                    
                    simular_guardado_bd(cliente_encontrado, datos_mensaje)
                    
                else:
                    logger.warning("⚠️ Cliente NO encontrado en la tabla")
            else:
                logger.warning("⚠️ No hay resultados en la tabla")
                
        except Exception as e:
            logger.error(f"❌ Error buscando tabla: {e}")
        
        # Resumen final
        logger.info("=" * 60)
        logger.info("🎯 RESUMEN DEL DEBUG:")
        logger.info(f"   📍 URL final: {driver.current_url}")
        logger.info(f"   📄 Título final: {driver.title}")
        logger.info("✅ Debug completado")
        
    except Exception as e:
        logger.error(f"❌ Error en debug: {e}")
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

def buscar_cliente_en_tabla(filas, nombre_completo):
    """Busca el cliente específico en la tabla"""
    try:
        # Obtener encabezados
        encabezados = []
        if filas:
            celdas_header = filas[0].find_elements(By.CSS_SELECTOR, 'th, td')
            encabezados = [celda.text.strip() for celda in celdas_header if celda.text.strip()]
            logger.info(f"📝 Encabezados: {encabezados}")
        
        # Buscar en filas de datos
        for i, fila in enumerate(filas[1:], 1):
            celdas = fila.find_elements(By.CSS_SELECTOR, 'td')
            if celdas:
                fila_data = {}
                for j, celda in enumerate(celdas):
                    if j < len(encabezados):
                        encabezado = encabezados[j]
                        valor = celda.text.strip()
                        fila_data[encabezado] = valor
                
                if fila_data:
                    nombre_paciente = fila_data.get('Nombre del Paciente', '')
                    logger.info(f"🔍 Fila {i}: '{nombre_paciente}'")
                    
                    if nombre_paciente.upper() == nombre_completo.upper():
                        logger.info(f"✅ ¡CLIENTE ENCONTRADO en fila {i}!")
                        logger.info(f"   📋 Datos: {fila_data}")
                        return fila_data
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error buscando cliente: {e}")
        return None

def simular_guardado_bd(fila_data, datos_mensaje):
    """Simula el guardado en base de datos"""
    try:
        logger.info("💾 Simulando guardado en base de datos...")
        
        # Verificar si hay IdFactura e IdAseguradora
        id_factura = datos_mensaje.get('IdFactura')
        id_aseguradora = datos_mensaje.get('IdAseguradora')
        
        logger.info(f"🔍 Verificando IDs:")
        logger.info(f"   • IdFactura: {id_factura}")
        logger.info(f"   • IdAseguradora: {id_aseguradora}")
        
        if id_factura and id_aseguradora:
            logger.info("✅ IDs encontrados - Procedería con UPDATE")
            logger.info(f"   📋 Póliza a actualizar: {fila_data.get('Póliza', 'N/A')}")
            logger.info(f"   📋 Dependiente a actualizar: {fila_data.get('No. Dependiente', 'N/A')}")
        else:
            logger.info("⚠️ IDs no encontrados - Procedería con INSERT")
        
        logger.info("✅ Simulación de guardado completada")
        
    except Exception as e:
        logger.error(f"❌ Error en simulación de guardado: {e}")

if __name__ == "__main__":
    debug_worker_flow()
