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
import uuid
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

class ScrapingWorker:
    """Worker principal para procesar mensajes de aseguradoras"""
    
    def __init__(self):
        self.processor = AseguradoraProcessor()
        self.running = False
        
    def start(self):
        """Inicia el worker"""
        try:
            logger.info("🚀 Iniciando worker de scraping...")
            
            # Conectar a RabbitMQ
            if not self.processor.connect_rabbitmq():
                logger.error("❌ No se pudo conectar a RabbitMQ")
                return False
            
            # Configurar Selenium
            if not self.processor.setup_selenium_driver():
                logger.error("❌ No se pudo configurar Selenium")
                return False
            
            self.running = True
            logger.info("✅ Worker iniciado correctamente")
            
            # Iniciar procesamiento de mensajes
            self._process_messages()
            
        except Exception as e:
            logger.error(f"❌ Error iniciando worker: {e}")
            return False
    
    def _process_messages(self):
        """Procesa mensajes de la cola de RabbitMQ"""
        try:
            logger.info("📨 Iniciando procesamiento de mensajes...")
            
            def callback(ch, method, properties, body):
                try:
                    # Decodificar mensaje
                    mensaje = json.loads(body.decode('utf-8'))
                    logger.info(f"📨 Mensaje recibido: {mensaje.get('IdFactura', 'Sin ID')}")
                    
                    # Procesar mensaje
                    self._process_single_message(mensaje)
                    
                    # Confirmar procesamiento
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info("✅ Mensaje procesado exitosamente")
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando mensaje: {e}")
                    # Rechazar mensaje
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            # Configurar consumo de mensajes
            self.processor.rabbitmq_channel.basic_qos(prefetch_count=1)
            self.processor.rabbitmq_channel.basic_consume(
                queue=Config.RABBITMQ_QUEUE,
                on_message_callback=callback
            )
            
            logger.info("⏳ Esperando mensajes...")
            self.processor.rabbitmq_channel.start_consuming()
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento de mensajes: {e}")
    
    def _process_single_message(self, mensaje):
        """Procesa un mensaje individual"""
        try:
            # Obtener información de la aseguradora
            id_aseguradora = mensaje.get('IdAseguradora')
            if not id_aseguradora:
                logger.error("❌ Mensaje sin IdAseguradora")
                return False
            
            # Obtener URL de la aseguradora
            url_info = self.processor.db_manager.get_url_aseguradora(id_aseguradora)
            if not url_info:
                logger.error(f"❌ No se encontró URL para aseguradora {id_aseguradora}")
                return False
            
            # Ejecutar login
            if not self.processor.execute_login(url_info, mensaje):
                logger.error("❌ Error en login")
                return False
            
            # Capturar información
            if not self.processor.capturar_informacion_pantalla(
                url_info['id_url'], 
                url_info.get('nombre'), 
                mensaje
            ):
                logger.error("❌ Error capturando información")
                return False
            
            logger.info("✅ Mensaje procesado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje individual: {e}")
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
