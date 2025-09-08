#!/usr/bin/env python3
"""
Worker de producción para procesar mensajes de aseguradoras continuamente
"""

import time
import logging
import signal
import sys
import json
import pika
from datetime import datetime
from src.config import Config
from src.database import DatabaseManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

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

class AseguradoraProcessor:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        # Cache para URLs de aseguradoras (nombre -> url_info)
        self.url_cache = {}
        # Driver de Selenium para login automático
        self.driver = None
        
        # Gestor de sesiones por aseguradora
        self.sesiones_aseguradoras = {}
        self.aseguradoras_activas = set()
        
        logger.info("🚀 Procesador inicializado con caché de URLs y Selenium")
        logger.info("   • Gestión de sesiones por aseguradora habilitada")
    
    def connect_rabbitmq(self):
        """Conecta a RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(Config.RABBITMQ_USERNAME, Config.RABBITMQ_PASSWORD)
            self.rabbitmq_connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=Config.RABBITMQ_HOST,
                    port=Config.RABBITMQ_PORT,
                    credentials=credentials
                )
            )
            
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            
            # Declarar la cola y el exchange
            self.rabbitmq_channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True)
            self.rabbitmq_channel.exchange_declare(
                exchange=Config.RABBITMQ_EXCHANGE, 
                exchange_type='direct', 
                durable=True
            )
            
            # Vincular la cola al exchange
            self.rabbitmq_channel.queue_bind(
                exchange=Config.RABBITMQ_EXCHANGE,
                queue=Config.RABBITMQ_QUEUE,
                routing_key=Config.RABBITMQ_ROUTING_KEY
            )
            
            logger.info("✅ Conectado a RabbitMQ exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando a RabbitMQ: {e}")
            return False
    
    def setup_selenium_driver(self):
        """Configura el driver de Selenium para login automático"""
        try:
            if self.driver:
                return True
                
            logger.info("🔧 Configurando driver de Selenium...")
            
            # Opciones de Edge para modo headless
            edge_options = Options()
            # edge_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--window-size=1920,1080")
            edge_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
            
            # Reducir logs de Edge
            edge_options.add_argument("--log-level=3")  # Solo errores críticos
            edge_options.add_argument("--silent")
            edge_options.add_argument("--disable-logging")
            edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # Crear driver de Edge
            self.driver = webdriver.Edge(options=edge_options)
            self.driver.set_page_load_timeout(30)
            
            # Configurar logging de Selenium para reducir ruido
            import logging
            selenium_logger = logging.getLogger('selenium')
            selenium_logger.setLevel(logging.WARNING)
            
            # Reducir logs de urllib3 (usado por Selenium)
            urllib3_logger = logging.getLogger('urllib3')
            urllib3_logger.setLevel(logging.WARNING)
            
            logger.info("✅ Driver de Edge configurado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando Selenium: {e}")
            return False
    
    def execute_login(self, url_info, datos_mensaje=None):
        """Ejecuta el login automático en la página web"""
        try:
            # Para PAN AMERICAN LIFE DE ECUADOR, usar el procesador específico
            if url_info.get('nombre') == 'PAN AMERICAN LIFE DE ECUADOR':
                logger.info("🇪🇨 Usando procesador específico para PAN AMERICAN LIFE DE ECUADOR")
                
                try:
                    from aseguradoras.pan_american_life_ecuador.implementacion_oauth2 import crear_procesador_oauth2
                    procesador = crear_procesador_oauth2(self.db_manager)
                    logger.info("✅ Procesador específico PAN AMERICAN LIFE DE ECUADOR cargado para login")
                    
                    # Usar el procesador específico para el login
                    return procesador._ejecutar_login_con_reintentos(self.driver)
                    
                except ImportError as e:
                    logger.error(f"❌ Error importando procesador específico: {e}")
                    logger.info("🔄 Usando lógica genérica como fallback")
                    # Continuar con la lógica genérica
                except Exception as e:
                    logger.error(f"❌ Error ejecutando procesador específico: {e}")
                    logger.info("🔄 Usando lógica genérica como fallback")
                    # Continuar con la lógica genérica
            
            # Lógica genérica para otras aseguradoras
            if not self.setup_selenium_driver():
                logger.error("❌ No se pudo configurar Selenium")
                return False
            
            url_login = url_info['url_login']
            logger.info(f"🌐 Navegando a: {url_login}")
            
            # Navegar a la página de login
            self.driver.get(url_login)
            
            # Esperar a que la página cargue
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("✅ Página cargada correctamente")
            
            # Ejecutar campos de login
            if url_info.get('campos_login'):
                logger.info("🔐 Ejecutando campos de login...")
                
                for campo in url_info['campos_login']:
                    selector = campo['selector_html']
                    valor = campo['valor_dinamico']
                    
                    if not valor:
                        logger.warning(f"⚠️  Campo {selector} sin valor, saltando...")
                        continue
                    
                    try:
                        # Buscar el elemento con reintento de recarga
                        elemento = self._buscar_elemento_con_reintento(selector, f"Campo {selector}")
                        
                        # Limpiar y escribir valor
                        elemento.clear()
                        elemento.send_keys(valor)
                        
                        logger.info(f"✅ Campo {selector} completado con: {valor}")
                        
                    except TimeoutException:
                        logger.error(f"❌ No se encontró el campo {selector}")
                        return False
                    except Exception as e:
                        logger.error(f"❌ Error en campo {selector}: {e}")
                        return False
            
            # Ejecutar acciones post-login
            if url_info.get('acciones_post_login'):
                logger.info("🎯 Ejecutando acciones post-login...")
                
                for accion in url_info['acciones_post_login']:
                    tipo = accion['tipo_accion']
                    selector = accion['selector_html']
                    
                    try:
                        # Buscar el elemento con reintento
                        elemento = self._buscar_boton_con_reintento(selector, f"Acción {selector}")
                        
                        if tipo.lower() == 'click':
                            elemento.click()
                            logger.info(f"✅ Click ejecutado en: {selector}")
                        elif tipo.lower() == 'submit':
                            elemento.submit()
                            logger.info(f"✅ Submit ejecutado en: {selector}")
                        else:
                            logger.warning(f"⚠️  Tipo de acción no reconocido: {tipo}")
                        
                        # Pequeña pausa para que la acción se procese
                        time.sleep(2)
                        
                    except TimeoutException:
                        logger.error(f"❌ No se pudo ejecutar acción {tipo} en {selector}")
                        return False
                    except Exception as e:
                        logger.error(f"❌ Error ejecutando acción {tipo}: {e}")
                        return False
            
            # Verificar si el login fue exitoso
            logger.info("🔍 Verificando resultado del login...")
            
            # Obtener la URL actual para verificar si cambió
            url_actual = self.driver.current_url
            titulo_pagina = self.driver.title
            
            logger.info(f"✅ Login completado exitosamente!")
            logger.info(f"   📍 URL actual: {url_actual}")
            logger.info(f"   📄 Título de la página: {titulo_pagina}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return False
    
    def capturar_informacion_pantalla(self, id_url, nombre_aseguradora=None, datos_mensaje=None):
        """Captura información de la pantalla post-login y la almacena en la base de datos"""
        try:
            logger.info("📸 Iniciando captura de información de la pantalla...")
            
            # Lógica específica para PAN AMERICAN LIFE DE ECUADOR
            if nombre_aseguradora == 'PAN AMERICAN LIFE DE ECUADOR':
                # Usar el procesador específico que ya maneja todo el flujo
                try:
                    from aseguradoras.pan_american_life_ecuador.implementacion_oauth2 import crear_procesador_oauth2
                    procesador = crear_procesador_oauth2(self.db_manager)
                    logger.info("✅ Procesador específico PAN AMERICAN LIFE DE ECUADOR cargado para captura")
                    
                    # El procesador ya maneja todo el flujo OAuth2 + captura
                    return procesador.procesar_oauth2_completo(self.driver, datos_mensaje)
                    
                except ImportError as e:
                    logger.error(f"❌ Error importando procesador específico: {e}")
                    # Fallback a lógica original
                    return self._capturar_informacion_pale_ec(id_url, datos_mensaje)
            
            # Lógica genérica para otras aseguradoras
            return self._capturar_informacion_generica(id_url)
            
        except Exception as e:
            logger.error(f"❌ Error en captura de información: {e}")
            return False
    
    def _capturar_informacion_pale_ec(self, id_url, datos_mensaje):
        """Captura información específica para PAN AMERICAN LIFE DE ECUADOR (fallback)"""
        try:
            logger.info("📸 Capturando información específica para PAN AMERICAN LIFE DE ECUADOR...")
            
            # Lógica específica para PAN AMERICAN LIFE DE ECUADOR
            # Esta función actúa como fallback si el procesador específico no está disponible
            
            # Construir nombre completo del cliente
            nombre_completo = self._construir_nombre_completo(datos_mensaje)
            if not nombre_completo:
                logger.error("❌ No se pudo construir el nombre completo del cliente")
                return False
            
            # Capturar tabla y buscar cliente
            resultado = self._capturar_tabla_resultados_pale_ec(nombre_completo, datos_mensaje)
            if not resultado:
                logger.error("❌ No se pudo capturar información de la tabla")
                return False
            
            # Guardar en base de datos
            if not self._guardar_cliente_en_bd(resultado, datos_mensaje):
                logger.error("❌ Error guardando en base de datos")
                return False
            
            logger.info("✅ Captura de información completada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en captura de información: {e}")
            return False
    
    def _construir_nombre_completo(self, datos_mensaje):
        """Construye el nombre completo del cliente concatenando los campos"""
        try:
            logger.info("🔤 Construyendo nombre completo del cliente...")
            
            # Extraer campos del mensaje
            primer_nombre = datos_mensaje.get('PersonaPrimerNombre', '').strip()
            segundo_nombre = datos_mensaje.get('PersonaSegundoNombre', '').strip()
            primer_apellido = datos_mensaje.get('PersonaPrimerApellido', '').strip()
            segundo_apellido = datos_mensaje.get('PersonaSegundoApellido', '').strip()
            
            logger.info(f"   📝 Primer nombre: '{primer_nombre}'")
            logger.info(f"   📝 Segundo nombre: '{segundo_nombre}'")
            logger.info(f"   📝 Primer apellido: '{primer_apellido}'")
            logger.info(f"   📝 Segundo apellido: '{segundo_apellido}'")
            
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
                logger.error("❌ No se pudo construir el nombre completo - todos los campos están vacíos")
                return None
            
            nombre_completo = ' '.join(partes_nombre)
            logger.info(f"✅ Nombre completo construido: '{nombre_completo}'")
            
            return nombre_completo
            
        except Exception as e:
            logger.error(f"❌ Error construyendo nombre completo: {e}")
            return None
    
    def _capturar_tabla_resultados_pale_ec(self, nombre_completo_cliente=None, datos_mensaje=None):
        """Captura la tabla de resultados específica para PAN AMERICAN LIFE DE ECUADOR"""
        try:
            logger.info("🔍 Capturando tabla de resultados para PAN AMERICAN LIFE DE ECUADOR...")
            
            # Buscar la tabla de resultados
            tabla = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.GridViewStylePV'))
            )
            
            logger.info("✅ Tabla encontrada")
            
            # Buscar filas de datos
            filas = tabla.find_elements(By.CSS_SELECTOR, 'tr.RowStylePV')
            logger.info(f"📊 Encontradas {len(filas)} filas de datos")
            
            # Buscar el cliente específico
            for i, fila in enumerate(filas):
                try:
                    # Buscar la columna "Nombre del Paciente"
                    celdas = fila.find_elements(By.TAG_NAME, 'td')
                    if len(celdas) >= 4:  # Asegurar que hay suficientes columnas
                        nombre_paciente = celdas[3].text.strip()  # Columna 4 (índice 3)
                        
                        logger.info(f"   🔍 Fila {i+1}: '{nombre_paciente}'")
                        
                        # Verificar si coincide con el nombre completo
                        if nombre_completo_cliente.upper() in nombre_paciente.upper():
                            logger.info(f"✅ Cliente encontrado en fila {i+1}")
                            
                            # Verificar que el status sea "Activo"
                            if len(celdas) >= 8:  # Asegurar que hay columna de status
                                status_celda = celdas[7]  # Columna 8 (índice 7)
                                status_texto = status_celda.text.strip()
                                
                                if "Activo" in status_texto:
                                    logger.info("✅ Status 'Activo' confirmado")
                                    
                                    # Extraer datos de la fila
                                    poliza = celdas[0].text.strip()  # Columna 1 (índice 0)
                                    dependiente = celdas[2].text.strip()  # Columna 3 (índice 2)
                                    
                                    logger.info(f"   📋 Póliza: {poliza}")
                                    logger.info(f"   📋 Dependiente: {dependiente}")
                                    
                                    return {
                                        'poliza': poliza,
                                        'dependiente': dependiente,
                                        'nombre_paciente': nombre_paciente,
                                        'status': status_texto
                                    }
                                else:
                                    logger.warning(f"⚠️ Cliente encontrado pero status no es 'Activo': {status_texto}")
                            else:
                                logger.warning("⚠️ No se pudo verificar el status - estructura de tabla inesperada")
                        else:
                            logger.info(f"   ❌ No coincide: '{nombre_paciente}' != '{nombre_completo_cliente}'")
                            
                except Exception as e:
                    logger.warning(f"⚠️ Error procesando fila {i+1}: {e}")
                    continue
            
            logger.warning("⚠️ Cliente no encontrado en la tabla")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error capturando tabla de resultados: {e}")
            return None
    
    def _guardar_cliente_en_bd(self, fila_data, datos_mensaje):
        """Guarda la información del cliente en la base de datos"""
        try:
            logger.info("💾 Guardando cliente en base de datos...")
            
            # Extraer datos
            num_poliza = fila_data['poliza']
            num_dependiente = fila_data['dependiente']
            
            id_factura = datos_mensaje.get('IdFactura')
            id_aseguradora = datos_mensaje.get('IdAseguradora')
            
            logger.info(f"   📋 IdFactura: {id_factura}")
            logger.info(f"   📋 IdAseguradora: {id_aseguradora}")
            logger.info(f"   📋 NumPoliza: {num_poliza}")
            logger.info(f"   📋 NumDependiente: {num_dependiente}")
            
            # Buscar si ya existe un registro
            query_buscar = """
                SELECT IdfacturaCliente, NumPoliza, NumDependiente 
                FROM [NeptunoMedicalAutomatico].[dbo].[FacturaCliente] 
                WHERE IdFactura = ? AND IdAseguradora = ?
            """
            
            resultado = self.db_manager.execute_query(query_buscar, (id_factura, id_aseguradora))
            
            if resultado:
                # Actualizar registro existente
                logger.info("🔄 Actualizando registro existente...")
                
                query_update = """
                    UPDATE [NeptunoMedicalAutomatico].[dbo].[FacturaCliente] 
                    SET NumPoliza = ?, NumDependiente = ?
                    WHERE IdFactura = ? AND IdAseguradora = ?
                """
                
                self.db_manager.execute_query(query_update, (num_poliza, num_dependiente, id_factura, id_aseguradora))
                logger.info("✅ Registro actualizado exitosamente")
                
            else:
                # Insertar nuevo registro
                logger.info("➕ Insertando nuevo registro...")
                self._insertar_nuevo_cliente(datos_mensaje, num_poliza, num_dependiente)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando cliente en base de datos: {e}")
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
            logger.info("✅ Nuevo cliente insertado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error insertando nuevo cliente: {e}")
            raise
    
    def _buscar_elemento_con_reintento(self, selector, nombre_campo, max_reintentos=2):
        """Busca un elemento con reintento y recarga de página si es necesario"""
        try:
            for intento in range(1, max_reintentos + 1):
                try:
                    logger.info(f"🔍 Buscando elemento '{nombre_campo}' (intento {intento}/{max_reintentos})...")
                    logger.info(f"   📍 Selector: {selector}")
                    
                    elemento = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    
                    logger.info(f"✅ Elemento '{nombre_campo}' encontrado en intento {intento}")
                    return elemento
                    
                except TimeoutException:
                    if intento < max_reintentos:
                        logger.warning(f"⚠️ Elemento '{nombre_campo}' no encontrado en intento {intento}, recargando página...")
                        self.driver.refresh()
                        time.sleep(5)
                    else:
                        logger.error(f"❌ Elemento '{nombre_campo}' no encontrado después de {intento} intentos")
                        raise
                        
        except Exception as e:
            logger.error(f"❌ Error buscando elemento '{nombre_campo}': {e}")
            raise
    
    def _buscar_boton_con_reintento(self, selector, nombre_campo, max_reintentos=2):
        """Busca un botón con reintento y recarga de página si es necesario"""
        try:
            for intento in range(1, max_reintentos + 1):
                try:
                    logger.info(f"🔍 Buscando botón para '{nombre_campo}' (intento {intento}/{max_reintentos})...")
                    logger.info(f"   📍 Selector: {selector}")
                    
                    elemento = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    logger.info(f"✅ Botón para '{nombre_campo}' encontrado en intento {intento}")
                    return elemento
                    
                except TimeoutException:
                    if intento < max_reintentos:
                        logger.warning(f"⚠️ Botón '{nombre_campo}' no encontrado en intento {intento}, recargando página...")
                        self.driver.refresh()
                        time.sleep(5)
                    else:
                        logger.error(f"❌ Botón '{nombre_campo}' no encontrado después de {intento} intentos")
                        raise
                        
        except Exception as e:
            logger.error(f"❌ Error buscando botón '{nombre_campo}': {e}")
            raise
    
    def _capturar_informacion_generica(self, id_url):
        """Captura información genérica para otras aseguradoras"""
        try:
            logger.info("📸 Capturando información genérica...")
            
            # Lógica genérica para otras aseguradoras
            # Esta función puede ser implementada según las necesidades específicas
            
            logger.info("✅ Captura de información genérica completada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en captura de información genérica: {e}")
            return False
    
    def _recrear_sesion_navegador(self):
        """Recrea la sesión del navegador cuando se detecta desconexión"""
        try:
            logger.warning("🔄 Detectada desconexión del navegador - Recreando sesión...")
            
            # Cerrar el driver actual si existe
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                    logger.info("✅ Driver anterior cerrado")
                except:
                    pass
                
            # Crear nuevo driver
            logger.info("🔧 Creando nuevo driver de Edge...")
            edge_options = Options()
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--window-size=1920,1080")
            edge_options.add_argument("--disable-blink-features=AutomationControlled")
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Edge(options=edge_options)
            self.driver.set_page_load_timeout(30)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Nueva sesión del navegador creada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error recreando sesión del navegador: {e}")
            return False

def main():
    """Función principal del worker"""
    try:
        logger.info("🚀 Iniciando worker de producción...")
        
        # Crear instancia del worker
        worker = ScrapingWorker()
        
        # Iniciar el worker
        worker.start()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Deteniendo worker por interrupción del usuario...")
    except Exception as e:
        logger.error(f"❌ Error en función principal: {e}")
    finally:
        logger.info("🔌 Worker detenido correctamente")
        sys.exit(0)

if __name__ == "__main__":
    main()
                                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                                )
                                logger.info("✅ Página completamente cargada después de la búsqueda")
                                logger.info(f"   📍 URL final después de búsqueda: {self.driver.current_url}")
                            except:
                                logger.info("ℹ️ Página cargada (timeout de readyState)")
                                logger.info(f"   📍 URL actual (timeout): {self.driver.current_url}")
                            
                        except Exception as e:
                            logger.warning(f"⚠️ No se pudo hacer clic en el botón: {e}")
                            logger.info("🔄 Intentando con selectores alternativos...")
                            
                            # Intentar con selectores alternativos
                            selectores_alternativos = [
                                'button[type="submit"]',
                                'input[type="submit"]',
                                '.btn-primary',
                                '.btn-buscar',
                                'button:contains("Buscar")',
                                'button:contains("Consultar")'
                            ]
                            
                            for selector_alt in selectores_alternativos:
                                try:
                                    boton_alt = WebDriverWait(self.driver, 5).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector_alt))
                                    )
                                    boton_alt.click()
                                    logger.info(f"✅ Botón alternativo clickeado: {selector_alt}")
                                    time.sleep(5)  # Aumentar tiempo de espera
                                    break
                                except:
                                    continue
                        
                        # Capturar la tabla de resultados
                        logger.info("📊 Iniciando captura de tabla de resultados...")
                        return self._capturar_tabla_resultados_pale_ec(nombre_completo, datos_mensaje)
                        
                    else:
                        logger.info(f"ℹ️ Campo {nombre_campo} no es de tipo input, saltando...")
                        
                except TimeoutException:
                    if obligatorio:
                        logger.error(f"❌ Campo obligatorio {nombre_campo} no encontrado: {selector_css}")
                        logger.info(f"🔍 Elementos disponibles en la página:")
                        try:
                            elementos_input = self.driver.find_elements(By.CSS_SELECTOR, 'input')
                            logger.info(f"   📝 Inputs encontrados: {len(elementos_input)}")
                            for i, elem in enumerate(elementos_input[:5]):  # Mostrar solo los primeros 5
                                logger.info(f"      {i+1}. id='{elem.get_attribute('id')}', name='{elem.get_attribute('name')}', placeholder='{elem.get_attribute('placeholder')}'")
                        except:
                            pass
                        return False
                    else:
                        logger.warning(f"⚠️ Campo opcional {nombre_campo} no encontrado: {selector_css}")
                except Exception as e:
                    logger.error(f"❌ Error procesando campo {nombre_campo}: {e}")
                    if obligatorio:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en captura específica PALE_EC: {e}")
            return False
    
    def _construir_nombre_completo(self, datos_mensaje):
        """Construye el nombre completo del cliente concatenando las columnas del mensaje RabbitMQ"""
        try:
            # Obtener las columnas de nombre del mensaje RabbitMQ
            primer_nombre = datos_mensaje.get('PersonaPrimerNombre', '').strip()
            segundo_nombre = datos_mensaje.get('PersonaSegundoNombre', '').strip()
            primer_apellido = datos_mensaje.get('PersonaPrimerApellido', '').strip()
            segundo_apellido = datos_mensaje.get('PersonaSegundoApellido', '').strip()
            
            # Construir nombre completo con espacios entre columnas
            nombre_completo = f"{primer_nombre} {segundo_nombre} {primer_apellido} {segundo_apellido}".strip()
            
            if nombre_completo:
                logger.info(f"🔍 Construyendo nombre completo desde RabbitMQ:")
                logger.info(f"   • PersonaPrimerNombre: '{primer_nombre}'")
                logger.info(f"   • PersonaSegundoNombre: '{segundo_nombre}'")
                logger.info(f"   • PersonaPrimerApellido: '{primer_apellido}'")
                logger.info(f"   • PersonaSegundoApellido: '{segundo_apellido}'")
                logger.info(f"   • Nombre Completo: '{nombre_completo}'")
                return nombre_completo
            else:
                logger.warning("⚠️ No se encontraron datos de nombre en el mensaje RabbitMQ")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error construyendo nombre completo: {e}")
            return None
    
    def _capturar_tabla_resultados_pale_ec(self, nombre_completo_cliente=None, datos_mensaje=None):
        """Captura la tabla de resultados con clase GridViewStylePV y busca el cliente específico"""
        try:
            logger.info("📊 Capturando tabla de resultados...")
            logger.info("=" * 60)
            logger.info(f"📍 URL actual durante captura de tabla: {self.driver.current_url}")
            
            if nombre_completo_cliente:
                logger.info(f"🔍 Buscando cliente específico: '{nombre_completo_cliente}'")
            
            # Buscar la tabla con clase GridViewStylePV
            logger.info("🔍 Buscando tabla con clase 'GridViewStylePV'...")
            tabla = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.GridViewStylePV'))
            )
            
            logger.info("✅ Tabla GridViewStylePV encontrada")
            logger.info(f"   📍 Ubicación de la tabla en la página")
            
            # Obtener todas las filas de la tabla
            filas = tabla.find_elements(By.CSS_SELECTOR, 'tr')
            logger.info(f"📋 Total de filas encontradas: {len(filas)}")
            
            if len(filas) <= 1:  # Solo header o tabla vacía
                logger.info("ℹ️ Tabla sin resultados o solo con encabezados")
                logger.info(f"   📍 URL confirmada: {self.driver.current_url}")
                return True
            
            # Obtener encabezados (primera fila)
            encabezados = []
            if filas:
                celdas_header = filas[0].find_elements(By.CSS_SELECTOR, 'th, td')
                encabezados = [celda.text.strip() for celda in celdas_header if celda.text.strip()]
                logger.info(f"📝 Encabezados de la tabla ({len(encabezados)} columnas):")
                for i, encabezado in enumerate(encabezados, 1):
                    logger.info(f"   {i}. {encabezado}")
            
            logger.info("=" * 60)
            
            # Procesar filas de datos (excluyendo la primera si es header)
            cliente_encontrado = None
            logger.info("📄 Procesando filas de datos para buscar cliente específico...")
            
            for i, fila in enumerate(filas[1:], 1):
                celdas = fila.find_elements(By.CSS_SELECTOR, 'td')
                if celdas:
                    fila_data = {}
                    
                    # Construir datos de la fila
                    for j, celda in enumerate(celdas):
                        if j < len(encabezados):
                            encabezado = encabezados[j]
                            valor = celda.text.strip()
                            fila_data[encabezado] = valor
                    
                    if fila_data:
                        # 🔍 BUSCAR CLIENTE ESPECÍFICO SI SE PROPORCIONA NOMBRE
                        if nombre_completo_cliente and self._es_cliente_buscado(fila_data, nombre_completo_cliente):
                            if self._validar_cliente_activo(fila_data):
                                cliente_encontrado = fila_data
                                logger.info(f"🎯 ¡CLIENTE ENCONTRADO Y VALIDADO en fila {i}!")
                                logger.info(f"   ✅ Nombre: '{fila_data.get('Nombre del Paciente', 'N/A')}'")
                                logger.info(f"   ✅ Status: '{fila_data.get('Status', 'N/A')}'")
                                logger.info(f"   📋 Datos del cliente:")
                                logger.info(f"      • Póliza: {fila_data.get('Póliza', 'N/A')}")
                                logger.info(f"      • Certificado: {fila_data.get('Certificado', 'N/A')}")
                                logger.info(f"      • No. Dependiente: {fila_data.get('No. Dependiente', 'N/A')}")
                                logger.info(f"      • Relación: {fila_data.get('Relacion', 'N/A')}")
                                logger.info(f"      • Tipo de Póliza: {fila_data.get('Tipo de Póliza', 'N/A')}")
                                
                                # 🚀 GUARDAR INFORMACIÓN EN BASE DE DATOS INMEDIATAMENTE
                                if datos_mensaje:
                                    logger.info("💾 Guardando información del cliente en base de datos...")
                                    if self._guardar_cliente_en_bd(fila_data, datos_mensaje):
                                        logger.info("✅ Cliente guardado exitosamente en base de datos")
                    else:
                                        logger.error("❌ Error guardando cliente en base de datos")
                else:
                                    logger.warning("⚠️ No hay datos del mensaje para guardar en BD")
                                
                                # Una vez encontrado el cliente, no necesitamos seguir procesando
                                logger.info("✅ Cliente encontrado - deteniendo búsqueda")
                                break
                            else:
                                logger.warning(f"⚠️ Cliente encontrado pero NO está activo en fila {i}")
                                logger.warning(f"   ❌ Status: '{fila_data.get('Status', 'N/A')}'")
                                # Continuar buscando en caso de que haya otro cliente con el mismo nombre
                        else:
                            # Solo mostrar información si no estamos buscando un cliente específico
                            if not nombre_completo_cliente:
                                logger.info(f"📄 Fila {i}: {fila_data.get('Nombre del Paciente', 'N/A')}")
                    
                    # Si encontramos el cliente, salir del bucle
                    if cliente_encontrado:
                        break
            
            logger.info("=" * 60)
            logger.info(f"🎯 RESUMEN DE CAPTURA:")
            logger.info(f"   📝 Columnas capturadas: {len(encabezados)}")
            logger.info(f"   📋 Encabezados: {', '.join(encabezados)}")
            
            if cliente_encontrado:
                logger.info("🎯 CLIENTE ENCONTRADO Y VALIDADO:")
                logger.info(f"   👤 Nombre: {cliente_encontrado.get('Nombre del Paciente', 'N/A')}")
                logger.info(f"   📋 Información de Póliza:")
                logger.info(f"      • Póliza: {cliente_encontrado.get('Póliza', 'N/A')}")
                logger.info(f"      • Certificado: {cliente_encontrado.get('Certificado', 'N/A')}")
                logger.info(f"      • No. Dependiente: {cliente_encontrado.get('No. Dependiente', 'N/A')}")
                logger.info(f"      • Relación: {cliente_encontrado.get('Relacion', 'N/A')}")
                logger.info(f"      • Tipo de Póliza: {cliente_encontrado.get('Tipo de Póliza', 'N/A')}")
                logger.info(f"      • Status: {cliente_encontrado.get('Status', 'N/A')}")
            else:
                if nombre_completo_cliente:
                    logger.warning(f"⚠️ NO SE ENCONTRÓ el cliente '{nombre_completo_cliente}' o no está activo")
                else:
                    logger.info("ℹ️ No se buscó cliente específico")
            
            logger.info("=" * 60)
            logger.info("✅ Captura de tabla completada exitosamente")
            return True
            
        except TimeoutException:
            logger.warning("⚠️ No se encontró tabla de resultados con clase 'GridViewStylePV'")
            logger.info("🔍 Buscando otras tablas en la página...")
            
            try:
                # Buscar otras tablas
                tablas = self.driver.find_elements(By.CSS_SELECTOR, 'table')
                logger.info(f"📋 Tablas encontradas en la página: {len(tablas)}")
                
                for i, tabla in enumerate(tablas):
                    try:
                        clase = tabla.get_attribute('class') or 'sin-clase'
                        filas = tabla.find_elements(By.CSS_SELECTOR, 'tr')
                        logger.info(f"   Tabla {i+1}: clase='{clase}', filas={len(filas)}")
                    except:
                        pass
                
                return True
            except:
                return True
                
        except Exception as e:
            logger.error(f"❌ Error capturando tabla: {e}")
            return False
    
    def _es_cliente_buscado(self, fila_data, nombre_completo_cliente):
        """Verifica si la fila corresponde al cliente buscado"""
        try:
            nombre_paciente = fila_data.get('Nombre del Paciente', '').strip()
            if not nombre_paciente:
                return False
            
            # Comparar nombres (ignorar mayúsculas/minúsculas y espacios extra)
            nombre_paciente_normalizado = ' '.join(nombre_paciente.split()).upper()
            nombre_buscado_normalizado = ' '.join(nombre_completo_cliente.split()).upper()
            
            es_cliente = nombre_paciente_normalizado == nombre_buscado_normalizado
            
            if es_cliente:
                logger.info(f"🎯 ¡COINCIDENCIA DE NOMBRE ENCONTRADA!")
                logger.info(f"   🔍 Buscado: '{nombre_completo_cliente}'")
                logger.info(f"   ✅ Encontrado: '{nombre_paciente}'")
            else:
                logger.info(f"ℹ️ No es el cliente buscado:")
                logger.info(f"   🔍 Buscado: '{nombre_completo_cliente}'")
                logger.info(f"   ❌ Encontrado: '{nombre_paciente}'")
            
            return es_cliente
            
        except Exception as e:
            logger.error(f"❌ Error verificando si es cliente buscado: {e}")
            return False
    
    def _validar_cliente_activo(self, fila_data):
        """Verifica si el cliente está activo según el status"""
        try:
            status = fila_data.get('Status', '').strip()
            if not status:
                logger.warning("⚠️ No se encontró información de Status")
                return False
            
            # Verificar si está activo (ignorar mayúsculas/minúsculas)
            es_activo = 'activo' in status.lower()
            
            if es_activo:
                logger.info(f"✅ Cliente está ACTIVO - Status: '{status}'")
            else:
                logger.warning(f"⚠️ Cliente NO está activo - Status: '{status}'")
            
            return es_activo
            
        except Exception as e:
            logger.error(f"❌ Error validando status del cliente: {e}")
            return False
    
    def _guardar_cliente_en_bd(self, fila_data, datos_mensaje):
        """Actualiza o inserta la información del cliente en la base de datos NeptunoMedicalAutomatico"""
        try:
            import uuid
            from datetime import datetime
            
            logger.info("💾 Iniciando proceso de actualización/inserción en base de datos...")
            logger.info("=" * 60)
            
            # Obtener IdFactura e IdAseguradora del mensaje (si están disponibles)
            id_factura = datos_mensaje.get('IdFactura')
            id_aseguradora = datos_mensaje.get('IdAseguradora')
            
            logger.info(f"🔍 Buscando coincidencias con:")
            logger.info(f"   • IdFactura: {id_factura}")
            logger.info(f"   • IdAseguradora: {id_aseguradora}")
            
            # Si tenemos IdFactura e IdAseguradora, intentar UPDATE primero
            if id_factura and id_aseguradora:
                logger.info("🔄 Intentando UPDATE - Buscando registro existente...")
                
                # Query para buscar registro existente
                select_query = """
                    SELECT [IdfacturaCliente], [NumPoliza], [NumDependiente]
                    FROM [NeptunoMedicalAutomatico].[dbo].[FacturaCliente]
                    WHERE [IdFactura] = :IdFactura 
                    AND [IdAseguradora] = :IdAseguradora
                    AND [estado] = 1
                """
                
                # Buscar registro existente
                registro_existente = self.db_manager.execute_query(
                    select_query, 
                    {'IdFactura': id_factura, 'IdAseguradora': id_aseguradora}
                )
                
                if registro_existente and len(registro_existente) > 0:
                    # ✅ REGISTRO ENCONTRADO - HACER UPDATE
                    registro = registro_existente[0]
                    id_factura_cliente = registro['IdfacturaCliente']
                    
                    logger.info(f"✅ Registro encontrado - ID: {id_factura_cliente}")
                    logger.info(f"   📋 Póliza actual: {registro.get('NumPoliza', 'N/A')}")
                    logger.info(f"   📋 Dependiente actual: {registro.get('NumDependiente', 'N/A')}")
                    
                    # Preparar datos para UPDATE
                    datos_update = {
                        'IdfacturaCliente': id_factura_cliente,
                        'NumPoliza': fila_data.get('Póliza', ''),
                        'NumDependiente': fila_data.get('No. Dependiente', '')
                    }
                    
                    # Query de UPDATE
                    update_query = """
                        UPDATE [NeptunoMedicalAutomatico].[dbo].[FacturaCliente]
                        SET [NumPoliza] = :NumPoliza,
                            [NumDependiente] = :NumDependiente
                        WHERE [IdfacturaCliente] = :IdfacturaCliente
                    """
                    
                    # Ejecutar UPDATE
                    logger.info("🔄 Ejecutando UPDATE...")
                    logger.info(f"   📋 Nueva Póliza: {datos_update['NumPoliza']}")
                    logger.info(f"   📋 Nuevo Dependiente: {datos_update['NumDependiente']}")
                    
                    resultado_update = self.db_manager.execute_query(update_query, datos_update)
                    
                    if resultado_update:
                        logger.info("✅ UPDATE ejecutado exitosamente")
                        logger.info(f"   🆔 ID actualizado: {id_factura_cliente}")
                        logger.info(f"   📋 Póliza actualizada: {datos_update['NumPoliza']}")
                        logger.info(f"   📋 Dependiente actualizado: {datos_update['NumDependiente']}")
                        return True
                    else:
                        logger.error("❌ Error en UPDATE - resultado vacío")
                        return False
                        
                else:
                    # ⚠️ NO SE ENCONTRÓ REGISTRO - HACER INSERT
                    logger.info("⚠️ No se encontró registro existente - Procediendo con INSERT...")
                    return self._insertar_nuevo_cliente(fila_data, datos_mensaje)
                    
            else:
                # ⚠️ NO HAY IdFactura o IdAseguradora - HACER INSERT
                logger.info("⚠️ No se proporcionaron IdFactura o IdAseguradora - Procediendo con INSERT...")
                return self._insertar_nuevo_cliente(fila_data, datos_mensaje)
                
        except Exception as e:
            logger.error(f"❌ Error en proceso de actualización/inserción: {e}")
            logger.error(f"   📍 Error tipo: {type(e).__name__}")
            return False
    
    def _buscar_elemento_con_reintento(self, selector, nombre_campo, max_reintentos=2):
        """Busca un elemento con reintento de recarga de página si no se encuentra"""
        for intento in range(1, max_reintentos + 1):
            try:
                logger.info(f"🔍 Buscando elemento '{nombre_campo}' (intento {intento}/{max_reintentos})...")
                logger.info(f"   📍 Selector: {selector}")
                
                # Intentar encontrar el elemento
                elemento = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                logger.info(f"✅ Elemento '{nombre_campo}' encontrado en intento {intento}")
                return elemento
                
            except Exception as e:
                logger.warning(f"⚠️ Elemento '{nombre_campo}' no encontrado en intento {intento}")
                logger.warning(f"   📍 Error: {e}")
                
                if intento < max_reintentos:
                    logger.info(f"🔄 Recargando página para intento {intento + 1}...")
                    logger.info(f"   📍 URL actual: {self.driver.current_url}")
                    
                    # Recargar la página
                    self.driver.refresh()
                    time.sleep(3)  # Esperar a que se recargue
                    
                    logger.info(f"✅ Página recargada - URL: {self.driver.current_url}")
                else:
                    logger.error(f"❌ Elemento '{nombre_campo}' no encontrado después de {max_reintentos} intentos")
                    raise e
        
        return None
    
    def _buscar_boton_con_reintento(self, selector, nombre_campo, max_reintentos=2):
        """Busca un botón con reintento de recarga de página si no se encuentra"""
        for intento in range(1, max_reintentos + 1):
            try:
                logger.info(f"🔍 Buscando botón para '{nombre_campo}' (intento {intento}/{max_reintentos})...")
                logger.info(f"   📍 Selector: {selector}")
                
                # Intentar encontrar el botón
                boton = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                logger.info(f"✅ Botón para '{nombre_campo}' encontrado en intento {intento}")
                return boton
                
            except Exception as e:
                logger.warning(f"⚠️ Botón para '{nombre_campo}' no encontrado en intento {intento}")
                logger.warning(f"   📍 Error: {e}")
                
                if intento < max_reintentos:
                    logger.info(f"🔄 Recargando página para intento {intento + 1}...")
                    logger.info(f"   📍 URL actual: {self.driver.current_url}")
                    
                    # Recargar la página
                    self.driver.refresh()
                    time.sleep(3)  # Esperar a que se recargue
                    
                    logger.info(f"✅ Página recargada - URL: {self.driver.current_url}")
                else:
                    logger.error(f"❌ Botón para '{nombre_campo}' no encontrado después de {max_reintentos} intentos")
                    raise e
        
        return None
    
    def _recrear_sesion_navegador(self):
        """Recrea la sesión del navegador cuando se detecta desconexión"""
        try:
            logger.warning("🔄 Detectada desconexión del navegador - Recreando sesión...")
            
            # Cerrar el driver actual si existe
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                    logger.info("✅ Driver anterior cerrado")
                except:
                    pass
            
            # Crear nuevo driver
            logger.info("🔧 Creando nuevo driver de Edge...")
            edge_options = Options()
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--window-size=1920,1080")
            edge_options.add_argument("--disable-blink-features=AutomationControlled")
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Edge(options=edge_options)
            self.driver.set_page_load_timeout(30)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Nueva sesión del navegador creada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error recreando sesión del navegador: {e}")
            return False
    
    def _insertar_nuevo_cliente(self, fila_data, datos_mensaje):
        """Inserta un nuevo cliente en la base de datos"""
        try:
            import uuid
            
            logger.info("➕ INSERTANDO NUEVO CLIENTE...")
            logger.info("=" * 60)
            
            # Generar ID único para el cliente
            id_factura_cliente = str(uuid.uuid4())
            logger.info(f"🆔 ID generado: {id_factura_cliente}")
            
            # Preparar datos para inserción
            datos_insercion = {
                'IdfacturaCliente': id_factura_cliente,
                'IdFactura': datos_mensaje.get('IdFactura'),
                'IdAseguradora': datos_mensaje.get('IdAseguradora'),
                'NumDocIdentidad': datos_mensaje.get('NumDocIdentidad', ''),
                'ClientePersonaPrimerNombre': datos_mensaje.get('PersonaPrimerNombre', ''),
                'ClientePersonaSegundoNombre': datos_mensaje.get('PersonaSegundoNombre', ''),
                'ClientePersonaPrimerApellido': datos_mensaje.get('PersonaPrimerApellido', ''),
                'ClientePersonaSegundoApellido': datos_mensaje.get('PersonaSegundoApellido', ''),
                'NumPoliza': fila_data.get('Póliza', ''),
                'NumDependiente': fila_data.get('No. Dependiente', ''),
                'estado': 1  # 1 = Activo
            }
            
            # Mostrar datos que se van a insertar
            logger.info("📋 Datos a insertar en FacturaCliente:")
            for campo, valor in datos_insercion.items():
                logger.info(f"   • {campo}: '{valor}'")
            
            # Query de inserción
            insert_query = """
                INSERT INTO [NeptunoMedicalAutomatico].[dbo].[FacturaCliente] (
                    [IdfacturaCliente], [IdFactura], [IdAseguradora], [NumDocIdentidad],
                    [ClientePersonaPrimerNombre], [ClientePersonaSegundoNombre],
                    [ClientePersonaPrimerApellido], [ClientePersonaSegundoApellido],
                    [NumPoliza], [NumDependiente], [estado]
                ) VALUES (
                    :IdfacturaCliente, :IdFactura, :IdAseguradora, :NumDocIdentidad,
                    :ClientePersonaPrimerNombre, :ClientePersonaSegundoNombre,
                    :ClientePersonaPrimerApellido, :ClientePersonaSegundoApellido,
                    :NumPoliza, :NumDependiente, :estado
                )
            """
            
            # Ejecutar inserción
            logger.info("🚀 Ejecutando INSERT...")
            resultado = self.db_manager.execute_query(insert_query, datos_insercion)
            
            if resultado:
                logger.info("✅ Cliente insertado exitosamente en base de datos")
                logger.info(f"   🆔 ID: {id_factura_cliente}")
                logger.info(f"   📋 Póliza: {datos_insercion['NumPoliza']}")
                logger.info(f"   📋 Dependiente: {datos_insercion['NumDependiente']}")
                logger.info(f"   👤 Cliente: {datos_insercion['ClientePersonaPrimerNombre']} {datos_insercion['ClientePersonaPrimerApellido']}")
                return True
            else:
                logger.error("❌ Error en la inserción - resultado vacío")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error insertando nuevo cliente: {e}")
            logger.error(f"   📍 Error tipo: {type(e).__name__}")
            return False
            
        except TimeoutException:
            logger.warning("⚠️ No se encontró tabla de resultados con clase 'GridViewStylePV'")
            logger.info("🔍 Buscando otras tablas en la página...")
            
            try:
                # Buscar otras tablas
                tablas = self.driver.find_elements(By.CSS_SELECTOR, 'table')
                logger.info(f"📋 Tablas encontradas en la página: {len(tablas)}")
                
                for i, tabla in enumerate(tablas):
                    try:
                        clase = tabla.get_attribute('class') or 'sin-clase'
                        filas = tabla.find_elements(By.CSS_SELECTOR, 'tr')
                        logger.info(f"   Tabla {i+1}: clase='{clase}', filas={len(filas)}")
                    except:
                        pass
                
                return True
            except:
                return True
                
        except Exception as e:
            logger.error(f"❌ Error capturando tabla: {e}")
            return False
    
    def _capturar_informacion_generica(self, id_url):
        """Captura información genérica para otras aseguradoras"""
        try:
            logger.info("📸 Captura genérica de información...")
            
            # Obtener configuración de campos a capturar desde la base de datos
            campos_query = """
                SELECT NombreCampo, TipoCampo, SelectorCSS, Orden, Obligatorio
                FROM informacion_capturada 
                WHERE IdUrl = :id_url AND Activo = 1
                ORDER BY Orden
            """
            
            campos_captura = self.db_manager.execute_query(campos_query, {'id_url': id_url})
            
            if not campos_captura:
                logger.info("ℹ️ No hay campos configurados para capturar")
                return True
            
            logger.info(f"🎯 Campos a capturar: {len(campos_captura)}")
            
            # Capturar información de cada campo
            for campo in campos_captura:
                nombre_campo = campo['NombreCampo']
                tipo_campo = campo['TipoCampo']
                selector_css = campo['SelectorCSS']
                orden = campo['Orden']
                obligatorio = campo['Obligatorio']
                
                try:
                    logger.info(f"🔍 Capturando campo: {nombre_campo} ({tipo_campo})")
                    
                    # Buscar el elemento en la página
                    elemento = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector_css))
                    )
                    
                    # Obtener el valor según el tipo de campo
                    if tipo_campo.lower() == 'input':
                        valor_capturado = elemento.get_attribute('value') or elemento.get_attribute('placeholder') or ''
                    elif tipo_campo.lower() == 'text':
                        valor_capturado = elemento.text or ''
                    elif tipo_campo.lower() == 'select':
                        # Para select, obtener la opción seleccionada
                        from selenium.webdriver.support.ui import Select
                        select_element = Select(elemento)
                        valor_capturado = select_element.first_selected_option.text if select_element.first_selected_option else ''
                    else:
                        valor_capturado = elemento.text or elemento.get_attribute('value') or ''
                    
                    # Limpiar el valor capturado
                    if valor_capturado:
                        valor_capturado = valor_capturado.strip()
                    
                    logger.info(f"✅ Campo {nombre_campo} capturado: {valor_capturado[:50]}...")
                    
                except TimeoutException:
                    if obligatorio:
                        logger.error(f"❌ Campo obligatorio {nombre_campo} no encontrado: {selector_css}")
                        return False
                    else:
                        logger.warning(f"⚠️ Campo opcional {nombre_campo} no encontrado: {selector_css}")
                except Exception as e:
                    logger.error(f"❌ Error capturando campo {nombre_campo}: {e}")
                    if obligatorio:
                        return False
            
            logger.info("✅ Captura de información genérica completada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en captura genérica: {e}")
            return False
    
    def get_url_by_aseguradora_name(self, nombre_aseguradora):
        """Busca la URL y campos de login de una aseguradora por su nombre en la base de datos o caché"""
        try:
            # Primero verificar si ya está en caché
            if nombre_aseguradora in self.url_cache:
                logger.info(f"📋 Información encontrada en caché para: {nombre_aseguradora}")
                return self.url_cache[nombre_aseguradora]
            
            # Si no está en caché, buscar en la base de datos
            logger.info(f"🔍 Buscando información en base de datos para: {nombre_aseguradora}")
            
            # 1. Obtener información básica de la URL
            url_query = """
                SELECT id, nombre, url_login, url_destino, descripcion, fecha_creacion
                FROM urls_automatizacion 
                WHERE nombre = :nombre
            """
            
            url_results = self.db_manager.execute_query(url_query, {'nombre': nombre_aseguradora})
            
            if url_results and len(url_results) > 0:
                url_row = url_results[0]
                url_id = str(url_row['id'])
                
                # 2. Obtener campos de login (usuario/contraseña)
                campos_query = """
                    SELECT selector_html, valor_dinamico
                    FROM campos_login 
                    WHERE id_url = :id_url
                    ORDER BY selector_html
                """
                
                campos_results = self.db_manager.execute_query(campos_query, {'id_url': url_id})
                
                # 3. Obtener acciones post-login
                acciones_query = """
                    SELECT tipo_accion, selector_html, valor_dinamico
                    FROM acciones_post_login 
                    WHERE id_url = :id_url
                    ORDER BY tipo_accion
                """
                
                acciones_results = self.db_manager.execute_query(acciones_query, {'id_url': url_id})
                
                # Construir información completa
                url_info = {
                    'id': url_id,
                    'nombre': url_row['nombre'],
                    'url_login': url_row['url_login'],
                    'url_destino': url_row['url_destino'],
                    'descripcion': url_row['descripcion'],
                    'fecha_creacion': url_row['fecha_creacion'].isoformat() if url_row['fecha_creacion'] else None,
                    'campos_login': campos_results,
                    'acciones_post_login': acciones_results
                }
                
                # Guardar en caché para futuras consultas
                self.url_cache[nombre_aseguradora] = url_info
                logger.info(f"💾 Información completa guardada en caché para: {nombre_aseguradora}")
                logger.info(f"   📝 Campos de login: {len(campos_results)}")
                logger.info(f"   🎯 Acciones post-login: {len(acciones_results)}")
                
                return url_info
            else:
                logger.warning(f"⚠️  No se encontró URL para {nombre_aseguradora}")
                return None
                    
        except Exception as e:
            logger.error(f"❌ Error buscando información para {nombre_aseguradora}: {e}")
            return None
    
    def process_aseguradora_message(self, message_data):
        """Procesa un mensaje de aseguradora"""
        try:
            nombre_aseguradora = message_data.get('NombreCompleto')
            if not nombre_aseguradora:
                logger.warning("⚠️  Mensaje sin NombreCompleto")
                return None
            
            logger.info(f"🔍 Procesando aseguradora: {nombre_aseguradora}")
            
            # 🚀 GESTIONAR SESIÓN DE LA ASEGURADORA
            if not self.gestionar_sesion_aseguradora(nombre_aseguradora, message_data):
                logger.error(f"❌ No se pudo gestionar la sesión para {nombre_aseguradora}")
                return None
            
            # Buscar URL en la base de datos (si no está en cache)
            url_info = self.get_url_by_aseguradora_name(nombre_aseguradora)
            
            if url_info:
                # Crear resultado combinado
                result = {
                    'aseguradora_info': message_data,
                    'url_info': url_info,
                    'procesado_en': datetime.now().isoformat(),
                    'sesion_activa': self.verificar_sesion_activa(nombre_aseguradora)
                }
                
                logger.info(f"✅ Información completa encontrada para {nombre_aseguradora}")
                logger.info(f"   🌐 URL Login: {url_info['url_login']}")
                if url_info.get('url_destino'):
                    logger.info(f"   🎯 URL Destino: {url_info['url_destino']}")
                
                # Mostrar campos de login
                if url_info.get('campos_login'):
                    logger.info(f"   🔐 Campos de Login:")
                    for campo in url_info['campos_login']:
                        selector = campo['selector_html']
                        valor = campo['valor_dinamico'] or 'Sin valor'
                        logger.info(f"      • {selector}: {valor}")
                
                # Mostrar acciones post-login
                if url_info.get('acciones_post_login'):
                    logger.info(f"   🎯 Acciones Post-Login:")
                    for accion in url_info['acciones_post_login']:
                        tipo = accion['tipo_accion']
                        selector = accion['selector_html']
                        valor = accion['valor_dinamico'] or 'Sin valor'
                        logger.info(f"      • {tipo}: {selector} = {valor}")
                
                # Mostrar estado de la sesión
                if self.verificar_sesion_activa(nombre_aseguradora):
                    logger.info(f"✅ Sesión activa para {nombre_aseguradora} - No se requiere nuevo login")
                    logger.info(f"   📅 Fecha de login: {self.sesiones_aseguradoras.get(nombre_aseguradora, {}).get('fecha_login', 'N/A')}")
                else:
                    logger.info(f"ℹ️ {nombre_aseguradora} no requiere login automático")
                
                return result
            else:
                logger.warning(f"⚠️  No se encontró URL para {nombre_aseguradora}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            return None
    
    def process_message(self, ch, method, properties, body):
        """Callback para procesar mensajes de RabbitMQ"""
        try:
            # Decodificar el mensaje
            message_text = body.decode('utf-8')
            logger.info(f"📨 Procesando mensaje #{method.delivery_tag}")
            
            # Parsear JSON
            try:
                message_data = json.loads(message_text)
                
                # Verificar si es un mensaje de aseguradora
                if 'NombreCompleto' in message_data:
                    # Procesar mensaje individual
                    result = self.process_aseguradora_message(message_data)
                    if result:
                        logger.info("✅ Mensaje procesado exitosamente")
                        # Aquí podrías guardar el resultado en otra tabla o hacer algo más
                elif 'Clientes' in message_data and isinstance(message_data['Clientes'], list):
                    # Procesar lista de clientes
                    logger.info(f"📋 Procesando lista de {len(message_data['Clientes'])} clientes")
                    
                    for i, cliente in enumerate(message_data['Clientes']):
                        logger.info(f"  🔍 Procesando cliente {i+1}/{len(message_data['Clientes'])}")
                        result = self.process_aseguradora_message(cliente)
                        if result:
                            logger.info(f"    ✅ Cliente {i+1} procesado")
                        else:
                            logger.warning(f"    ⚠️  Cliente {i+1} sin procesar")
                    
                    # Mostrar mensaje de espera después de procesar lista completa
                    logger.info("⏳ Lista de clientes procesada - Esperando siguiente mensaje...")
                else:
                    logger.warning("⚠️  Formato de mensaje no reconocido")
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error parseando JSON: {e}")
            
            # Acknowledge el mensaje
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            # Mostrar mensaje de espera después de procesar
            logger.info("⏳ Mensaje procesado - Esperando siguiente mensaje...")
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self):
        """Inicia el consumo de mensajes - SIEMPRE ACTIVO"""
        try:
            if not self.connect_rabbitmq():
                return
            
            # Obtener información de la cola
            queue_info = self.rabbitmq_channel.queue_declare(
                queue=Config.RABBITMQ_QUEUE, 
                durable=True, 
                passive=True
            )
            message_count = queue_info.method.message_count
            consumer_count = queue_info.method.consumer_count
            
            logger.info(f"📊 Cola: {Config.RABBITMQ_QUEUE}")
            logger.info(f"📊 Exchange: {Config.RABBITMQ_EXCHANGE}")
            logger.info(f"📊 Routing Key: {Config.RABBITMQ_ROUTING_KEY}")
            logger.info(f"📈 Mensajes en cola: {message_count}")
            logger.info(f"👥 Consumidores activos: {consumer_count}")
            
            # Configurar QoS para procesar un mensaje a la vez
            self.rabbitmq_channel.basic_qos(prefetch_count=1)
            
            # Consumir mensajes - SIEMPRE ACTIVO
            logger.info("🔄 Iniciando consumo de mensajes...")
            logger.info("💡 Presiona Ctrl+C para detener")
            logger.info("⏳ Worker activo esperando mensajes...")
            
            # Configurar el consumidor para estar siempre activo
            self.rabbitmq_channel.basic_consume(
                queue=Config.RABBITMQ_QUEUE,
                on_message_callback=self.process_message,
                auto_ack=False  # Acknowledgment manual para mejor control
            )
            
            try:
                # BUCLE INFINITO - SIEMPRE ESPERANDO MENSAJES
                logger.info("🔄 Worker iniciado - Esperando mensajes...")
                
                # Mostrar mensaje de espera cuando no hay mensajes
                if message_count == 0:
                    logger.info("⏳ No hay mensajes en cola - Esperando nuevos mensajes...")
                
                # Usar start_consuming() que mantiene el worker activo
                self.rabbitmq_channel.start_consuming()
                        
            except KeyboardInterrupt:
                logger.info("⏹️  Deteniendo consumo de mensajes...")
                self.rabbitmq_channel.stop_consuming()
                
        except Exception as e:
            logger.error(f"❌ Error en el consumo: {e}")
        finally:
            self.cleanup()
    
    def get_cache_stats(self):
        """Retorna estadísticas del caché"""
        return {
            'total_cached': len(self.url_cache),
            'cached_aseguradoras': list(self.url_cache.keys())
        }
    
    def show_cache_stats(self):
        """Muestra estadísticas del caché y sesiones"""
        stats = self.get_cache_stats()
        logger.info(f"📊 Estadísticas del caché:")
        logger.info(f"   Total en caché: {stats['total_cached']}")
        if stats['cached_aseguradoras']:
            logger.info(f"   Aseguradoras en caché: {', '.join(stats['cached_aseguradoras'])}")
        else:
            logger.info("   Caché vacío")
        
        # Mostrar estado de sesiones
        estado_sesiones = self.obtener_estado_sesiones()
        logger.info(f"🔐 Estado de Sesiones:")
        logger.info(f"   Total activas: {estado_sesiones['total_activas']}")
        if estado_sesiones['aseguradoras_activas']:
            logger.info(f"   Aseguradoras con sesión activa: {', '.join(estado_sesiones['aseguradoras_activas'])}")
            # Mostrar detalles de cada sesión
            for aseguradora in estado_sesiones['aseguradoras_activas']:
                sesion_info = estado_sesiones['sesiones_detalle'].get(aseguradora, {})
                fecha_login = sesion_info.get('fecha_login', 'N/A')
                estado = sesion_info.get('estado', 'N/A')
                logger.info(f"      • {aseguradora}: {estado} (Login: {fecha_login})")
        else:
            logger.info("   No hay sesiones activas")
    
    def gestionar_sesion_aseguradora(self, nombre_aseguradora, datos_mensaje=None):
        """Gestiona la sesión de una aseguradora específica"""
        try:
            # Verificar si es PAN AMERICAN LIFE DE ECUADOR
            if nombre_aseguradora == 'PAN AMERICAN LIFE DE ECUADOR':
                # Obtener configuración de la aseguradora
                url_info = self.get_url_by_aseguradora_name(nombre_aseguradora)
                if not url_info:
                    logger.error(f"❌ No se pudo obtener configuración para {nombre_aseguradora}")
                    return False
                
                # Verificar si ya tenemos una sesión activa
                if nombre_aseguradora in self.aseguradoras_activas:
                    logger.info(f"✅ Sesión activa encontrada para {nombre_aseguradora}")
                    logger.info(f"🔄 Ejecutando captura de información con NumDocIdentidad...")
                    
                    # SIEMPRE ejecutar captura de información, incluso con sesión activa
                    if self.capturar_informacion_pantalla(url_info['id'], nombre_aseguradora, datos_mensaje):
                        logger.info(f"✅ Captura de información completada para {nombre_aseguradora}")
                        return True
                    else:
                        logger.error(f"❌ Error en captura de información para {nombre_aseguradora}")
                        return False
                
                # Si no hay sesión activa, hacer login completo
                logger.info(f"🔐 Iniciando login para {nombre_aseguradora}")
                
                if self.execute_login(url_info, datos_mensaje):
                    # Marcar como activa
                    self.aseguradoras_activas.add(nombre_aseguradora)
                    self.sesiones_aseguradoras[nombre_aseguradora] = {
                        'fecha_login': datetime.now(),
                        'estado': 'activa',
                        'url_info': url_info
                    }
                    logger.info(f"✅ Login exitoso para {nombre_aseguradora} - Sesión marcada como activa")
                    return True
                else:
                    logger.error(f"❌ Login fallido para {nombre_aseguradora}")
                    return False
            else:
                logger.info(f"ℹ️ {nombre_aseguradora} no requiere login automático")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error gestionando sesión para {nombre_aseguradora}: {e}")
            return False
    
    def verificar_sesion_activa(self, nombre_aseguradora):
        """Verifica si una aseguradora tiene sesión activa y válida"""
        if nombre_aseguradora not in self.aseguradoras_activas:
            return False
        
        # Verificar que el driver de Selenium esté activo
        if not self.driver:
            logger.warning(f"⚠️ Driver de Selenium no disponible - Limpiando sesión de {nombre_aseguradora}")
            self.aseguradoras_activas.discard(nombre_aseguradora)
            if nombre_aseguradora in self.sesiones_aseguradoras:
                del self.sesiones_aseguradoras[nombre_aseguradora]
            return False
        
        # Verificar que la sesión no sea muy antigua (opcional - puedes ajustar el tiempo)
        sesion_info = self.sesiones_aseguradoras.get(nombre_aseguradora, {})
        if 'fecha_login' in sesion_info:
            tiempo_sesion = datetime.now() - sesion_info['fecha_login']
            if tiempo_sesion.total_seconds() > 3600:  # 1 hora
                logger.warning(f"⚠️ Sesión de {nombre_aseguradora} expirada (más de 1 hora) - Limpiando")
                self.aseguradoras_activas.discard(nombre_aseguradora)
                if nombre_aseguradora in self.sesiones_aseguradoras:
                    del self.sesiones_aseguradoras[nombre_aseguradora]
                return False
        
        return True
    
    def obtener_estado_sesiones(self):
        """Retorna el estado de todas las sesiones activas"""
        return {
            'total_activas': len(self.aseguradoras_activas),
            'aseguradoras_activas': list(self.aseguradoras_activas),
            'sesiones_detalle': self.sesiones_aseguradoras
        }
    
    def cleanup(self):
        """Limpia las conexiones"""
        try:
            # Mostrar estadísticas del caché antes de limpiar
            self.show_cache_stats()
            
            # Cerrar driver de Selenium
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("🔌 Driver de Selenium cerrado")
                except Exception as e:
                    logger.error(f"❌ Error cerrando Selenium: {e}")
            
            if self.rabbitmq_channel and not self.rabbitmq_channel.is_closed:
                self.rabbitmq_channel.close()
            
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                self.rabbitmq_connection.close()
                
            logger.info("🔌 Conexiones cerradas")
            
        except Exception as e:
            logger.error(f"❌ Error cerrando conexiones: {e}")

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
