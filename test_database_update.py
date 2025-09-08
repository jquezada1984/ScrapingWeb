#!/usr/bin/env python3
"""
Script de prueba para verificar la actualización de la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import DatabaseManager
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_database_update():
    """Prueba la actualización de la base de datos"""
    try:
        logger.info("🚀 Iniciando prueba de base de datos...")
        
        # Inicializar el manager de base de datos
        db_manager = DatabaseManager()
        
        # Probar conexión
        if db_manager.test_connection():
            logger.info("✅ Conexión a la base de datos exitosa")
        else:
            logger.error("❌ Error conectando a la base de datos")
            return False
        
        # Datos de prueba
        test_data = {
            'num_poliza': '77224',
            'num_dependiente': '0',
            'id_factura': '1258742',
            'id_aseguradora': 14
        }
        
        logger.info(f"📋 Datos de prueba: {test_data}")
        
        # Query de prueba
        query = """
            UPDATE [dbo].[FacturaCliente] 
            SET NumPoliza = :num_poliza, 
                NumDependiente = :num_dependiente
            WHERE IdFactura = :id_factura 
            AND IdAseguradora = :id_aseguradora
        """
        
        logger.info(f"🔍 Ejecutando query UPDATE:")
        logger.info(f"   Query: {query}")
        logger.info(f"   Parámetros: {test_data}")
        
        # Ejecutar la actualización
        result = db_manager.execute_query(query, test_data)
        
        if result:
            logger.info("✅ UPDATE ejecutado exitosamente")
            
            # Verificar cuántas filas fueron afectadas
            if hasattr(result, 'rowcount'):
                filas_afectadas = result.rowcount
                logger.info(f"📊 Filas afectadas: {filas_afectadas}")
                
                if filas_afectadas > 0:
                    logger.info("✅ Registro actualizado correctamente")
                    return True
                else:
                    logger.warning("⚠️ No se encontró ningún registro para actualizar")
                    return False
            else:
                logger.info("✅ Actualización completada (sin información de filas afectadas)")
                return True
        else:
            logger.error("❌ Error ejecutando UPDATE")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        return False

if __name__ == "__main__":
    success = test_database_update()
    if success:
        logger.info("🎉 Prueba completada exitosamente")
    else:
        logger.error("💥 Prueba falló")
        sys.exit(1)

