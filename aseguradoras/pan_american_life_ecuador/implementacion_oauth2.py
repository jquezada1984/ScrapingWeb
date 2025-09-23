#!/usr/bin/env python3
"""
Implementación específica para PAN AMERICAN LIFE DE ECUADOR
Maneja todo el flujo OAuth2, login, navegación y captura de datos
"""

import logging
import time
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

class PanAmericanLifeEcuadorOAuth2Processor:
    """Procesador específico para PAN AMERICAN LIFE DE ECUADOR"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.error_handler = None
        self.cache_get_function = None
        self.cache_save_function = None
        self.logger.info("🚀 Procesador OAuth2 PAN AMERICAN LIFE DE ECUADOR inicializado")
    
    def set_error_handler(self, error_handler_func):
        """Establece la función para manejar errores"""
        self.error_handler = error_handler_func
        self.logger.info("✅ Error handler configurado en procesador específico")
    
    def set_cache_functions(self, cache_get_func, cache_save_func):
        """Establece las funciones para manejar el caché"""
        self.cache_get_function = cache_get_func
        self.cache_save_function = cache_save_func
        self.logger.info("✅ Cache functions configuradas en procesador específico")
    
    def procesar_oauth2_completo(self, driver, datos_mensaje):
        """Procesa el flujo OAuth2 completo para PAN AMERICAN LIFE DE ECUADOR"""
        try:
            self.logger.info("🔐 Iniciando procesamiento OAuth2 completo para PAN AMERICAN LIFE DE ECUADOR")
            
            # Obtener NumDocIdentidad para verificar caché
            num_doc_identidad = datos_mensaje.get('NumDocIdentidad')
            if not num_doc_identidad:
                self.logger.error("❌ No se encontró NumDocIdentidad en los datos del mensaje")
                return False
            
            # Verificar si ya tenemos estos datos en caché
            if self.cache_get_function:
                datos_cache = self.cache_get_function(num_doc_identidad)
                if datos_cache:
                    # Usar datos del caché
                    self.logger.info("✅ Usando datos del caché para evitar búsqueda repetida")
                    
                    # Verificar si hay error en los datos del caché
                    if 'error' in datos_cache:
                        self.logger.error(f"❌ Error en datos del caché: {datos_cache['error']}")
                        # Guardar cliente con error en base de datos
                        if self.error_handler:
                            self.error_handler(datos_mensaje, datos_cache['error'])
                        return False
                    
                    # Guardar en base de datos usando datos del caché
                    if not self._guardar_cliente_en_bd(datos_cache, datos_mensaje):
                        self.logger.error("❌ Error guardando en base de datos con datos del caché")
                        return False
                    
                    self.logger.info("✅ Procesamiento OAuth2 completo exitoso usando caché")
                    return True
            
            # Si no está en caché, proceder con la búsqueda normal
            self.logger.info("🔍 NumDocIdentidad no encontrado en caché, procediendo con búsqueda en página...")
            
            # Verificar si ya estamos en la página correcta (después del login)
            if not self._verificar_pagina_correcta(driver):
                self.logger.info("🔄 No estamos en la página correcta, ejecutando login...")
                # Ejecutar login con reintentos solo si es necesario
                if not self._ejecutar_login_con_reintentos(driver):
                    self.logger.error("❌ Error en login con reintentos")
                    return False
            else:
                self.logger.info("✅ Ya estamos en la página correcta, continuando con búsqueda...")
            
            # Consultar y mostrar información de la tabla informacion_capturada
            self._mostrar_configuracion_campos()
            
            # Obtener configuración de campos desde la base de datos
            configuracion_campos = self._obtener_configuracion_campos()
            if not configuracion_campos:
                self.logger.error("❌ No se pudo obtener configuración de campos")
                return False
            
            # Realizar búsqueda con NumDocIdentidad
            if not self._realizar_busqueda_cliente(driver, datos_mensaje, configuracion_campos):
                self.logger.error("❌ Error en búsqueda del cliente")
                return False
            
            # Construir nombre completo del cliente
            nombre_completo = self._construir_nombre_completo(datos_mensaje)
            if not nombre_completo:
                self.logger.error("❌ No se pudo construir el nombre completo del cliente")
                return False
            
            # Capturar tabla y buscar cliente
            resultado = self._capturar_tabla_y_buscar_cliente(driver, nombre_completo, datos_mensaje)
            if not resultado:
                self.logger.error("❌ No se pudo capturar información de la tabla")
                return False
            
            # Guardar en caché para futuras referencias
            if self.cache_save_function:
                self.cache_save_function(num_doc_identidad, resultado)
            
            # Guardar en base de datos
            if not self._guardar_cliente_en_bd(resultado, datos_mensaje):
                self.logger.error("❌ Error guardando en base de datos")
                return False
            
            self.logger.info("✅ Procesamiento OAuth2 completo exitoso")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en procesamiento OAuth2 completo: {e}")
            return False
    
    def _verificar_pagina_correcta(self, driver):
        """Verifica si ya estamos en la página de búsqueda de PAN AMERICAN LIFE DE ECUADOR"""
        try:
            self.logger.info("🔍 Verificando si estamos en la página correcta...")
            
            # Verificar URL actual
            url_actual = driver.current_url
            self.logger.info(f"📍 URL actual: {url_actual}")
            
            # Si estamos en la URL correcta, asumir que estamos en la página correcta
            if "benefitsdirect.palig.com" in url_actual and "MisPolizasPVR" in url_actual:
                self.logger.info("✅ Estamos en la URL correcta de PAN AMERICAN LIFE DE ECUADOR")
                return True
            
            # Verificar elementos característicos de la página de búsqueda (más flexibles)
            elementos_verificacion = [
                "INFORMACIÓN GENERAL",
                "Identificación",
                "BUSCAR",
                "PÓLIZAS"
            ]
            
            elementos_encontrados = 0
            for elemento in elementos_verificacion:
                try:
                    # Buscar el elemento en la página
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{elemento}')]"))
                    )
                    self.logger.info(f"✅ Elemento encontrado: {elemento}")
                    elementos_encontrados += 1
                except TimeoutException:
                    self.logger.info(f"❌ Elemento no encontrado: {elemento}")
            
            # Si encontramos al menos 2 elementos, consideramos que estamos en la página correcta
            if elementos_encontrados >= 2:
                self.logger.info("✅ Estamos en la página correcta de PAN AMERICAN LIFE DE ECUADOR")
                return True
            else:
                self.logger.info("❌ No estamos en la página correcta")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando página correcta: {e}")
            return False
    
    def _mostrar_configuracion_campos(self):
        """Muestra la configuración de campos desde la tabla informacion_capturada"""
        try:
            self.logger.info("🔍 CONSULTANDO TABLA informacion_capturada...")
            
            # Primero obtener el IdUrl para PAN AMERICAN LIFE DE ECUADOR
            query_url = """
                SELECT id FROM urls_automatizacion 
                WHERE nombre = 'PAN AMERICAN LIFE DE ECUADOR'
            """
            
            resultado_url = self.db_manager.execute_query(query_url)
            if not resultado_url:
                self.logger.error("❌ No se encontró IdUrl para PAN AMERICAN LIFE DE ECUADOR")
                return
            
            id_url = resultado_url[0]['id']
            self.logger.info(f"✅ IdUrl encontrado: {id_url}")
            
            # Consultar la tabla informacion_capturada
            query_campos = """
                SELECT 
                    [SelectorCSS],
                    [BotonEnvio]
                FROM [NeptunoMedicalAutomatico].[dbo].[informacion_capturada]
                WHERE [IdUrl] = :id_url
            """
            
            campos = self.db_manager.execute_query(query_campos, {'id_url': id_url})
            
            if not campos:
                self.logger.warning("⚠️ No se encontraron registros en informacion_capturada para este IdUrl")
                return
            
            self.logger.info("=" * 80)
            self.logger.info("📋 CONFIGURACIÓN DE CAMPOS DESDE TABLA informacion_capturada")
            self.logger.info("=" * 80)
            self.logger.info(f"🔗 IdUrl: {id_url}")
            self.logger.info(f"📊 Total de registros encontrados: {len(campos)}")
            self.logger.info("")
            
            for i, campo in enumerate(campos, 1):
                self.logger.info(f"📝 REGISTRO {i}:")
                self.logger.info(f"   • SelectorCSS: {campo['SelectorCSS']}")
                self.logger.info(f"   • BotonEnvio: {campo['BotonEnvio']}")
                self.logger.info("")
            
            self.logger.info("=" * 80)
            
        except Exception as e:
            self.logger.error(f"❌ Error consultando tabla informacion_capturada: {e}")
    
    def _obtener_configuracion_campos(self):
        """Obtiene la configuración de campos desde la tabla informacion_capturada"""
        try:
            self.logger.info("🔍 Obteniendo configuración de campos desde la base de datos...")
            
            # Primero obtener el IdUrl para PAN AMERICAN LIFE DE ECUADOR
            query_url = """
                SELECT id FROM urls_automatizacion 
                WHERE nombre = 'PAN AMERICAN LIFE DE ECUADOR'
            """
            
            resultado_url = self.db_manager.execute_query(query_url)
            if not resultado_url:
                self.logger.error("❌ No se encontró IdUrl para PAN AMERICAN LIFE DE ECUADOR")
                return None
            
            id_url = resultado_url[0]['id']
            self.logger.info(f"✅ IdUrl encontrado: {id_url}")
            
            # Obtener configuración de campos
            query_campos = """
                SELECT [IdInformacion], [IdUrl], [NombreCampo], [ValorCampo], 
                       [TipoCampo], [SelectorCSS], [Orden], [Obligatorio], 
                       [Activo], [FechaCreacion], [BotonEnvio]
                FROM [NeptunoMedicalAutomatico].[dbo].[informacion_capturada]
                WHERE [IdUrl] = :id_url AND [Activo] = 1
                ORDER BY [Orden]
            """
            
            campos = self.db_manager.execute_query(query_campos, {'id_url': id_url})
            if not campos:
                self.logger.error("❌ No se encontraron campos configurados para PAN AMERICAN LIFE DE ECUADOR")
                return None
            
            self.logger.info(f"✅ Encontrados {len(campos)} campos configurados")
            for campo in campos:
                self.logger.info(f"   • {campo['NombreCampo']}: {campo['SelectorCSS']}")
            
            return campos
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo configuración de campos: {e}")
            return None
    
    def _realizar_busqueda_cliente(self, driver, datos_mensaje, configuracion_campos):
        """Realiza la búsqueda del cliente usando NumDocIdentidad"""
        try:
            self.logger.info("🔍 Realizando búsqueda del cliente...")
            
            num_doc_identidad = datos_mensaje.get('NumDocIdentidad')
            if not num_doc_identidad:
                self.logger.error("❌ No se encontró NumDocIdentidad en los datos del mensaje")
                return False
            
            self.logger.info(f"📋 NumDocIdentidad: {num_doc_identidad}")
            
            # Buscar el campo para ingresar NumDocIdentidad
            campo_documento = None
            boton_busqueda = None
            
            self.logger.info("🔍 Analizando configuración de campos...")
            for campo in configuracion_campos:
                self.logger.info(f"   • Campo: {campo['NombreCampo']} - Selector: {campo['SelectorCSS']} - BotonEnvio: {campo['BotonEnvio']}")
                
                # Buscar campo de identificación (más específico)
                if (campo['NombreCampo'].lower() in ['identificacion', 'identificacion del titular', 'documento', 'cedula', 'numdocidentidad'] or
                    'identificacion' in campo['SelectorCSS'].lower() or
                    'txtIdentificacion' in campo['SelectorCSS']):
                    campo_documento = campo
                    self.logger.info(f"✅ Campo de identificación encontrado: {campo['NombreCampo']}")
                
                # Buscar botón de búsqueda
                if campo['BotonEnvio'] and campo['BotonEnvio'].strip():
                    boton_busqueda = campo
                    self.logger.info(f"✅ Botón de búsqueda encontrado: {campo['BotonEnvio']}")
            
            if not campo_documento:
                self.logger.error("❌ No se encontró campo para NumDocIdentidad en la configuración")
                return False
            
            if not boton_busqueda:
                self.logger.error("❌ No se encontró botón de búsqueda en la configuración")
                return False
            
            self.logger.info(f"✅ Campo documento encontrado: {campo_documento['SelectorCSS']}")
            self.logger.info(f"✅ Botón búsqueda encontrado: {boton_busqueda['SelectorCSS']}")
            
            # Ingresar NumDocIdentidad
            try:
                selector_campo = campo_documento['SelectorCSS']
                self.logger.info(f"🔍 Buscando campo con selector: {selector_campo}")
                
                # Intentar diferentes métodos de búsqueda
                elemento_documento = None
                
                # Método 1: CSS Selector
                try:
                    elemento_documento = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector_campo))
                    )
                    self.logger.info("✅ Campo encontrado con CSS Selector")
                except TimeoutException:
                    self.logger.info("⚠️ CSS Selector no funcionó, intentando XPath...")
                    
                    # Método 2: XPath
                    try:
                        # Extraer el valor del atributo name sin las comillas
                        name_value = selector_campo.split('=')[1].strip('"')
                        xpath_selector = f"//input[@name='{name_value}']"
                        elemento_documento = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, xpath_selector))
                        )
                        self.logger.info("✅ Campo encontrado con XPath")
                    except TimeoutException:
                        self.logger.info("⚠️ XPath no funcionó, intentando búsqueda por atributo...")
                        
                        # Método 3: Búsqueda por atributo name
                        try:
                            name_value = selector_campo.split('=')[1].strip('"')
                            elemento_documento = driver.find_element(By.NAME, name_value)
                            self.logger.info("✅ Campo encontrado con búsqueda por atributo name")
                        except:
                            self.logger.error("❌ No se pudo encontrar el campo con ningún método")
                            return False
                
                if elemento_documento:
                    elemento_documento.clear()
                    elemento_documento.send_keys(num_doc_identidad)
                    self.logger.info(f"✅ NumDocIdentidad ingresado: {num_doc_identidad}")
                else:
                    self.logger.error("❌ No se pudo obtener el elemento del campo")
                    return False
                
            except Exception as e:
                self.logger.error(f"❌ Error ingresando NumDocIdentidad: {e}")
                return False
            
            # Hacer clic en el botón de búsqueda
            try:
                selector_boton = boton_busqueda['BotonEnvio']
                self.logger.info(f"🔍 Buscando botón con selector: {selector_boton}")
                
                # Intentar diferentes métodos de búsqueda para el botón
                elemento_boton = None
                
                # Método 1: CSS Selector
                try:
                    elemento_boton = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector_boton))
                    )
                    self.logger.info("✅ Botón encontrado con CSS Selector")
                except TimeoutException:
                    self.logger.info("⚠️ CSS Selector no funcionó para el botón, intentando XPath...")
                    
                    # Método 2: XPath
                    try:
                        # Extraer el valor del atributo id sin las comillas
                        id_value = selector_boton.split('=')[1].strip('"')
                        xpath_selector = f"//a[@id='{id_value}']"
                        elemento_boton = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, xpath_selector))
                        )
                        self.logger.info("✅ Botón encontrado con XPath")
                    except TimeoutException:
                        self.logger.info("⚠️ XPath no funcionó, intentando búsqueda por ID...")
                        
                        # Método 3: Búsqueda por ID
                        try:
                            id_value = selector_boton.split('=')[1].strip('"')
                            elemento_boton = driver.find_element(By.ID, id_value)
                            self.logger.info("✅ Botón encontrado con búsqueda por ID")
                        except:
                            self.logger.error("❌ No se pudo encontrar el botón con ningún método")
                            return False
                
                if elemento_boton:
                    elemento_boton.click()
                    self.logger.info("✅ Botón de búsqueda clickeado")
                    
                    # Esperar a que se cargue la página de resultados
                    time.sleep(3)
                else:
                    self.logger.error("❌ No se pudo obtener el elemento del botón")
                    return False
                
            except Exception as e:
                self.logger.error(f"❌ Error haciendo clic en el botón de búsqueda: {e}")
                return False
            
            self.logger.info("✅ Búsqueda del cliente completada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error realizando búsqueda del cliente: {e}")
            return False
    
    def _ejecutar_login_con_reintentos(self, driver):
        """Ejecuta el login con lógica de reintentos específica para PAN AMERICAN LIFE DE ECUADOR"""
        try:
            self.logger.info("🔐 Ejecutando login con reintentos...")
            
            # URL de login específica para PAN AMERICAN LIFE DE ECUADOR
            url_login = "https://attest.palig.com/as/authorization.oauth2?client_id=cf7770f3699048ca9c61358b4dff25f5&redirect_uri=https%3A%2F%2Fbenefitsdirect.palig.com%2FInicio%2FLogin.aspx&response_type=code%20id_token&scope=openid%20profile%20email%20phone&state=OpenIdConnect.AuthenticationProperties%3DEXT82eDzm70H4FnxSn_OSRdC0ztASLp7Bvg8yLL52IEtIBpUyjD0IgIAK2j3eotEFyvMduisG7lsrN_jS47FwqP1Ye8RmSvSCWGJztHD53DbYlBg6Si-9zzt_8Efapm7-7fpkkxkUMhcPLmiLc54y6uQoA-d6uJ9jwBtbN00C1RguGixAAIRtMHyLWPVpBEQPpVPzS-6duAbBzUrsj9DrHDwEUlLYKM_XwLKtTN2C3kFXgQ6w5TVEjc7erJO16I1mxb4sAur-MV7SQAJNVbSg0smGa8JTlVV37t3I2zgvVeE1c44Hp4R72C9ivX23Ai0&response_mode=form_post&nonce=638918216386869899.ODZmNTA2ZDQtZDIwZi00MTE0LTk1NjItMjI0YWFlYzMyNzQ4MGE5YjVhOTgtMzNjNS00NDBmLTllMjAtYzg0NDY2MDkwNDc5&x-client-SKU=ID_NET451&x-client-ver=5.6.0.0"
            
            self.logger.info(f"🌐 Navegando a: {url_login}")
            driver.get(url_login)
            
            # Esperar a que la página cargue
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.logger.info("✅ Página cargada correctamente")
            
            # Ejecutar campos de login
            self.logger.info("🔐 Ejecutando campos de login...")
            
            # Campo password
            password_element = self._buscar_elemento_con_reintento(driver, "#password", "Campo #password")
            password_element.clear()
            password_element.send_keys("Mediglobal1")
            self.logger.info("✅ Campo #password completado con: Mediglobal1")
            
            # Campo username
            username_element = self._buscar_elemento_con_reintento(driver, "#username", "Campo #username")
            username_element.clear()
            username_element.send_keys("conveniosyseguros@mediglobal.com.ec")
            self.logger.info("✅ Campo #username completado con: conveniosyseguros@mediglobal.com.ec")
            
            # Ejecutar acción post-login
            self.logger.info("🎯 Ejecutando acciones post-login...")
            
            # Variable para controlar reintentos de login
            intentos_login = 0
            max_intentos_login = 2
            
            # 🌍 CAMBIAR IDIOMA A ESPAÑOL ANTES DEL LOGIN
            try:
                self.logger.info("🌍 Cambiando idioma a español...")
                idioma_espanol = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[role="button"][onclick*="setLanguage(\'es\')"]'))
                )
                idioma_espanol.click()
                self.logger.info("✅ Idioma cambiado a español")
                time.sleep(2)  # Esperar a que se procese el cambio de idioma
            except Exception as e:
                self.logger.warning(f"⚠️ No se pudo cambiar idioma a español: {e}")
                self.logger.info("🔄 Continuando con idioma actual...")
            
            # Buscar y hacer clic en el botón de login (ahora en español)
            login_button = self._buscar_boton_con_reintento(driver, 'a[title="Inicio de sesión"]', 'Acción botón de login')
            login_button.click()
            self.logger.info("✅ Click ejecutado en: a[title=\"Inicio de sesión\"]")
            
            # Esperar a que se procese
            time.sleep(2)
            
            # 🚀 ESPERAR A QUE SE COMPLETE TODA LA REDIRECCIÓN OAUTH2
            self.logger.info("⏳ Esperando a que se complete la redirección OAuth2...")
            self.logger.info("🇪🇨 Esperando redirección completa para PAN AMERICAN LIFE DE ECUADOR...")
            
            # Variable para rastrear cambios de URL
            url_anterior = driver.current_url
            self.logger.info(f"📍 URL inicial: {url_anterior}")
            
            # Variables para control de timeout
            timeout_authorization_ping = 30  # 30 segundos máximo en authorization.ping
            tiempo_inicio_ping = None
            
            # Esperar hasta que llegue a la página final (máximo 120 segundos)
            for intento in range(1, 41):  # 40 intentos * 3 segundos = 120 segundos
                time.sleep(3)
                
                url_actual = driver.current_url
                titulo_actual = driver.title
                
                # Verificar si la URL cambió
                if url_actual != url_anterior:
                    self.logger.info(f"🔄 CAMBIO DE URL DETECTADO en intento {intento}/40")
                    self.logger.info(f"   📍 URL anterior: {url_anterior}")
                    self.logger.info(f"   📍 URL actual: {url_actual}")
                    self.logger.info(f"   📄 Título: {titulo_actual}")
                    url_anterior = url_actual
                else:
                    self.logger.info(f"   ⏳ Intento {intento}/40 - URL: {url_actual[:80]}...")
                    self.logger.info(f"      Título: {titulo_actual}")
                
                # 🔍 DETECTAR PÁGINA DE AUTORIZACIÓN.PING Y MANEJARLA
                if "authorization.ping" in url_actual:
                    # Iniciar timer si es la primera vez que detectamos esta página
                    if tiempo_inicio_ping is None:
                        tiempo_inicio_ping = time.time()
                        self.logger.info(f"🔄 ESTADO INTERMEDIO OAUTH2 DETECTADO en intento {intento}")
                        self.logger.info(f"   📍 Página de autorización.ping: {url_actual}")
                        self.logger.info(f"   📄 Título de la página: {titulo_actual}")
                        self.logger.info(f"   ⏳ Esperando continuación del flujo OAuth2...")
                    else:
                        # Verificar timeout
                        tiempo_transcurrido = time.time() - tiempo_inicio_ping
                        if tiempo_transcurrido > timeout_authorization_ping:
                            self.logger.warning(f"⚠️ TIMEOUT en página authorization.ping después de {timeout_authorization_ping} segundos")
                            self.logger.warning(f"   🔄 Recargando página para forzar continuación...")
                            
                            try:
                                driver.refresh()
                                time.sleep(5)
                                tiempo_inicio_ping = None  # Resetear timer
                                continue
                            except Exception as e:
                                self.logger.error(f"❌ Error recargando página: {e}")
                                break
                    
                    # Buscar elementos para continuar el flujo
                    self.logger.info(f"   🔍 Buscando elementos para continuar el flujo...")
                    try:
                        # Buscar botones o enlaces para continuar
                        elementos_continuar = driver.find_elements(By.CSS_SELECTOR, 
                            'input[type="submit"], button, a, input[value*="continuar"], input[value*="siguiente"]')
                        
                        if elementos_continuar:
                            self.logger.info(f"   ✅ Encontrados {len(elementos_continuar)} elementos para continuar")
                            for i, elem in enumerate(elementos_continuar):
                                try:
                                    texto = elem.text or elem.get_attribute('value') or elem.get_attribute('title') or 'sin-texto'
                                    self.logger.info(f"      {i+1}. {elem.tag_name} - Texto: '{texto}'")
                                    
                                    # Intentar hacer clic en el primer elemento clickeable
                                    if elem.is_enabled() and elem.is_displayed():
                                        self.logger.info(f"   🎯 Haciendo clic en elemento {i+1} para continuar...")
                                        elem.click()
                                        self.logger.info(f"   ✅ Click ejecutado, esperando continuación...")
                                        time.sleep(2)
                                        tiempo_inicio_ping = None  # Resetear timer después del click
                                        break
                                except Exception as e:
                                    self.logger.warning(f"   ⚠️ No se pudo hacer clic en elemento {i+1}: {e}")
                        else:
                            self.logger.info(f"   ℹ️ No se encontraron elementos clickeables en la página de autorización.ping")
                            
                    except Exception as e:
                        self.logger.warning(f"   ⚠️ Error buscando elementos de continuación: {e}")
                    
                    # Continuar esperando
                    continue
                
                # 🔍 DETECTAR SI VOLVIMOS AL LOGIN Y REINTENTAR
                if "authorization.oauth2" in url_actual and intentos_login < max_intentos_login:
                    intentos_login += 1
                    self.logger.warning(f"🔄 ¡VOLVIMOS AL LOGIN! (Intento {intentos_login}/{max_intentos_login})")
                    self.logger.info("🔄 Reintentando login automáticamente...")
                    
                    try:
                        # Esperar a que se recargue la página
                        time.sleep(2)
                        
                        # Reintentar campos de login
                        self.logger.info("🔐 Reintentando login - llenando campos...")
                        
                        # Campo password (reintento)
                        password_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#password"))
                        )
                        password_element.clear()
                        password_element.send_keys("Mediglobal1")
                        self.logger.info("✅ Campo #password completado (reintento)")
                        
                        # Campo username (reintento)
                        username_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
                        )
                        username_element.clear()
                        username_element.send_keys("conveniosyseguros@mediglobal.com.ec")
                        self.logger.info("✅ Campo #username completado (reintento)")
                        
                        # Reintentar acciones post-login
                        self.logger.info("🎯 Reintentando acciones post-login...")
                        
                        login_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Inicio de sesión"]'))
                        )
                        login_button.click()
                        self.logger.info("✅ Click ejecutado (reintento) en: a[title=\"Inicio de sesión\"]")
                        
                        time.sleep(2)
                        
                        self.logger.info("✅ Reintento de login completado, continuando...")
                        
                    except Exception as e:
                        self.logger.error(f"❌ Error en reintento de login: {e}")
                        if intentos_login >= max_intentos_login:
                            self.logger.error("❌ Máximo de reintentos de login alcanzado")
                            break
                    
                    # Continuar con el siguiente intento
                    continue
                
                # Verificar si llegamos a la página final de beneficios
                if "benefitsdirect.palig.com" in url_actual:
                    self.logger.info(f"✅ ¡Primera redirección detectada en intento {intento}!")
                    self.logger.info(f"   🎯 Página intermedia alcanzada: {url_actual}")
                    
                    # Esperar más tiempo para que se complete la segunda redirección
                    self.logger.info("⏳ Esperando segunda redirección a MisPolizasPVR.aspx...")
                    
                    # Variable para rastrear cambios de URL en la segunda redirección
                    url_anterior2 = driver.current_url
                    self.logger.info(f"      📍 URL inicial segunda redirección: {url_anterior2}")
                    
                    for intento2 in range(1, 21):  # Esperar 60 segundos más
                        time.sleep(3)
                        url_actual2 = driver.current_url
                        titulo_actual2 = driver.title
                        
                        # Verificar si la URL cambió en la segunda redirección
                        if url_actual2 != url_anterior2:
                            self.logger.info(f"      🔄 CAMBIO DE URL en segunda redirección - intento 2.{intento2}/20")
                            self.logger.info(f"         📍 URL anterior: {url_anterior2}")
                            self.logger.info(f"         📍 URL actual: {url_actual2}")
                            self.logger.info(f"         📄 Título: {titulo_actual2}")
                            url_anterior2 = url_actual2
                        else:
                            self.logger.info(f"      ⏳ Intento 2.{intento2}/20 - URL: {url_actual2[:80]}...")
                            self.logger.info(f"         📄 Título: {titulo_actual2}")
                        
                        # Verificar si llegamos a la página final
                        if "MisPolizasPVR.aspx" in url_actual2:
                            self.logger.info(f"🎯 ¡Redirección OAuth2 COMPLETAMENTE terminada en intento 2.{intento2}!")
                            self.logger.info(f"   🎯 Página final alcanzada: {url_actual2}")
                            break
                    
                    break
            
            # Verificar URL final
            url_final = driver.current_url
            titulo_final = driver.title
            
            self.logger.info(f"✅ REDIRECCIÓN OAUTH2 COMPLETADA!")
            self.logger.info(f"   📍 URL final: {url_final}")
            self.logger.info(f"   📄 Título final: {titulo_final}")
            self.logger.info(f"📊 Resumen de reintentos de login: {intentos_login}/{max_intentos_login}")
            
            # Verificar si llegamos a la página correcta
            if "benefitsdirect.palig.com" in url_final:
                self.logger.info("🎯 ¡Página de beneficios alcanzada correctamente!")
                
                # Verificar si estamos en la página principal en lugar de la de búsqueda
                if "MisPolizasPVR.aspx" not in url_final:
                    self.logger.info("⚠️ DETECTADA PÁGINA PRINCIPAL - redirigiendo a página de búsqueda...")
                    self.logger.info(f"   📍 URL actual (página principal): {url_final}")
                    self.logger.info(f"   📄 Título de página principal: {titulo_final}")
                    
                    # Esperar un poco más para que se complete cualquier redirección pendiente
                    time.sleep(3)
                    
                    # Verificar si ya se redirigió automáticamente
                    url_actualizada = driver.current_url
                    if "MisPolizasPVR.aspx" in url_actualizada:
                        self.logger.info("✅ Redirección automática completada")
                    else:
                        self.logger.info("🔄 Forzando navegación a página de búsqueda...")
                        
                        # Intentar navegar a la página específica de búsqueda
                        try:
                            url_busqueda = "https://benefitsdirect.palig.com/Inicio/Contenido/InfoAsegurado/MisPolizasPVR.aspx"
                            self.logger.info(f"🌐 NAVEGACIÓN MANUAL A PÁGINA DE BÚSQUEDA")
                            self.logger.info(f"   📍 URL objetivo: {url_busqueda}")
                            self.logger.info(f"   📍 URL antes de navegación: {driver.current_url}")
                            
                            driver.get(url_busqueda)
                            time.sleep(5)  # Esperar a que cargue
                            
                            # Verificar que la navegación fue exitosa
                            url_despues_navegacion = driver.current_url
                            titulo_despues_navegacion = driver.title
                            
                            self.logger.info(f"   📍 URL después de navegación: {url_despues_navegacion}")
                            self.logger.info(f"   📄 Título después de navegación: {titulo_despues_navegacion}")
                            
                            if "MisPolizasPVR.aspx" in url_despues_navegacion:
                                self.logger.info("✅ PÁGINA DE BÚSQUEDA ALCANZADA EXITOSAMENTE")
                                self.logger.info(f"   📍 URL final: {url_despues_navegacion}")
                                self.logger.info(f"   📄 Título: {titulo_despues_navegacion}")
                            else:
                                self.logger.warning("⚠️ NAVEGACIÓN NO COMPLETADA")
                                self.logger.info(f"   📍 URL actual (no es la esperada): {url_despues_navegacion}")
                                
                        except Exception as e:
                            self.logger.error(f"❌ Error en navegación manual: {e}")
                else:
                    self.logger.info("✅ Ya estamos en la página de búsqueda correcta")
                    
            else:
                self.logger.warning("⚠️ No se llegó a la página de beneficios esperada")
                self.logger.info("🔄 Intentando navegación manual completa...")
                
                # Intentar navegar manualmente si no llegamos automáticamente
                try:
                    url_beneficios = "https://benefitsdirect.palig.com/Inicio/Contenido/InfoAsegurado/MisPolizasPVR.aspx"
                    self.logger.info(f"🌐 NAVEGACIÓN MANUAL COMPLETA")
                    self.logger.info(f"   📍 URL objetivo: {url_beneficios}")
                    self.logger.info(f"   📍 URL actual antes de navegación manual: {driver.current_url}")
                    
                    driver.get(url_beneficios)
                    time.sleep(5)  # Esperar a que cargue
                    
                    url_actual_manual = driver.current_url
                    titulo_actual_manual = driver.title
                    self.logger.info(f"✅ NAVEGACIÓN MANUAL COMPLETADA")
                    self.logger.info(f"   📍 URL después de navegación manual: {url_actual_manual}")
                    self.logger.info(f"   📄 Título después de navegación manual: {titulo_actual_manual}")
                    
                    if "MisPolizasPVR.aspx" in url_actual_manual:
                        self.logger.info("🎯 ¡PÁGINA DE BENEFICIOS ALCANZADA MANUALMENTE!")
                        self.logger.info(f"   📍 URL final: {url_actual_manual}")
                    else:
                        self.logger.warning("⚠️ NO SE PUDO ALCANZAR LA PÁGINA DE BENEFICIOS")
                        self.logger.warning(f"   📍 URL final (no es la esperada): {url_actual_manual}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error en navegación manual: {e}")
            
            # Obtener la URL actual para verificar si cambió
            url_actual = driver.current_url
            titulo_pagina = driver.title
            
            self.logger.info(f"✅ Login completado exitosamente!")
            self.logger.info(f"   📍 URL actual: {url_actual}")
            self.logger.info(f"   📄 Título de la página: {titulo_pagina}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando login con reintentos: {e}")
            return False
    
    def _navegar_a_pagina_busqueda(self, driver):
        """Navega a la página de búsqueda específica"""
        try:
            self.logger.info("🔍 Navegando a página de búsqueda...")
            
            url_actual = driver.current_url
            if "MisPolizasPVR.aspx" in url_actual:
                self.logger.info("✅ Ya estamos en la página de búsqueda")
                return True
            
            # Navegar a la página de búsqueda
            url_busqueda = "https://benefitsdirect.palig.com/Inicio/Contenido/InfoAsegurado/MisPolizasPVR.aspx"
            driver.get(url_busqueda)
            time.sleep(5)
            
            url_despues = driver.current_url
            if "MisPolizasPVR.aspx" in url_despues:
                self.logger.info("✅ Página de búsqueda alcanzada")
                return True
            else:
                self.logger.warning(f"⚠️ No se pudo alcanzar la página de búsqueda: {url_despues}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error navegando a página de búsqueda: {e}")
            return False
    
    def _construir_nombre_completo(self, datos_mensaje):
        """Construye el nombre completo del cliente concatenando los campos"""
        try:
            self.logger.info("🔤 Construyendo nombre completo del cliente...")
            
            # Extraer campos del mensaje
            primer_nombre = datos_mensaje.get('PersonaPrimerNombre', '').strip()
            segundo_nombre = datos_mensaje.get('PersonaSegundoNombre', '').strip()
            primer_apellido = datos_mensaje.get('PersonaPrimerApellido', '').strip()
            segundo_apellido = datos_mensaje.get('PersonaSegundoApellido', '').strip()
            
            self.logger.info(f"   📝 Primer nombre: '{primer_nombre}'")
            self.logger.info(f"   📝 Segundo nombre: '{segundo_nombre}'")
            self.logger.info(f"   📝 Primer apellido: '{primer_apellido}'")
            self.logger.info(f"   📝 Segundo apellido: '{segundo_apellido}'")
            
            # Construir nombre completo
            partes_nombre = []
            
            if primer_nombre:
                partes_nombre.append(primer_nombre)
            if segundo_nombre:
                partes_nombre.append(segundo_nombre)
            if primer_apellido:
                partes_nombre.append(primer_apellido)
            if segundo_apellido:
                partes_nombre.append(segundo_apellido)
            
            if not partes_nombre:
                self.logger.error("❌ No se pudo construir el nombre completo - todos los campos están vacíos")
                return None
            
            nombre_completo = ' '.join(partes_nombre)
            self.logger.info(f"✅ Nombre completo construido: '{nombre_completo}'")
            
            return nombre_completo
            
        except Exception as e:
            self.logger.error(f"❌ Error construyendo nombre completo: {e}")
            return None
    
    def _capturar_tabla_y_buscar_cliente(self, driver, nombre_completo, datos_mensaje):
        """Captura la tabla y busca el cliente específico"""
        try:
            self.logger.info("🔍 Capturando tabla y buscando cliente...")
            
            # Buscar la tabla de resultados
            tabla = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ContenidoPrincipal_CtrlBuscaAseguradoProv_gridAsegurados"))
            )
            
            self.logger.info("✅ Tabla encontrada")
            
            # Buscar filas de datos
            filas = tabla.find_elements(By.CSS_SELECTOR, 'tr.RowStylePV')
            total_registros = len(filas)
            self.logger.info(f"📊 TOTAL DE REGISTROS RECIBIDOS: {total_registros}")
            self.logger.info(f"🔄 INICIANDO PROCESAMIENTO DE {total_registros} REGISTROS...")
            
            # Buscar el cliente específico
            for i, fila in enumerate(filas):
                progreso_actual = i + 1
                self.logger.info(f"📈 PROGRESO: {progreso_actual}/{total_registros} registros procesados ({(progreso_actual/total_registros)*100:.1f}%)")
                try:
                    # Re-buscar la fila para evitar elementos stale
                    filas_actualizadas = tabla.find_elements(By.CSS_SELECTOR, 'tr.RowStylePV')
                    if i >= len(filas_actualizadas):
                        self.logger.warning(f"⚠️ Fila {i+1} ya no existe, saltando...")
                        continue
                    
                    fila_actual = filas_actualizadas[i]
                    
                    # Buscar la columna "Nombre del Paciente"
                    celdas = fila_actual.find_elements(By.TAG_NAME, 'td')
                    if len(celdas) >= 8:  # Asegurar que hay suficientes columnas
                        # Intentar diferentes métodos para extraer el texto
                        try:
                            # Método 1: .text
                            nombre_paciente = celdas[3].text.strip()
                            self.logger.info(f"      🔍 Método .text: '{nombre_paciente}'")
                            
                            if not nombre_paciente:
                                # Método 2: innerHTML
                                nombre_paciente = celdas[3].get_attribute('innerHTML').strip()
                                self.logger.info(f"      🔍 Método innerHTML: '{nombre_paciente}'")
                                
                                # Limpiar HTML tags si existen
                                import re
                                nombre_paciente = re.sub(r'<[^>]+>', '', nombre_paciente).strip()
                                self.logger.info(f"      🔍 Después de limpiar HTML: '{nombre_paciente}'")
                            
                            if not nombre_paciente:
                                # Método 3: innerText
                                nombre_paciente = celdas[3].get_attribute('innerText').strip()
                                self.logger.info(f"      🔍 Método innerText: '{nombre_paciente}'")
                                
                        except Exception as e:
                            self.logger.error(f"      ❌ Error extrayendo nombre: {e}")
                            nombre_paciente = ""
                        
                        self.logger.info(f"   🔍 Fila {i+1}: '{nombre_paciente}' (celdas: {len(celdas)})")
                        
                        # Log de todas las celdas para debugging
                        for j, celda in enumerate(celdas):
                            try:
                                texto_celda = celda.text.strip() or celda.get_attribute('innerHTML').strip()
                                self.logger.info(f"      Celda {j}: '{texto_celda[:50]}...'")
                            except:
                                self.logger.info(f"      Celda {j}: [ERROR extrayendo texto]")
                        
                        # Función para normalizar nombres (quitar acentos, espacios extra, etc.)
                        def normalizar_nombre(nombre):
                            import re
                            import unicodedata
                            # Convertir a mayúsculas
                            nombre = nombre.upper()
                            # Quitar acentos
                            nombre = unicodedata.normalize('NFD', nombre).encode('ascii', 'ignore').decode('ascii')
                            # Quitar espacios extra y caracteres especiales
                            nombre = re.sub(r'\s+', ' ', nombre).strip()
                            # Quitar caracteres no alfanuméricos excepto espacios
                            nombre = re.sub(r'[^A-Z0-9\s]', '', nombre)
                            return nombre
                        
                        # Normalizar ambos nombres para comparación
                        nombre_paciente_normalizado = normalizar_nombre(nombre_paciente)
                        nombre_completo_normalizado = normalizar_nombre(nombre_completo)
                        
                        self.logger.info(f"   🔍 COMPARACIÓN DE NOMBRES:")
                        self.logger.info(f"      • Nombre original buscado: '{nombre_completo}'")
                        self.logger.info(f"      • Nombre original encontrado: '{nombre_paciente}'")
                        self.logger.info(f"      • Nombre normalizado buscado: '{nombre_completo_normalizado}'")
                        self.logger.info(f"      • Nombre normalizado encontrado: '{nombre_paciente_normalizado}'")
                        
                        # Verificar si coincide (exacto o parcial)
                        coincide_exacto = nombre_paciente_normalizado == nombre_completo_normalizado
                        coincide_parcial = (nombre_completo_normalizado in nombre_paciente_normalizado or 
                                          nombre_paciente_normalizado in nombre_completo_normalizado)
                        
                        if coincide_exacto or coincide_parcial:
                            tipo_coincidencia = "EXACTA" if coincide_exacto else "PARCIAL"
                            self.logger.info(f"🎯 ¡CLIENTE ENCONTRADO! ({tipo_coincidencia}) Fila {i+1}/{total_registros} - Procesando datos...")
                            
                                # EXTRAER TODOS LOS DATOS INMEDIATAMENTE para evitar elementos stale
                                try:
                                    self.logger.info("🔍 EXTRAYENDO DATOS DE LA FILA ENCONTRADA...")
                                    
                                    # Extraer datos de todas las celdas de una vez
                                    datos_celdas = []
                                    for j, celda in enumerate(celdas):
                                        try:
                                            # Método 1: .text
                                            texto = celda.text.strip()
                                            if not texto:
                                                # Método 2: innerHTML y limpiar
                                                texto = celda.get_attribute('innerHTML').strip()
                                                import re
                                                texto = re.sub(r'<[^>]+>', '', texto).strip()
                                            if not texto:
                                                # Método 3: innerText
                                                texto = celda.get_attribute('innerText').strip()
                                            
                                            datos_celdas.append(texto)
                                            self.logger.info(f"   📋 Celda {j}: '{texto}'")
                                        except Exception as e:
                                            self.logger.error(f"   ❌ Error extrayendo celda {j}: {e}")
                                            datos_celdas.append("")
                                
                                self.logger.info(f"📊 TOTAL DE CELDAS EXTRAÍDAS: {len(datos_celdas)}")
                                self.logger.info(f"📋 RESUMEN DE DATOS EXTRAÍDOS:")
                                for j, dato in enumerate(datos_celdas):
                                    self.logger.info(f"   Celda {j}: '{dato}'")
                                
                                # Verificar que el status sea "Activo" - buscar en el span dentro del div
                                self.logger.info("🔍 VERIFICANDO STATUS DEL CLIENTE...")
                                try:
                                    # Método 1: Buscar el span dentro del div verde
                                    status_element = fila_actual.find_element(By.CSS_SELECTOR, ".rectangle-green span")
                                    status_texto = status_element.text.strip()
                                    self.logger.info(f"   📊 Status encontrado (método 1): '{status_texto}'")
                                except Exception as e:
                                    self.logger.warning(f"   ⚠️ Método 1 falló: {e}")
                                    try:
                                        # Método 2: Buscar cualquier span con texto "Activo"
                                        status_element = fila_actual.find_element(By.XPATH, ".//span[contains(text(), 'Activo')]")
                                        status_texto = status_element.text.strip()
                                        self.logger.info(f"   📊 Status encontrado (método 2): '{status_texto}'")
                                    except Exception as e2:
                                        self.logger.warning(f"   ⚠️ Método 2 falló: {e2}")
                                        # Método 3: Fallback a datos extraídos
                                        status_texto = datos_celdas[7] if len(datos_celdas) > 7 else ""
                                        self.logger.info(f"   📊 Status (fallback): '{status_texto}'")
                                
                                self.logger.info(f"🔍 STATUS FINAL: '{status_texto}'")
                                
                                if "ACTIVO" in status_texto.upper():
                                    self.logger.info("✅ Status 'Activo' confirmado - procediendo con extracción de datos")
                                    
                                    # Crear diccionario con los datos extraídos
                                    self.logger.info("📋 CREANDO DICCIONARIO DE DATOS...")
                                    datos_fila = {
                                        'poliza': datos_celdas[0] if len(datos_celdas) > 0 else "",  # Póliza
                                        'certificado': datos_celdas[1] if len(datos_celdas) > 1 else "",  # Certificado
                                        'no_dependiente': datos_celdas[2] if len(datos_celdas) > 2 else "",  # No. Dependiente
                                        'nombre_paciente': datos_celdas[3] if len(datos_celdas) > 3 else "",  # Nombre del Paciente
                                        'titular': datos_celdas[4] if len(datos_celdas) > 4 else "",  # Titular
                                        'relacion': datos_celdas[5] if len(datos_celdas) > 5 else "",  # Relación
                                        'tipo_poliza': datos_celdas[6] if len(datos_celdas) > 6 else "",  # Tipo de Póliza
                                        'status': status_texto,  # Status
                                        'dependiente': datos_celdas[9] if len(datos_celdas) > 9 else ""  # Dependiente (columna oculta)
                                    }
                                    
                                    self.logger.info(f"📋 Datos finales para actualización:")
                                    for key, value in datos_fila.items():
                                        self.logger.info(f"   • {key}: {value}")
                                    
                                    # Actualizar la base de datos con los datos encontrados
                                    self.logger.info("💾 ACTUALIZANDO BASE DE DATOS...")
                                    try:
                                        if self._actualizar_factura_cliente(datos_fila, datos_mensaje):
                                            self.logger.info("✅ Base de datos actualizada exitosamente")
                                            self.logger.info(f"✅ PROCESAMIENTO EXITOSO: Cliente encontrado y procesado en fila {i+1}/{total_registros}")
                                            return datos_fila
                                        else:
                                            self.logger.error("❌ Error actualizando base de datos")
                                            # Guardar cliente con error
                                            if self.error_handler:
                                                error_msg = f"Error actualizando base de datos para cliente '{nombre_completo}'"
                                                self.logger.info(f"💾 Guardando cliente con error: {error_msg}")
                                                if self.error_handler(datos_mensaje, error_msg):
                                                    self.logger.info("✅ Cliente con error guardado exitosamente")
                                                else:
                                                    self.logger.error("❌ Error guardando cliente con error")
                                    except Exception as e:
                                        self.logger.error(f"❌ Excepción actualizando base de datos: {e}")
                                        # Guardar cliente con error
                                        if self.error_handler:
                                            error_msg = f"Excepción actualizando base de datos para cliente '{nombre_completo}': {str(e)}"
                                            self.logger.info(f"💾 Guardando cliente con error: {error_msg}")
                                            if self.error_handler(datos_mensaje, error_msg):
                                                self.logger.info("✅ Cliente con error guardado exitosamente")
                                            else:
                                                self.logger.error("❌ Error guardando cliente con error")
                                else:
                                    self.logger.warning(f"⚠️ Cliente encontrado pero status no es 'Activo': {status_texto}")
                                    
                                    # Guardar cliente con error si hay error handler disponible
                                    if self.error_handler:
                                        error_msg = f"Cliente '{nombre_completo}' encontrado pero status no es 'Activo': {status_texto}"
                                        self.logger.info(f"💾 Guardando cliente con error: {error_msg}")
                                        if self.error_handler(datos_mensaje, error_msg):
                                            self.logger.info("✅ Cliente con error guardado exitosamente")
                                        else:
                                            self.logger.error("❌ Error guardando cliente con error")
                                    
                            except Exception as e:
                                self.logger.error(f"❌ Error extrayendo datos de la fila: {e}")
                                continue
                        else:
                            self.logger.info(f"   ❌ No coincide: '{nombre_paciente_normalizado}' != '{nombre_completo_normalizado}'")
                            
                except Exception as e:
                    self.logger.warning(f"⚠️ Error procesando fila {i+1}: {e}")
                    continue
            
            self.logger.warning(f"⚠️ Cliente '{nombre_completo}' no encontrado en la tabla")
            self.logger.info(f"📊 RESUMEN FINAL: {total_registros} registros procesados - Cliente no encontrado")
            
            # Guardar cliente con error si hay error handler disponible
            if self.error_handler:
                error_msg = f"Cliente '{nombre_completo}' no encontrado en la tabla de resultados"
                self.logger.info(f"💾 Guardando cliente con error: {error_msg}")
                if self.error_handler(datos_mensaje, error_msg):
                    self.logger.info("✅ Cliente con error guardado exitosamente")
                else:
                    self.logger.error("❌ Error guardando cliente con error")
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error capturando tabla y buscando cliente: {e}")
            
            # Guardar cliente con error si hay error handler disponible
            if self.error_handler:
                error_msg = f"Error capturando tabla y buscando cliente: {str(e)}"
                self.logger.info(f"💾 Guardando cliente con error: {error_msg}")
                if self.error_handler(datos_mensaje, error_msg):
                    self.logger.info("✅ Cliente con error guardado exitosamente")
                else:
                    self.logger.error("❌ Error guardando cliente con error")
            
            return None
    
    def _actualizar_factura_cliente(self, datos_fila, datos_mensaje):
        """Actualiza la tabla FacturaCliente con los datos encontrados"""
        try:
            self.logger.info("🔄 Actualizando tabla FacturaCliente...")
            
            # Extraer datos necesarios
            num_poliza = datos_fila.get('poliza', '')
            num_dependiente = datos_fila.get('no_dependiente', '')
            id_factura = datos_mensaje.get('IdFactura', '')
            id_aseguradora = datos_mensaje.get('IdAseguradora', '')
            
            self.logger.info(f"📋 Datos para actualización:")
            self.logger.info(f"   • NumPoliza: '{num_poliza}'")
            self.logger.info(f"   • NumDependiente: '{num_dependiente}'")
            self.logger.info(f"   • IdFactura: '{id_factura}'")
            self.logger.info(f"   • IdAseguradora: '{id_aseguradora}'")
            
            # Verificar que tenemos todos los datos necesarios
            if not all([num_poliza, id_factura, id_aseguradora]):
                self.logger.error("❌ Faltan datos necesarios para la actualización")
                return False
            
            # Ejecutar la consulta UPDATE
            query = """
                UPDATE [dbo].[FacturaCliente] 
                SET NumPoliza = :num_poliza, 
                    NumDependiente = :num_dependiente
                WHERE IdFactura = :id_factura 
                AND IdAseguradora = :id_aseguradora
            """
            
            params = {
                'num_poliza': num_poliza,
                'num_dependiente': num_dependiente,
                'id_factura': id_factura,
                'id_aseguradora': id_aseguradora
            }
            
            self.logger.info(f"🔍 Ejecutando query UPDATE:")
            self.logger.info(f"   Query: {query}")
            self.logger.info(f"   Parámetros: {params}")
            
            # Ejecutar la actualización
            try:
                result = self.db_manager.execute_query(query, params)
                
                if result:
                    self.logger.info("✅ UPDATE ejecutado exitosamente")
                    
                    # Verificar cuántas filas fueron afectadas
                    if hasattr(result, 'rowcount'):
                        filas_afectadas = result.rowcount
                        self.logger.info(f"📊 Filas afectadas: {filas_afectadas}")
                        
                        if filas_afectadas > 0:
                            self.logger.info("✅ Registro actualizado correctamente")
                            return True
                        else:
                            self.logger.warning("⚠️ No se encontró ningún registro para actualizar")
                            return False
                    else:
                        self.logger.info("✅ Actualización completada (sin información de filas afectadas)")
                        return True
                else:
                    self.logger.error("❌ Error ejecutando UPDATE - resultado None")
                    return False
                    
            except Exception as db_error:
                # Capturar y mostrar el error específico de la base de datos
                self.logger.error(f"❌ ERROR DE BASE DE DATOS:")
                self.logger.error(f"   • Tipo de error: {type(db_error).__name__}")
                self.logger.error(f"   • Mensaje: {str(db_error)}")
                
                # Información adicional sobre el error
                if hasattr(db_error, 'args') and db_error.args:
                    self.logger.error(f"   • Argumentos del error: {db_error.args}")
                
                # Información específica para errores de SQL Server
                if hasattr(db_error, 'orig') and db_error.orig:
                    self.logger.error(f"   • Error original: {db_error.orig}")
                
                # Verificar si es un error de conexión
                if "connection" in str(db_error).lower():
                    self.logger.error("   • Posible problema de conexión a la base de datos")
                elif "permission" in str(db_error).lower() or "denied" in str(db_error).lower():
                    self.logger.error("   • Posible problema de permisos")
                elif "table" in str(db_error).lower() or "object" in str(db_error).lower():
                    self.logger.error("   • Posible problema con la tabla o objeto")
                elif "syntax" in str(db_error).lower():
                    self.logger.error("   • Posible error de sintaxis SQL")
                
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error actualizando FacturaCliente: {e}")
            return False
    
    def _guardar_cliente_en_bd(self, fila_data, datos_mensaje):
        """Guarda la información del cliente en la base de datos usando IdFactura e IdAseguradora"""
        try:
            self.logger.info("💾 Guardando cliente en base de datos...")
            
            # Extraer datos de la fila encontrada
            num_poliza = fila_data['poliza']
            num_dependiente = fila_data['dependiente']
            
            # Extraer IdFactura e IdAseguradora del mensaje RabbitMQ
            id_factura = datos_mensaje.get('IdFactura')
            id_aseguradora = datos_mensaje.get('IdAseguradora')
            
            self.logger.info(f"   📋 IdFactura: {id_factura}")
            self.logger.info(f"   📋 IdAseguradora: {id_aseguradora}")
            self.logger.info(f"   📋 NumPoliza: {num_poliza}")
            self.logger.info(f"   📋 NumDependiente: {num_dependiente}")
            
            if not id_factura or not id_aseguradora:
                self.logger.error("❌ Faltan IdFactura o IdAseguradora en los datos del mensaje")
                return False
            
            # Buscar si ya existe un registro con IdFactura e IdAseguradora
            query_buscar = """
                SELECT IdfacturaCliente, NumPoliza, NumDependiente 
                FROM [NeptunoMedicalAutomatico].[dbo].[FacturaCliente] 
                WHERE IdFactura = :id_factura AND IdAseguradora = :id_aseguradora
            """
            
            resultado = self.db_manager.execute_query(query_buscar, {
                'id_factura': id_factura, 
                'id_aseguradora': id_aseguradora
            })
            
            if resultado:
                # Actualizar registro existente
                self.logger.info("🔄 Actualizando registro existente...")
                
                query_update = """
                    UPDATE [NeptunoMedicalAutomatico].[dbo].[FacturaCliente] 
                    SET NumPoliza = :num_poliza, NumDependiente = :num_dependiente
                    WHERE IdFactura = :id_factura AND IdAseguradora = :id_aseguradora
                """
                
                self.db_manager.execute_query(query_update, {
                    'num_poliza': num_poliza, 
                    'num_dependiente': num_dependiente,
                    'id_factura': id_factura, 
                    'id_aseguradora': id_aseguradora
                })
                self.logger.info("✅ Registro actualizado exitosamente")
                
            else:
                # Insertar nuevo registro
                self.logger.info("➕ Insertando nuevo registro...")
                self._insertar_nuevo_cliente(datos_mensaje, num_poliza, num_dependiente)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error guardando cliente en base de datos: {e}")
            return False
    
    def _insertar_nuevo_cliente(self, datos_mensaje, num_poliza, num_dependiente):
        """Inserta un nuevo cliente en la base de datos"""
        try:
            # Generar ID único
            id_factura_cliente = str(uuid.uuid4())
            
            # Extraer datos del mensaje
            id_factura = datos_mensaje.get('IdFactura')
            id_aseguradora = datos_mensaje.get('IdAseguradora')
            num_doc_identidad = datos_mensaje.get('NumDocIdentidad')
            cliente_primer_nombre = datos_mensaje.get('ClientePersonaPrimerNombre')
            cliente_segundo_nombre = datos_mensaje.get('ClientePersonaSegundoNombre')
            cliente_primer_apellido = datos_mensaje.get('ClientePersonaPrimerApellido')
            cliente_segundo_apellido = datos_mensaje.get('ClientePersonaSegundoApellido')
            
            query_insert = """
                INSERT INTO [NeptunoMedicalAutomatico].[dbo].[FacturaCliente] 
                (IdfacturaCliente, IdFactura, IdAseguradora, NumDocIdentidad, 
                 ClientePersonaPrimerNombre, ClientePersonaSegundoNombre, 
                 ClientePersonaPrimerApellido, ClientePersonaSegundoApellido, 
                 NumPoliza, NumDependiente, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """
            
            params = (
                id_factura_cliente, id_factura, id_aseguradora, num_doc_identidad,
                cliente_primer_nombre, cliente_segundo_nombre,
                cliente_primer_apellido, cliente_segundo_apellido,
                num_poliza, num_dependiente
            )
            
            self.db_manager.execute_query(query_insert, params)
            self.logger.info("✅ Nuevo cliente insertado exitosamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error insertando nuevo cliente: {e}")
            raise
    
    def _buscar_elemento_con_reintento(self, driver, selector, descripcion):
        """Busca un elemento con reintento y recarga de página si es necesario"""
        try:
            for intento in range(1, 3):  # 2 intentos
                try:
                    self.logger.info(f"🔍 Buscando elemento '{descripcion}' (intento {intento}/2)...")
                    self.logger.info(f"   📍 Selector: {selector}")
                    
                    elemento = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    
                    self.logger.info(f"✅ Elemento '{descripcion}' encontrado en intento {intento}")
                    return elemento
                    
                except TimeoutException:
                    if intento < 2:
                        self.logger.warning(f"⚠️ Elemento '{descripcion}' no encontrado en intento {intento}, recargando página...")
                        driver.refresh()
                        time.sleep(5)
                    else:
                        self.logger.error(f"❌ Elemento '{descripcion}' no encontrado después de {intento} intentos")
                        raise
                        
        except Exception as e:
            self.logger.error(f"❌ Error buscando elemento '{descripcion}': {e}")
            raise
    
    def _buscar_boton_con_reintento(self, driver, selector, descripcion):
        """Busca un botón con reintento y recarga de página si es necesario"""
        try:
            for intento in range(1, 3):  # 2 intentos
                try:
                    self.logger.info(f"🔍 Buscando botón para '{descripcion}' (intento {intento}/2)...")
                    self.logger.info(f"   📍 Selector: {selector}")
                    
                    elemento = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    self.logger.info(f"✅ Botón para '{descripcion}' encontrado en intento {intento}")
                    return elemento
                    
                except TimeoutException:
                    if intento < 2:
                        self.logger.warning(f"⚠️ Botón '{descripcion}' no encontrado en intento {intento}, recargando página...")
                        driver.refresh()
                        time.sleep(5)
                    else:
                        self.logger.error(f"❌ Botón '{descripcion}' no encontrado después de {intento} intentos")
                        raise
                        
        except Exception as e:
            self.logger.error(f"❌ Error buscando botón '{descripcion}': {e}")
            raise

def crear_procesador_oauth2(db_manager):
    """Función factory para crear el procesador OAuth2"""
    return PanAmericanLifeEcuadorOAuth2Processor(db_manager)

