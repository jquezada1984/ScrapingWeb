#!/usr/bin/env python3
"""
Script de prueba para verificar la búsqueda de cliente por nombre completo
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
        logging.FileHandler('test_busqueda_cliente.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_busqueda_cliente():
    """Prueba la búsqueda de cliente por nombre completo"""
    
    # Configurar Edge
    edge_options = Options()
    # edge_options.add_argument("--headless")  # Comentar para ver el navegador
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        logger.info("🚀 INICIANDO PRUEBA DE BÚSQUEDA DE CLIENTE")
        logger.info("=" * 60)
        
        # Crear driver
        driver = webdriver.Edge(options=edge_options)
        driver.set_page_load_timeout(30)
        
        # Simular datos del mensaje RabbitMQ
        datos_mensaje = {
            'PersonaPrimerNombre': 'FABIAN',
            'PersonaSegundoNombre': 'MAURICIO',
            'PersonaPrimerApellido': 'BELTRAN',
            'PersonaSegundoApellido': 'NARVAEZ',
            'NumDocIdentidad': '1234567890'
        }
        
        # Construir nombre completo
        nombre_completo = construir_nombre_completo(datos_mensaje)
        logger.info(f"👤 Nombre completo construido: '{nombre_completo}'")
        
        # Simular HTML de la tabla (como vendría de la página)
        html_tabla = """
        <table class="GridViewStylePV" cellspacing="0" cellpadding="5" rules="all" border="1" id="ContenidoPrincipal_CtrlBuscaAseguradoProv_gridAsegurados" style="border-collapse:collapse;">
            <tbody>
                <tr class="HeaderStylePV">
                    <th scope="col" style="width:85px;">Póliza</th>
                    <th scope="col" style="width:80px;">Certificado</th>
                    <th scope="col" style="width:105px;">No. Dependiente</th>
                    <th scope="col" style="width:122px;">Nombre del Paciente</th>
                    <th scope="col" style="width:122px;">Titular</th>
                    <th scope="col" style="width:80px;">Relacion</th>
                    <th scope="col" style="width:112px;">Tipo de Póliza</th>
                    <th scope="col" style="width:110px;">Status</th>
                    <th scope="col" style="width:40px;">&nbsp;</th>
                    <th class="hide" scope="col">Dependiente</th>
                </tr>
                <tr class="RowStylePV">
                    <td style="width:85px;">77224</td>
                    <td style="width:80px;">0000000463</td>
                    <td style="width:105px;">0</td>
                    <td style="width:122px;">FABIAN MAURICIO BELTRAN NARVAEZ</td>
                    <td style="width:122px;">FABIAN MAURICIO BELTRAN NARVAEZ</td>
                    <td style="width:80px;">&nbsp;</td>
                    <td style="width:112px;">Grupos Corporativos</td>
                    <td align="center" style="width:110px;">
                        <div style="position: relative">
                            <div id="ContenidoPrincipal_CtrlBuscaAseguradoProv_gridAsegurados_pStatusActivoText_0" class="rectangle-green">
                                <span id="ContenidoPrincipal_CtrlBuscaAseguradoProv_gridAsegurados_lbStatusActivoText_0">Activo</span>
                            </div>
                            <div class="floatingText">
                                <span>VER</span>
                            </div>
                        </div>
                    </td>
                    <td style="width:40px;"><input type="image" src="../../../images/eye.png" alt="VER" onclick="javascript:__doPostBack('ctl00$ContenidoPrincipal$CtrlBuscaAseguradoProv$gridAsegurados','Select$0');return false;"></td>
                    <td class="hide">19801130</td>
                </tr>
                <tr class="RowStylePV">
                    <td style="width:85px;">77224</td>
                    <td style="width:80px;">0000000463</td>
                    <td style="width:105px;">C2</td>
                    <td style="width:122px;">VERONICA ALEXANDRA INGA BRAVO</td>
                    <td style="width:122px;">FABIAN MAURICIO BELTRAN NARVAEZ</td>
                    <td style="width:80px;">Cónyuge</td>
                    <td style="width:112px;">Grupos Corporativos</td>
                    <td align="center" style="width:110px;">
                        <div style="position: relative">
                            <div id="ContenidoPrincipal_CtrlBuscaAseguradoProv_gridAsegurados_pStatusActivoText_1" class="rectangle-green">
                                <span id="ContenidoPrincipal_CtrlBuscaAseguradoProv_gridAsegurados_lbStatusActivoText_1">Activo</span>
                            </div>
                            <div class="floatingText">
                                <span>VER</span>
                            </div>
                        </div>
                    </td>
                    <td style="width:40px;"><input type="image" src="../../../images/eye.png" alt="VER" onclick="javascript:__doPostBack('ctl00$ContenidoPrincipal$CtrlBuscaAseguradoProv$gridAsegurados','Select$1');return false;"></td>
                    <td class="hide">19850210</td>
                </tr>
            </tbody>
        </table>
        """
        
        # Simular la lógica de búsqueda del worker
        logger.info("🔍 Simulando búsqueda de cliente en la tabla...")
        
        # Simular que encontramos la tabla y la procesamos
        filas_simuladas = [
            {
                'Póliza': '77224',
                'Certificado': '0000000463',
                'No. Dependiente': '0',
                'Nombre del Paciente': 'FABIAN MAURICIO BELTRAN NARVAEZ',
                'Titular': 'FABIAN MAURICIO BELTRAN NARVAEZ',
                'Relacion': '',
                'Tipo de Póliza': 'Grupos Corporativos',
                'Status': 'Activo'
            },
            {
                'Póliza': '77224',
                'Certificado': '0000000463',
                'No. Dependiente': 'C2',
                'Nombre del Paciente': 'VERONICA ALEXANDRA INGA BRAVO',
                'Titular': 'FABIAN MAURICIO BELTRAN NARVAEZ',
                'Relacion': 'Cónyuge',
                'Tipo de Póliza': 'Grupos Corporativos',
                'Status': 'Activo'
            }
        ]
        
        # Buscar el cliente
        cliente_encontrado = None
        for i, fila in enumerate(filas_simuladas, 1):
            logger.info(f"🔍 Verificando fila {i}: {fila.get('Nombre del Paciente', 'N/A')}")
            
            if es_cliente_buscado(fila, nombre_completo):
                if validar_cliente_activo(fila):
                    cliente_encontrado = fila
                    logger.info(f"🎯 ¡CLIENTE ENCONTRADO Y VALIDADO en fila {i}!")
                    break
                else:
                    logger.warning(f"⚠️ Cliente encontrado pero NO está activo en fila {i}")
            else:
                logger.info(f"ℹ️ No es el cliente buscado en fila {i}")
        
        # Mostrar resultado
        if cliente_encontrado:
            logger.info("=" * 60)
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
            logger.warning(f"⚠️ NO SE ENCONTRÓ el cliente '{nombre_completo}' o no está activo")
        
        logger.info("=" * 60)
        logger.info("✅ PRUEBA DE BÚSQUEDA COMPLETADA")
        
    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        
    finally:
        if driver:
            logger.info("🔌 Cerrando navegador...")
            driver.quit()

def construir_nombre_completo(datos_mensaje):
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

def es_cliente_buscado(fila_data, nombre_completo_cliente):
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

def validar_cliente_activo(fila_data):
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

if __name__ == "__main__":
    test_busqueda_cliente()
