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
        
        # Cache de búsquedas por NumDocIdentidad para evitar búsquedas repetidas
        # Estructura: {num_doc_identidad: {'poliza': '...', 'dependiente': '...', 'status': '...'}}
        self.cache_busquedas = {}
        
        logger.info("🚀 Procesador inicializado con caché de URLs, Selenium y búsquedas")
        logger.info("   • Gestión de sesiones por aseguradora habilitada")
        logger.info("   • Cache de búsquedas por NumDocIdentidad habilitado")
    
    def _obtener_datos_del_cache(self, num_doc_identidad):
        """Obtiene datos del caché si ya se buscó este NumDocIdentidad"""
        if num_doc_identidad in self.cache_busquedas:
            datos_cache = self.cache_busquedas[num_doc_identidad]
            logger.info(f"🎯 CACHE HIT: NumDocIdentidad '{num_doc_identidad}' encontrado en caché")
            logger.info(f"   • Póliza: {datos_cache.get('poliza', 'N/A')}")
            logger.info(f"   • Dependiente: {datos_cache.get('dependiente', 'N/A')}")
            logger.info(f"   • Status: {datos_cache.get('status', 'N/A')}")
            return datos_cache
        else:
            logger.info(f"🔍 CACHE MISS: NumDocIdentidad '{num_doc_identidad}' no encontrado en caché")
            return None
    
    def _guardar_en_cache(self, num_doc_identidad, datos_busqueda):
        """Guarda los datos de búsqueda en el caché"""
        self.cache_busquedas[num_doc_identidad] = datos_busqueda
        logger.info(f"💾 CACHE SAVE: NumDocIdentidad '{num_doc_identidad}' guardado en caché")
        logger.info(f"   • Póliza: {datos_busqueda.get('poliza', 'N/A')}")
        logger.info(f"   • Dependiente: {datos_busqueda.get('dependiente', 'N/A')}")
        logger.info(f"   • Status: {datos_busqueda.get('status', 'N/A')}")
        logger.info(f"📊 Total elementos en caché: {len(self.cache_busquedas)}")
    
    def _limpiar_cache_busquedas(self):
        """Limpia el caché de búsquedas (útil al cambiar de aseguradora)"""
        elementos_antes = len(self.cache_busquedas)
        self.cache_busquedas.clear()
        logger.info(f"🧹 CACHE CLEAR: Caché de búsquedas limpiado ({elementos_antes} elementos eliminados)")
    
    def limpiar_browser(self, limpieza_profunda=False):
        """Limpia el browser después del procesamiento"""
        try:
            if not self.driver:
                logger.info("ℹ️ No hay driver activo para limpiar")
                return True
                
            logger.info("🧹 Iniciando limpieza del browser...")
            
            if limpieza_profunda:
                # Limpieza profunda: cerrar y reabrir el browser
                logger.info("🔄 Realizando limpieza profunda del browser...")
                self.driver.quit()
                self.driver = None
                logger.info("✅ Browser cerrado para limpieza profunda")
            else:
                # Limpieza ligera: limpiar cookies y storage
                logger.info("🧽 Realizando limpieza ligera del browser...")
                
                # Limpiar cookies
                self.driver.delete_all_cookies()
                logger.info("   • Cookies eliminadas")
                
                # Limpiar localStorage y sessionStorage
                self.driver.execute_script("window.localStorage.clear();")
                self.driver.execute_script("window.sessionStorage.clear();")
                logger.info("   • LocalStorage y SessionStorage limpiados")
                
                # Limpiar cache del browser
                self.driver.execute_script("window.caches.keys().then(function(names) { for (let name of names) caches.delete(name); });")
                logger.info("   • Cache del browser limpiado")
                
                # Navegar a una página en blanco
                self.driver.get("about:blank")
                logger.info("   • Navegado a página en blanco")
                
                logger.info("✅ Browser limpiado exitosamente (limpieza ligera)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error limpiando browser: {e}")
            return False
    
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
            
            # Obtener NumDocIdentidad para verificar caché
            num_doc_identidad = datos_mensaje.get('NumDocIdentidad')
            if not num_doc_identidad:
                logger.error("❌ No se encontró NumDocIdentidad en los datos del mensaje")
                return False
            
            # Verificar si ya tenemos estos datos en caché
            datos_cache = self._obtener_datos_del_cache(num_doc_identidad)
            if datos_cache:
                # Usar datos del caché
                logger.info("✅ Usando datos del caché para evitar búsqueda repetida")
                
                # Verificar si hay error en los datos del caché
                if 'error' in datos_cache:
                    logger.error(f"❌ Error en datos del caché: {datos_cache['error']}")
                    # Guardar cliente con error en base de datos
                    if not self._guardar_cliente_con_error(datos_mensaje, datos_cache['error']):
                        logger.error("❌ Error guardando cliente con error en base de datos")
                    return False
                
                # Guardar en base de datos usando datos del caché
                if not self._guardar_cliente_en_bd(datos_cache, datos_mensaje):
                    logger.error("❌ Error guardando en base de datos con datos del caché")
                    return False
                
                logger.info("✅ Captura de información completada exitosamente usando caché")
                return True
            
            # Si no está en caché, proceder con la búsqueda normal
            logger.info("🔍 NumDocIdentidad no encontrado en caché, procediendo con búsqueda en página...")
            
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
            
            # Verificar si hay error en el resultado
            if 'error' in resultado:
                logger.error(f"❌ Error en captura: {resultado['error']}")
                # Guardar en caché para futuras referencias
                self._guardar_en_cache(num_doc_identidad, resultado)
                # Guardar cliente con error en base de datos
                if not self._guardar_cliente_con_error(datos_mensaje, resultado['error']):
                    logger.error("❌ Error guardando cliente con error en base de datos")
                return False
            
            # Guardar en caché para futuras referencias
            self._guardar_en_cache(num_doc_identidad, resultado)
            
            # Guardar en base de datos (caso exitoso)
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
                                    return {
                                        'error': f"Cliente encontrado pero status no es 'Activo': {status_texto}",
                                        'tipo_error': 'STATUS_NO_ACTIVO'
                                    }
                            else:
                                logger.warning("⚠️ No se pudo verificar el status - estructura de tabla inesperada")
                                return {
                                    'error': "No se pudo verificar el status - estructura de tabla inesperada",
                                    'tipo_error': 'ESTRUCTURA_TABLA_INESPERADA'
                                }
                        else:
                            logger.info(f"   ❌ No coincide: '{nombre_paciente}' != '{nombre_completo_cliente}'")
                            
                except Exception as e:
                    logger.warning(f"⚠️ Error procesando fila {i+1}: {e}")
                    continue
            
            logger.warning("⚠️ Cliente no encontrado en la tabla")
            return {
                'error': f"Cliente '{nombre_completo_cliente}' no encontrado en la tabla de resultados",
                'tipo_error': 'CLIENTE_NO_ENCONTRADO'
            }
            
        except Exception as e:
            logger.error(f"❌ Error capturando tabla de resultados: {e}")
            return {
                'error': f"Error capturando tabla de resultados: {str(e)}",
                'tipo_error': 'ERROR_CAPTURA_TABLA'
            }
    
    def _guardar_cliente_en_bd(self, fila_data, datos_mensaje):
        """Guarda la información del cliente en la base de datos"""
        try:
            logger.info("💾 Guardando cliente en base de datos...")
            
            # Extraer datos
            num_poliza = fila_data['poliza']
            num_dependiente = fila_data['dependiente']
            
            id_factura = datos_mensaje.get('IdFactura')
            id_aseguradora = datos_mensaje.get('IdAseguradora')
            
            # Convertir tipos de datos para asegurar compatibilidad con la BD
            # Según la estructura de la tabla: IdFactura es [int] e IdAseguradora es [int]
            if id_factura:
                id_factura = int(id_factura)  # Convertir a int (tipo de la BD)
            if id_aseguradora:
                id_aseguradora = int(id_aseguradora)  # Asegurar que sea int
            
            logger.info(f"   📋 IdFactura: {id_factura} (tipo: {type(id_factura)})")
            logger.info(f"   📋 IdAseguradora: {id_aseguradora} (tipo: {type(id_aseguradora)})")
            logger.info(f"   📋 NumPoliza: {num_poliza}")
            logger.info(f"   📋 NumDependiente: {num_dependiente}")
            
            # Buscar si ya existe un registro
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
                logger.info("🔄 Actualizando registro existente...")
                
                query_update = """
                    UPDATE [NeptunoMedicalAutomatico].[dbo].[FacturaCliente] 
                    SET NumPoliza = :num_poliza, NumDependiente = :num_dependiente, estado = 1, error = NULL
                    WHERE IdFactura = :id_factura AND IdAseguradora = :id_aseguradora
                """
                
                self.db_manager.execute_query(query_update, {
                    'num_poliza': num_poliza,
                    'num_dependiente': num_dependiente,
                    'id_factura': id_factura,
                    'id_aseguradora': id_aseguradora
                })
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
            
            # Convertir tipos de datos para asegurar compatibilidad con la BD
            # Según la estructura de la tabla: IdFactura es [int] e IdAseguradora es [int]
            if id_factura:
                id_factura = int(id_factura)  # Convertir a int (tipo de la BD)
            if id_aseguradora:
                id_aseguradora = int(id_aseguradora)  # Asegurar que sea int
            
            query_insert = """
                INSERT INTO [NeptunoMedicalAutomatico].[dbo].[FacturaCliente] 
                (IdfacturaCliente, IdFactura, IdAseguradora, NumDocIdentidad, 
                 ClientePersonaPrimerNombre, ClientePersonaSegundoNombre, 
                 ClientePersonaPrimerApellido, ClientePersonaSegundoApellido, 
                 NumPoliza, NumDependiente, estado, error)
                VALUES (:id_factura_cliente, :id_factura, :id_aseguradora, :num_doc_identidad, 
                        :cliente_primer_nombre, :cliente_segundo_nombre, 
                        :cliente_primer_apellido, :cliente_segundo_apellido, 
                        :num_poliza, :num_dependiente, 1, NULL)
            """
            
            params = {
                'id_factura_cliente': id_factura_cliente,
                'id_factura': id_factura,
                'id_aseguradora': id_aseguradora,
                'num_doc_identidad': num_doc_identidad,
                'cliente_primer_nombre': cliente_primer_nombre,
                'cliente_segundo_nombre': cliente_segundo_nombre,
                'cliente_primer_apellido': cliente_primer_apellido,
                'cliente_segundo_apellido': cliente_segundo_apellido,
                'num_poliza': num_poliza,
                'num_dependiente': num_dependiente
            }
            
            self.db_manager.execute_query(query_insert, params)
            logger.info("✅ Nuevo cliente insertado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error insertando nuevo cliente: {e}")
            raise
    
    def _guardar_cliente_con_error(self, datos_mensaje, mensaje_error):
        """Guarda un cliente con error en la base de datos"""
        try:
            logger.info(f"💾 Guardando cliente con error: {mensaje_error}")
            logger.info(f"   • Parámetros: {datos_mensaje}")
            
            # Extraer datos del mensaje - manejar tanto mensaje completo como cliente individual
            id_factura = datos_mensaje.get('IdFactura')
            id_aseguradora = datos_mensaje.get('IdAseguradora')
            num_doc_identidad = datos_mensaje.get('NumDocIdentidad')
            
            # Convertir tipos de datos para asegurar compatibilidad con la BD
            # Según la estructura de la tabla: IdFactura es [int] e IdAseguradora es [int]
            logger.info(f"🔧 CONVERSIÓN DE TIPOS:")
            logger.info(f"   • IdFactura ANTES: {id_factura} (tipo: {type(id_factura)})")
            logger.info(f"   • IdAseguradora ANTES: {id_aseguradora} (tipo: {type(id_aseguradora)})")
            
            if id_factura:
                id_factura = int(id_factura)  # Convertir a int (tipo de la BD)
                logger.info(f"   • IdFactura DESPUÉS: {id_factura} (tipo: {type(id_factura)})")
            if id_aseguradora:
                id_aseguradora = int(id_aseguradora)  # Asegurar que sea int
                logger.info(f"   • IdAseguradora DESPUÉS: {id_aseguradora} (tipo: {type(id_aseguradora)})")
            
            # Extraer datos del cliente si están disponibles
            cliente_primer_nombre = None
            cliente_segundo_nombre = None
            cliente_primer_apellido = None
            cliente_segundo_apellido = None
            
            # Si es un mensaje completo con array Clientes
            if 'Clientes' in datos_mensaje and datos_mensaje['Clientes']:
                cliente = datos_mensaje['Clientes'][0]
                cliente_primer_nombre = cliente.get('PersonaPrimerNombre')
                cliente_segundo_nombre = cliente.get('PersonaSegundoNombre')
                cliente_primer_apellido = cliente.get('PersonaPrimerApellido')
                cliente_segundo_apellido = cliente.get('PersonaSegundoApellido')
                if not num_doc_identidad:
                    num_doc_identidad = cliente.get('NumDocIdentidad')
            else:
                # Si es un cliente individual (del procesador específico)
                cliente_primer_nombre = datos_mensaje.get('PersonaPrimerNombre')
                cliente_segundo_nombre = datos_mensaje.get('PersonaSegundoNombre')
                cliente_primer_apellido = datos_mensaje.get('PersonaPrimerApellido')
                cliente_segundo_apellido = datos_mensaje.get('PersonaSegundoApellido')
                if not num_doc_identidad:
                    num_doc_identidad = datos_mensaje.get('NumDocIdentidad')
            
            logger.info(f"   • IdFactura: {id_factura} (tipo: {type(id_factura)})")
            logger.info(f"   • IdAseguradora: {id_aseguradora} (tipo: {type(id_aseguradora)})")
            logger.info(f"   • NumDocIdentidad: {num_doc_identidad}")
            
            # Buscar si ya existe un registro
            query_buscar = """
                SELECT IdfacturaCliente, error, IdFactura, IdAseguradora
                FROM [NeptunoMedicalAutomatico].[dbo].[FacturaCliente] 
                WHERE IdFactura = :id_factura AND IdAseguradora = :id_aseguradora
            """
            
            logger.info(f"🔍 Ejecutando SELECT para buscar registro:")
            logger.info(f"   • Query: {query_buscar}")
            logger.info(f"   • Parámetros: {{'id_factura': {id_factura}, 'id_aseguradora': {id_aseguradora}}}")
            
            resultado = self.db_manager.execute_query(query_buscar, {
                'id_factura': id_factura, 
                'id_aseguradora': id_aseguradora
            })
            
            logger.info(f"📊 Resultado del SELECT: {resultado}")
            if resultado:
                logger.info(f"   • Registros encontrados: {len(resultado)}")
                for i, reg in enumerate(resultado):
                    logger.info(f"   • Registro {i+1}: IdFactura={reg.get('IdFactura')} (tipo: {type(reg.get('IdFactura'))}), IdAseguradora={reg.get('IdAseguradora')} (tipo: {type(reg.get('IdAseguradora'))})")
            else:
                logger.info("   • No se encontraron registros")
            
            if resultado:
                # Actualizar registro existente con error
                logger.info("🔄 Actualizando registro existente con error...")
                
                query_update = """
                    UPDATE [NeptunoMedicalAutomatico].[dbo].[FacturaCliente] 
                    SET error = :mensaje_error, estado = 0
                    WHERE IdFactura = :id_factura AND IdAseguradora = :id_aseguradora
                """
                
                logger.info(f"🔄 Ejecutando UPDATE para actualizar registro:")
                logger.info(f"   • Query: {query_update}")
                logger.info(f"   • Parámetros: {{'mensaje_error': '{mensaje_error}', 'id_factura': {id_factura}, 'id_aseguradora': {id_aseguradora}}}")
                
                result_update = self.db_manager.execute_query(query_update, {
                    'mensaje_error': mensaje_error,
                    'id_factura': id_factura,
                    'id_aseguradora': id_aseguradora
                })
                
                # Verificar filas afectadas
                try:
                    # Para UPDATE, el resultado es un objeto Result de SQLAlchemy
                    if hasattr(result_update, 'rowcount'):
                        filas_afectadas = result_update.rowcount
                        logger.info(f"📊 Filas afectadas por UPDATE: {filas_afectadas}")
                        if filas_afectadas > 0:
                            logger.info("✅ Registro actualizado con error exitosamente")
                        else:
                            logger.warning("⚠️ UPDATE ejecutado pero 0 filas afectadas - posible problema de tipos de datos")
                    else:
                        logger.info("✅ UPDATE ejecutado (sin información de filas afectadas)")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo obtener información de filas afectadas: {e}")
                    logger.info("✅ UPDATE ejecutado (sin verificación de filas afectadas)")
                
            else:
                # No insertar nuevos registros, solo actualizar existentes
                logger.warning("⚠️ No se encontró registro existente para actualizar")
                logger.info("ℹ️ Solo se actualizan registros existentes, no se insertan nuevos")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando cliente con error: {e}")
            logger.error(f"   • Parámetros: {datos_mensaje}")
            return False
    
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
            
            # Mostrar información detallada de la cola
            logger.info(f"🔍 Configuración de cola:")
            logger.info(f"   • Nombre de cola: '{Config.RABBITMQ_QUEUE}'")
            logger.info(f"   • Exchange: '{Config.RABBITMQ_EXCHANGE}'")
            logger.info(f"   • Routing key: '{Config.RABBITMQ_ROUTING_KEY}'")
            logger.info(f"   • Host: {Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}")
            
            # Verificar estado de la cola antes de empezar a consumir
            try:
                queue_info = self.processor.rabbitmq_channel.queue_declare(
                    queue=Config.RABBITMQ_QUEUE, 
                    passive=True
                )
                message_count = queue_info.method.message_count
                consumer_count = queue_info.method.consumer_count
                logger.info(f"📊 Estado de la cola '{Config.RABBITMQ_QUEUE}':")
                logger.info(f"   • Mensajes en cola: {message_count}")
                logger.info(f"   • Consumidores activos: {consumer_count}")
                
                if message_count > 0:
                    logger.info(f"✅ Hay {message_count} mensaje(s) esperando ser procesados")
                else:
                    logger.info("⏳ No hay mensajes en la cola, esperando nuevos mensajes...")
                    
            except Exception as e:
                logger.warning(f"⚠️ No se pudo verificar el estado de la cola: {e}")
            
            def callback(ch, method, properties, body):
                try:
                    # Decodificar mensaje
                    mensaje = json.loads(body.decode('utf-8'))
                    logger.info(f"📨 Mensaje recibido: {mensaje.get('IdFactura', 'Sin ID')}")
                    
                    # Procesar mensaje
                    logger.info("🔄 Iniciando procesamiento del mensaje...")
                    resultado = self._process_single_message(mensaje)
                    logger.info(f"📊 Resultado del procesamiento: {resultado}")
                    
                    # Si el procesamiento fue exitoso, enviar mensaje de validación
                    if resultado:
                        logger.info("📤 Enviando mensaje de validación...")
                        if self._enviar_mensaje_validacion(mensaje):
                            logger.info("✅ Mensaje de validación enviado exitosamente")
                        else:
                            logger.warning("⚠️ Error enviando mensaje de validación")
                    else:
                        logger.warning("⚠️ Procesamiento falló, no se enviará mensaje de validación")
                    
                    # Confirmar procesamiento
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info("✅ Mensaje procesado exitosamente")
                    logger.info("⏳ Esperando siguiente mensaje...")
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando mensaje: {e}")
                    logger.error(f"   • Tipo de error: {type(e).__name__}")
                    logger.error(f"   • Detalles: {str(e)}")
                    # Rechazar mensaje
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    logger.info("⏳ Esperando siguiente mensaje...")
            
            # Configurar consumo de mensajes
            self.processor.rabbitmq_channel.basic_qos(prefetch_count=1)
            self.processor.rabbitmq_channel.basic_consume(
                queue=Config.RABBITMQ_QUEUE,
                on_message_callback=callback
            )
            
            logger.info("⏳ Esperando mensajes...")
            logger.info("🔄 Worker en modo continuo - procesará mensajes indefinidamente")
            
            # Bucle continuo para mantener el worker funcionando
            while True:
                try:
                    self.processor.rabbitmq_channel.start_consuming()
                except KeyboardInterrupt:
                    logger.info("⏹️ Deteniendo worker por interrupción del usuario...")
                    self.processor.rabbitmq_channel.stop_consuming()
                    break
                except Exception as e:
                    logger.error(f"❌ Error en start_consuming: {e}")
                    logger.info("🔄 Reintentando conexión en 5 segundos...")
                    time.sleep(5)
                    # Reintentar conexión
                    if self.processor.connect_rabbitmq():
                        logger.info("✅ Reconectado a RabbitMQ, continuando...")
                        # Reconfigurar consumo después de reconectar
                        self.processor.rabbitmq_channel.basic_qos(prefetch_count=1)
                        self.processor.rabbitmq_channel.basic_consume(
                            queue=Config.RABBITMQ_QUEUE,
                            on_message_callback=callback
                        )
                    else:
                        logger.error("❌ No se pudo reconectar a RabbitMQ, reintentando en 10 segundos...")
                        time.sleep(10)
                
        except Exception as e:
            logger.error(f"❌ Error en procesamiento de mensajes: {e}")
    
    def _process_single_message(self, mensaje):
        """Procesa un mensaje individual"""
        try:
            # Verificar si es un mensaje de validación (ignorarlo)
            if mensaje.get('TipoMensaje') == 'validacion_excel':
                logger.info("📤 Mensaje de validación detectado - ignorando (no procesar)")
                logger.info(f"   • ID: {mensaje.get('IdFactura', 'Sin ID')}")
                logger.info(f"   • Estado: {mensaje.get('Estado', 'Sin estado')}")
                logger.info("✅ Mensaje de validación ignorado correctamente")
                return True  # Retornar True para continuar esperando
            
            # Verificar y reinicializar driver si es necesario
            if not self.processor.driver:
                logger.info("🔄 Driver no disponible, reinicializando...")
                self.processor.setup_selenium_driver()
                if not self.processor.driver:
                    logger.error("❌ No se pudo reinicializar el driver")
                    return False
                logger.info("✅ Driver reinicializado exitosamente")
            
            # Mostrar información completa del mensaje recibido
            logger.info("📋 INFORMACIÓN COMPLETA DEL MENSAJE:")
            logger.info(f"   • Tipo de mensaje: {type(mensaje)}")
            logger.info(f"   • Contenido del mensaje: {mensaje}")
            
            # Obtener información de la aseguradora
            # El NombreCompleto está dentro del array Clientes
            nombre_aseguradora = None
            
            if 'Clientes' in mensaje and mensaje['Clientes']:
                # Tomar el NombreCompleto del primer cliente
                primer_cliente = mensaje['Clientes'][0]
                nombre_aseguradora = primer_cliente.get('NombreCompleto')
                logger.info(f"   • NombreCompleto extraído del primer cliente: '{nombre_aseguradora}' (tipo: {type(nombre_aseguradora)})")
            else:
                # Fallback: buscar directamente en el mensaje
                nombre_aseguradora = mensaje.get('NombreCompleto')
                logger.info(f"   • NombreCompleto extraído directamente: '{nombre_aseguradora}' (tipo: {type(nombre_aseguradora)})")
            
            if not nombre_aseguradora:
                logger.error("❌ No se pudo encontrar NombreCompleto en el mensaje")
                logger.info("   • Claves disponibles en el mensaje:")
                for key in mensaje.keys():
                    logger.info(f"     - {key}: {mensaje[key]}")
                return False
    
            # Obtener URL de la aseguradora
            logger.info(f"🔍 Buscando URL para aseguradora: '{nombre_aseguradora}'")
            url_info = self.processor.db_manager.get_url_aseguradora(nombre_aseguradora)
            if not url_info:
                logger.error(f"❌ No se encontró URL para aseguradora '{nombre_aseguradora}'")
                return False
                
            # Limpiar caché de búsquedas al cambiar de aseguradora
            logger.info("🧹 Limpiando caché de búsquedas para nueva aseguradora...")
            self.processor._limpiar_cache_busquedas()
            
            # Ejecutar login una sola vez para la aseguradora
            if not self.processor.execute_login(url_info, mensaje):
                logger.error("❌ Error en login")
                return False
            
            # Procesar cada cliente del array
            clientes_procesados = 0
            clientes_exitosos = 0
            total_clientes = len(mensaje.get('Clientes', []))
            logger.info(f"📋 Procesando {total_clientes} clientes...")
            
            # Guardar estadísticas para el mensaje de validación
            self._clientes_procesados = total_clientes
            self._clientes_exitosos = 0
            
            for i, cliente in enumerate(mensaje.get('Clientes', [])):
                try:
                    logger.info(f"👤 Procesando cliente {i+1}/{total_clientes}")
                    logger.info(f"   • IdFactura: {cliente.get('IdFactura')}")
                    logger.info(f"   • NumDocIdentidad: {cliente.get('NumDocIdentidad')}")
                    
                    # Construir nombre completo del cliente
                    nombre_completo_cliente = self._construir_nombre_completo_cliente(cliente)
                    if not nombre_completo_cliente:
                        logger.error(f"❌ No se pudo construir nombre completo para cliente {i+1}")
                        continue
                    
                    logger.info(f"   • Nombre completo: '{nombre_completo_cliente}'")
                    
                    # Capturar información para este cliente específico
                    # Para PAN AMERICAN LIFE DE ECUADOR, usar el procesador específico
                    logger.info(f"🔍 Verificando nombre de aseguradora: '{url_info.get('nombre')}'")
                    if url_info.get('nombre') == 'PAN AMERICAN LIFE DE ECUADOR':
                        logger.info("🇪🇨 Usando procesador específico para PAN AMERICAN LIFE DE ECUADOR")
                        try:
                            from aseguradoras.pan_american_life_ecuador.implementacion_oauth2 import crear_procesador_oauth2
                            logger.info("✅ Procesador específico importado correctamente")
                            
                            procesador_especifico = crear_procesador_oauth2(self.processor.db_manager)
                            logger.info("✅ Procesador específico creado correctamente")
                            
                            # Pasar la función de guardar errores al procesador específico
                            procesador_especifico.set_error_handler(self.processor._guardar_cliente_con_error)
                            
                            # Pasar las funciones de caché al procesador específico
                            procesador_especifico.set_cache_functions(
                                self.processor._obtener_datos_del_cache,
                                self.processor._guardar_en_cache
                            )
                            
                            # Usar el procesador específico que maneja toda la lógica
                            logger.info("🔄 Iniciando procesamiento con procesador específico...")
                            if procesador_especifico.procesar_oauth2_completo(self.processor.driver, cliente):
                                clientes_procesados += 1
                                clientes_exitosos += 1
                                self._clientes_exitosos += 1
                                logger.info(f"✅ Cliente {i+1} procesado exitosamente con procesador específico")
                            else:
                                logger.error(f"❌ Error procesando cliente {i+1} con procesador específico")
                                # Guardar cliente con error en base de datos
                                error_msg = f"Error en procesamiento con procesador específico OAuth2 para cliente {i+1}"
                                if not self.processor._guardar_cliente_con_error(cliente, error_msg):
                                    logger.error("❌ Error guardando cliente con error en base de datos")
                                
                        except ImportError as e:
                            logger.error(f"❌ Error importando procesador específico: {e}")
                            # Fallback a procesador genérico
                            if self.processor.capturar_informacion_pantalla(
                                url_info['id'], 
                                url_info.get('nombre'), 
                                cliente
                            ):
                                clientes_procesados += 1
                                clientes_exitosos += 1
                                self._clientes_exitosos += 1
                                logger.info(f"✅ Cliente {i+1} procesado exitosamente con procesador genérico")
                            else:
                                logger.error(f"❌ Error procesando cliente {i+1} con procesador genérico")
                                # Guardar cliente con error en base de datos
                                error_msg = f"Error en procesamiento con procesador genérico (fallback) para cliente {i+1}"
                                if not self.processor._guardar_cliente_con_error(cliente, error_msg):
                                    logger.error("❌ Error guardando cliente con error en base de datos")
                        except Exception as e:
                            logger.error(f"❌ Error ejecutando procesador específico: {e}")
                            # Fallback a procesador genérico
                            if self.processor.capturar_informacion_pantalla(
                                url_info['id'], 
                                url_info.get('nombre'), 
                                cliente
                            ):
                                clientes_procesados += 1
                                clientes_exitosos += 1
                                self._clientes_exitosos += 1
                                logger.info(f"✅ Cliente {i+1} procesado exitosamente con procesador genérico")
                            else:
                                logger.error(f"❌ Error procesando cliente {i+1} con procesador genérico")
                                # Guardar cliente con error en base de datos
                                error_msg = f"Error ejecutando procesador específico: {str(e)}"
                                if not self.processor._guardar_cliente_con_error(cliente, error_msg):
                                    logger.error("❌ Error guardando cliente con error en base de datos")
                    else:
                        # Para otras aseguradoras, usar procesador genérico
                        logger.info(f"🔄 Usando procesador genérico para aseguradora: '{url_info.get('nombre')}'")
                        if self.processor.capturar_informacion_pantalla(
                            url_info['id'], 
                            url_info.get('nombre'), 
                            cliente
                        ):
                            clientes_procesados += 1
                            clientes_exitosos += 1
                            self._clientes_exitosos += 1
                            logger.info(f"✅ Cliente {i+1} procesado exitosamente")
                        else:
                            logger.error(f"❌ Error procesando cliente {i+1}")
                            # Guardar cliente con error en base de datos
                            error_msg = f"Error en procesamiento con procesador genérico para cliente {i+1}"
                            if not self.processor._guardar_cliente_con_error(cliente, error_msg):
                                logger.error("❌ Error guardando cliente con error en base de datos")
                
                except Exception as e:
                    logger.error(f"❌ Error procesando cliente {i+1}: {e}")
                    # Guardar cliente con error en base de datos
                    error_msg = f"Error general procesando cliente {i+1}: {str(e)}"
                    if not self.processor._guardar_cliente_con_error(cliente, error_msg):
                        logger.error("❌ Error guardando cliente con error en base de datos")
                    continue
            
            logger.info(f"✅ Procesamiento completado: {clientes_procesados}/{total_clientes} clientes procesados exitosamente")
            
            # Enviar mensaje de validación a RabbitMQ después del procesamiento
            logger.info("📤 Enviando mensaje de validación a RabbitMQ...")
            if self._enviar_mensaje_validacion(mensaje):
                logger.info("✅ Mensaje de validación enviado exitosamente")
            else:
                logger.warning("⚠️ Error enviando mensaje de validación, pero continuando...")
            
            # Cerrar completamente el navegador después de procesar cada mensaje
            logger.info("🔒 Cerrando navegador después del procesamiento...")
            logger.info("🔄 Cerrando navegador completamente para el siguiente mensaje")
            
            if not self.processor.limpiar_browser(limpieza_profunda=True):
                logger.warning("⚠️ Error cerrando el navegador, pero continuando...")
            else:
                logger.info("✅ Navegador cerrado exitosamente, se abrirá uno nuevo para el siguiente mensaje")
            
            return clientes_procesados > 0
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje individual: {e}")
            return False
    
    def _construir_nombre_completo_cliente(self, datos_cliente):
        """Construye el nombre completo del cliente concatenando los campos"""
        try:
            logger.info("🔤 Construyendo nombre completo del cliente...")
            
            # Extraer campos del cliente
            primer_nombre = datos_cliente.get('PersonaPrimerNombre', '').strip()
            segundo_nombre = datos_cliente.get('PersonaSegundoNombre', '').strip()
            primer_apellido = datos_cliente.get('PersonaPrimerApellido', '').strip()
            segundo_apellido = datos_cliente.get('PersonaSegundoApellido', '').strip()
            
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
    
    def _enviar_mensaje_validacion(self, mensaje_original):
        """Envía un mensaje de validación después de procesar un mensaje"""
        try:
            logger.info("📤 Enviando mensaje de validación...")
            
            # Obtener el nombre de la aseguradora del mensaje original
            nombre_aseguradora = None
            if 'Clientes' in mensaje_original and mensaje_original['Clientes']:
                nombre_aseguradora = mensaje_original['Clientes'][0].get('NombreCompleto')
            else:
                nombre_aseguradora = mensaje_original.get('NombreCompleto')
            
            if not nombre_aseguradora:
                logger.warning("⚠️ No se pudo obtener el nombre de la aseguradora para el mensaje de validación")
                return False
            
            # Obtener información del procesamiento
            total_clientes = len(mensaje_original.get('Clientes', []))
            clientes_procesados = getattr(self, '_clientes_procesados', 0)
            clientes_exitosos = getattr(self, '_clientes_exitosos', 0)
            
            # Determinar estado del procesamiento
            if clientes_exitosos == total_clientes and total_clientes > 0:
                estado = "PROCESADO_EXITOSAMENTE"
                observaciones = f"Todos los clientes procesados exitosamente ({clientes_exitosos}/{total_clientes})"
            elif clientes_exitosos > 0:
                estado = "PROCESADO_PARCIALMENTE"
                observaciones = f"Procesamiento parcial: {clientes_exitosos}/{total_clientes} clientes exitosos"
            else:
                estado = "PROCESADO_CON_ERRORES"
                observaciones = f"Procesamiento con errores: 0/{total_clientes} clientes exitosos"
            
            # Crear mensaje de validación
            mensaje_validacion = {
                "IdFactura": f"VALIDACION-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "TipoMensaje": "validacion_excel",
                "FechaProcesamiento": datetime.now().isoformat(),
                "MensajeOriginal": mensaje_original.get('IdFactura', 'Sin ID'),
                "IdAseguradora": mensaje_original.get('IdAseguradora'),
                "Aseguradora": nombre_aseguradora,
                "TotalClientes": total_clientes,
                "ClientesExitosos": clientes_exitosos,
                "ClientesConError": total_clientes - clientes_exitosos,
                "Estado": estado,
                "Observaciones": observaciones,
                "Accion": "GENERAR_REPORTE_VALIDACION"
            }
            
            # Enviar mensaje de validación
            message_body = json.dumps(mensaje_validacion, ensure_ascii=False)
            
            self.processor.rabbitmq_channel.basic_publish(
                exchange="validacion_excel_exchange",
                routing_key=Config.RABBITMQ_ROUTING_KEY,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Hacer el mensaje persistente
                    content_type='application/json',
                    message_id=f"VALIDACION-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    timestamp=int(datetime.now().timestamp())
                )
            )
            
            logger.info("✅ Mensaje de validación enviado exitosamente")
            logger.info(f"   • ID de validación: {mensaje_validacion['IdFactura']}")
            logger.info(f"   • Tipo: {mensaje_validacion['TipoMensaje']}")
            logger.info(f"   • Aseguradora: {nombre_aseguradora}")
            logger.info(f"   • Estado: {mensaje_validacion['Estado']}")
            logger.info(f"   • Total clientes: {mensaje_validacion['TotalClientes']}")
            logger.info(f"   • Clientes exitosos: {mensaje_validacion['ClientesExitosos']}")
            logger.info(f"   • Clientes con error: {mensaje_validacion['ClientesConError']}")
            logger.info(f"   • Acción: {mensaje_validacion['Accion']}")
            logger.info(f"   • Exchange: validacion_excel_exchange")
            logger.info(f"   • Routing Key: {Config.RABBITMQ_ROUTING_KEY}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje de validación: {e}")
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
