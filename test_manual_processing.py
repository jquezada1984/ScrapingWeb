#!/usr/bin/env python3
"""
Script para probar el procesamiento manual sin RabbitMQ
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import DatabaseManager
from aseguradoras.pan_american_life_ecuador.implementacion_oauth2 import PanAmericanLifeEcuadorOAuth2Processor
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_manual_processing():
    """Prueba el procesamiento manual completo"""
    try:
        logger.info("🚀 Iniciando procesamiento manual...")
        
        # Inicializar el manager de base de datos
        db_manager = DatabaseManager()
        
        # Probar conexión
        if db_manager.test_connection():
            logger.info("✅ Conexión a la base de datos exitosa")
        else:
            logger.error("❌ Error conectando a la base de datos")
            return False
        
        # Crear el procesador específico
        processor = PanAmericanLifeEcuadorOAuth2Processor(db_manager)
        logger.info("✅ Procesador PAN AMERICAN LIFE DE ECUADOR creado")
        
        # Simular datos de mensaje (como los que vendrían de RabbitMQ)
        mensaje_simulado = {
            'IdAseguradora': 14,
            'Clientes': [
                {
                    'NombreCompleto': 'PAN AMERICAN LIFE DE ECUADOR',
                    'IdFactura': '1257917',
                    'IdAseguradora': 14,
                    'NumDocIdentidad': '0102158896',
                    'PersonaPrimerNombre': 'FABIAN',
                    'PersonaSegundoNombre': 'MAURICIO',
                    'PersonaPrimerApellido': 'BELTRAN',
                    'PersonaSegundoApellido': 'NARVAEZ',
                    'FechaProcesamiento': '2025-09-05T21:03:51.4870322Z'
                },
                {
                    'NombreCompleto': 'PAN AMERICAN LIFE DE ECUADOR',
                    'IdFactura': '1258742',
                    'IdAseguradora': 14,
                    'NumDocIdentidad': '0102158896',
                    'PersonaPrimerNombre': 'FABIAN',
                    'PersonaSegundoNombre': 'MAURICIO',
                    'PersonaPrimerApellido': 'BELTRAN',
                    'PersonaSegundoApellido': 'NARVAEZ',
                    'FechaProcesamiento': '2025-09-05T21:03:51.4870843Z'
                }
            ],
            'FechaProcesamiento': '2025-09-05T21:03:51.5024106Z',
            'TotalClientes': 2
        }
        
        logger.info("📋 Datos de mensaje simulado:")
        logger.info(f"   • IdAseguradora: {mensaje_simulado['IdAseguradora']}")
        logger.info(f"   • TotalClientes: {mensaje_simulado['TotalClientes']}")
        
        # Procesar cada cliente
        clientes_procesados = 0
        
        for i, cliente in enumerate(mensaje_simulado['Clientes']):
            logger.info(f"👤 Procesando cliente {i+1}/{len(mensaje_simulado['Clientes'])}")
            logger.info(f"   • IdFactura: {cliente['IdFactura']}")
            logger.info(f"   • NumDocIdentidad: {cliente['NumDocIdentidad']}")
            
            # Construir nombre completo
            nombre_completo = f"{cliente['PersonaPrimerNombre']} {cliente['PersonaSegundoNombre']} {cliente['PersonaPrimerApellido']} {cliente['PersonaSegundoApellido']}"
            logger.info(f"✅ Nombre completo construido: '{nombre_completo}'")
            
            # Simular datos de fila encontrada (como si hubiéramos extraído de la tabla web)
            datos_fila_simulados = {
                'poliza': '77224',
                'certificado': '0000000463',
                'no_dependiente': '0',
                'nombre_paciente': 'FABIAN MAURICIO BELTRAN NARVAEZ',
                'titular': 'FABIAN MAURICIO BELTRAN NARVAEZ',
                'relacion': '',
                'tipo_poliza': 'Grupos Corporativos',
                'status': 'Activo',
                'dependiente': '19801130'
            }
            
            logger.info("📋 Datos de fila simulados:")
            for key, value in datos_fila_simulados.items():
                logger.info(f"   • {key}: {value}")
            
            # Probar la actualización de la base de datos
            logger.info("🔄 Actualizando base de datos...")
            
            if processor._actualizar_factura_cliente(datos_fila_simulados, cliente):
                logger.info("✅ Base de datos actualizada exitosamente")
                clientes_procesados += 1
            else:
                logger.error("❌ Error actualizando base de datos")
        
        logger.info(f"✅ Procesamiento completado: {clientes_procesados}/{len(mensaje_simulado['Clientes'])} clientes procesados exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en el procesamiento: {e}")
        return False

if __name__ == "__main__":
    success = test_manual_processing()
    if success:
        logger.info("🎉 Procesamiento manual exitoso")
    else:
        logger.error("💥 Procesamiento manual falló")
        sys.exit(1)

