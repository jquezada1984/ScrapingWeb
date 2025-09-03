#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración del worker con Edge
"""

import logging
import sys
from src.config import Config
from src.database import DatabaseManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_configuration():
    """Prueba la configuración del worker"""
    
    logger.info("🚀 INICIANDO PRUEBA DE CONFIGURACIÓN DEL WORKER")
    logger.info("=" * 60)
    
    try:
        # 1. Validar configuración
        logger.info("🔍 Validando configuración...")
        errores = Config.validar_configuracion()
        
        if errores:
            logger.error("❌ Errores de configuración encontrados:")
            for error in errores:
                logger.error(f"   • {error}")
            return False
        
        logger.info("✅ Configuración válida")
        
        # 2. Mostrar configuración
        logger.info("📋 Configuración del sistema:")
        logger.info(f"   • SQL Server: {Config.SQL_SERVER_HOST}")
        logger.info(f"   • Base de datos: {Config.SQL_SERVER_DATABASE}")
        logger.info(f"   • RabbitMQ: {Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}")
        logger.info(f"   • Cola: {Config.RABBITMQ_QUEUE}")
        logger.info(f"   • Exchange: {Config.RABBITMQ_EXCHANGE}")
        
        # 3. Probar conexión a base de datos
        logger.info("🔌 Probando conexión a base de datos...")
        db_manager = DatabaseManager()
        
        if db_manager.test_connection():
            logger.info("✅ Conexión a base de datos exitosa")
        else:
            logger.error("❌ Error conectando a base de datos")
            return False
        
        # 4. Probar consulta simple
        logger.info("🔍 Probando consulta simple...")
        try:
            result = db_manager.execute_query("SELECT 1 as test")
            if result:
                logger.info("✅ Consulta de prueba exitosa")
            else:
                logger.warning("⚠️ Consulta de prueba sin resultados")
        except Exception as e:
            logger.error(f"❌ Error en consulta de prueba: {e}")
            return False
        
        # 5. Verificar tabla de aseguradoras
        logger.info("🔍 Verificando tabla de aseguradoras...")
        try:
            aseguradoras = db_manager.execute_query("SELECT TOP 5 nombre FROM urls_automatizacion")
            if aseguradoras:
                logger.info(f"✅ Encontradas {len(aseguradoras)} aseguradoras:")
                for aseguradora in aseguradoras:
                    logger.info(f"   • {aseguradora['nombre']}")
            else:
                logger.warning("⚠️ No se encontraron aseguradoras")
        except Exception as e:
            logger.error(f"❌ Error consultando aseguradoras: {e}")
            return False
        
        logger.info("=" * 60)
        logger.info("🎯 CONFIGURACIÓN DEL WORKER VERIFICADA EXITOSAMENTE")
        logger.info("✅ El worker está listo para ejecutarse con Edge")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de configuración: {e}")
        return False

if __name__ == "__main__":
    success = test_configuration()
    sys.exit(0 if success else 1)
