#!/usr/bin/env python3
"""
Implementación específica para PAN AMERICAN LIFE DE ECUADOR
Extiende la funcionalidad base del worker con lógica específica de esta aseguradora
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from .config import get_config_login, get_config_selenium, validar_configuracion

class PanAmericanLifeEcuadorProcessor:
    """Procesador específico para PAN AMERICAN LIFE DE ECUADOR"""
    
    def __init__(self):
        self.config = get_config_login()
        self.selenium_config = get_config_selenium()
        self.logger = logging.getLogger(__name__)
        
        # Validar configuración al inicializar
        errores = validar_configuracion()
        if errores:
            self.logger.error(f"❌ Configuración inválida para PAN AMERICAN LIFE DE ECUADOR: {errores}")
            raise ValueError(f"Configuración inválida: {errores}")
        
        self.logger.info("🚀 Procesador PAN AMERICAN LIFE DE ECUADOR inicializado correctamente")
    
    def procesar_login_especifico(self, driver):
        """Procesa el login específico para esta aseguradora"""
        try:
            self.logger.info("🔐 Iniciando login específico para PAN AMERICAN LIFE DE ECUADOR")
            
            # Navegar a la URL de login
            url_login = self.config['url']
            self.logger.info(f"🌐 Navegando a: {url_login}")
            driver.get(url_login)
            
            # Esperar a que la página cargue completamente
            self._esperar_carga_pagina(driver)
            
            # Procesar campos de login
            self._procesar_campos_login(driver)
            
            # Ejecutar acciones post-login
            self._ejecutar_acciones_post_login(driver)
            
            # Validar resultado del login
            return self._validar_login_exitoso(driver)
            
        except Exception as e:
            self.logger.error(f"❌ Error en login específico: {e}")
            return False
    
    def _esperar_carga_pagina(self, driver):
        """Espera a que la página cargue completamente"""
        try:
            timeout = self.config['timeouts']['carga_pagina']
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            self.logger.info("✅ Página cargada correctamente")
        except TimeoutException:
            self.logger.error(f"❌ Timeout esperando carga de página ({timeout}s)")
            raise
    
    def _procesar_campos_login(self, driver):
        """Procesa los campos de login en orden"""
        try:
            self.logger.info("🔐 Procesando campos de login...")
            
            for campo in self.config['campos']:
                selector = campo['selector']
                valor = campo['valor']
                descripcion = campo.get('descripcion', selector)
                
                self.logger.info(f"  📝 Procesando: {descripcion}")
                
                # Buscar el elemento
                elemento = self._buscar_elemento(driver, selector, campo.get('tipo', 'input'))
                
                if not elemento:
                    raise Exception(f"No se pudo encontrar el elemento: {selector}")
                
                # Limpiar y escribir valor
                elemento.clear()
                elemento.send_keys(valor)
                
                self.logger.info(f"    ✅ Campo {selector} completado con: {valor}")
                
                # Pequeña pausa entre campos
                time.sleep(0.5)
                
        except Exception as e:
            self.logger.error(f"❌ Error procesando campos de login: {e}")
            raise
    
    def _ejecutar_acciones_post_login(self, driver):
        """Ejecuta las acciones post-login en orden"""
        try:
            if not self.config['acciones']:
                self.logger.info("ℹ️  No hay acciones post-login definidas")
                return
            
            self.logger.info("🎯 Ejecutando acciones post-login...")
            
            for accion in self.config['acciones']:
                tipo = accion['tipo']
                selector = accion['selector']
                descripcion = accion.get('descripcion', selector)
                espera = accion.get('espera_despues', 2)
                
                self.logger.info(f"  🎯 Ejecutando: {descripcion}")
                
                # Buscar el elemento
                elemento = self._buscar_elemento_clicable(driver, selector)
                
                if not elemento:
                    raise Exception(f"No se pudo encontrar elemento clicable: {selector}")
                
                # Ejecutar acción según el tipo
                if tipo.lower() == 'click':
                    elemento.click()
                    self.logger.info(f"    ✅ Click ejecutado en: {selector}")
                elif tipo.lower() == 'submit':
                    elemento.submit()
                    self.logger.info(f"    ✅ Submit ejecutado en: {selector}")
                elif tipo.lower() == 'send_keys':
                    elemento.send_keys(accion.get('valor', ''))
                    self.logger.info(f"    ✅ Texto enviado a: {selector}")
                else:
                    self.logger.warning(f"    ⚠️  Tipo de acción no reconocido: {tipo}")
                
                # Esperar después de la acción
                if espera > 0:
                    self.logger.info(f"    ⏳ Esperando {espera}s después de la acción...")
                    time.sleep(espera)
                
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando acciones post-login: {e}")
            raise
    
    def _validar_login_exitoso(self, driver):
        """Valida si el login fue exitoso"""
        try:
            self.logger.info("🔍 Validando resultado del login...")
            
            # Esperar procesamiento del login
            espera = self.config['timeouts']['procesamiento_login']
            self.logger.info(f"⏳ Esperando {espera}s para procesamiento del login...")
            time.sleep(espera)
            
            # Obtener información de la página actual
            url_actual = driver.current_url
            titulo_pagina = driver.title
            
            self.logger.info(f"📍 URL actual: {url_actual}")
            self.logger.info(f"📄 Título de la página: {titulo_pagina}")
            
            # Validar según criterios configurados
            validaciones = self.config['validaciones']
            
            # Validar URL de éxito
            if validaciones.get('url_exito') and validaciones['url_exito'] in url_actual:
                self.logger.info("🎯 ¡URL de éxito detectada!")
                return True
            
            # Validar título de éxito
            if validaciones.get('titulo_exito') and validaciones['titulo_exito'] in titulo_pagina:
                self.logger.info("🎯 ¡Título de éxito detectado!")
                return True
            
            # Validar elementos esperados
            elementos_esperados = validaciones.get('elementos_esperados', [])
            for elemento in elementos_esperados:
                try:
                    driver.find_element(By.TAG_NAME, elemento)
                    self.logger.info(f"✅ Elemento esperado encontrado: {elemento}")
                except:
                    self.logger.warning(f"⚠️  Elemento esperado no encontrado: {elemento}")
            
            # Validar que no hay elementos de error
            elementos_no_esperados = validaciones.get('elementos_no_esperados', [])
            for elemento in elementos_no_esperados:
                try:
                    driver.find_element(By.XPATH, f"//*[contains(text(), '{elemento}')]")
                    self.logger.error(f"❌ Elemento de error detectado: {elemento}")
                    return False
                except:
                    pass  # Elemento de error no encontrado (es bueno)
            
            # Si llegamos aquí, consideramos el login exitoso
            self.logger.info("✅ Login validado como exitoso")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validando login: {e}")
            return False
    
    def _buscar_elemento(self, driver, selector, tipo='input'):
        """Busca un elemento en la página"""
        try:
            timeout = self.config['timeouts']['elemento_visible']
            
            if selector.startswith('#'):
                # Selector por ID
                elemento = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.ID, selector[1:]))
                )
            elif selector.startswith('.'):
                # Selector por clase
                elemento = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, selector[1:]))
                )
            elif selector.startswith('//'):
                # Selector XPath
                elemento = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            else:
                # Selector CSS por defecto
                elemento = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            
            return elemento
            
        except TimeoutException:
            self.logger.error(f"❌ Timeout buscando elemento: {selector}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error buscando elemento {selector}: {e}")
            return None
    
    def _buscar_elemento_clicable(self, driver, selector):
        """Busca un elemento clicable en la página"""
        try:
            timeout = self.config['timeouts']['elemento_clicable']
            
            if selector.startswith('#'):
                # Selector por ID
                elemento = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.ID, selector[1:]))
                )
            elif selector.startswith('.'):
                # Selector por clase
                elemento = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, selector[1:]))
                )
            elif selector.startswith('//'):
                # Selector XPath
                elemento = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            else:
                # Selector CSS por defecto
                elemento = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            
            return elemento
            
        except TimeoutException:
            self.logger.error(f"❌ Timeout buscando elemento clicable: {selector}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error buscando elemento clicable {selector}: {e}")
            return None
    
    def obtener_metricas_login(self, tiempo_inicio):
        """Calcula métricas del proceso de login"""
        tiempo_fin = time.time()
        tiempo_total = tiempo_fin - tiempo_inicio
        
        return {
            'tiempo_total': tiempo_total,
            'tiempo_inicio': tiempo_inicio,
            'tiempo_fin': tiempo_fin,
            'aseguradora': 'PAN AMERICAN LIFE DE ECUADOR',
            'codigo': 'PALE_EC'
        }
    
    def generar_reporte_login(self, resultado, metricas):
        """Genera un reporte del proceso de login"""
        reporte = {
            'fecha': time.strftime('%Y-%m-%d %H:%M:%S'),
            'aseguradora': 'PAN AMERICAN LIFE DE ECUADOR',
            'codigo': 'PALE_EC',
            'resultado': 'EXITOSO' if resultado else 'FALLIDO',
            'metricas': metricas,
            'configuracion_usada': {
                'url_login': self.config['url'],
                'campos_procesados': len(self.config['campos']),
                'acciones_ejecutadas': len(self.config['acciones']),
                'timeouts': self.config['timeouts']
            }
        }
        
        return reporte

# Función de fábrica para crear el procesador
def crear_procesador():
    """Crea y retorna una instancia del procesador"""
    return PanAmericanLifeEcuadorProcessor()

# Función para obtener información de la aseguradora
def get_info_aseguradora():
    """Retorna información básica de la aseguradora"""
    from .config import ASEGURADORA_INFO
    return ASEGURADORA_INFO

if __name__ == "__main__":
    # Prueba de la implementación
    try:
        procesador = crear_procesador()
        print("✅ Procesador creado correctamente")
        print(f"📋 Aseguradora: {get_info_aseguradora()['nombre']}")
        print(f"🔐 Campos de login: {len(procesador.config['campos'])}")
        print(f"🎯 Acciones post-login: {len(procesador.config['acciones'])}")
        
    except Exception as e:
        print(f"❌ Error creando procesador: {e}")
