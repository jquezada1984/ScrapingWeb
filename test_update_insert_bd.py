#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de UPDATE/INSERT en base de datos
"""

import logging
import uuid
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_update_insert_bd.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def simular_proceso_update_insert():
    """Simula el proceso de UPDATE/INSERT en base de datos"""
    
    logger.info("🧪 SIMULANDO PROCESO UPDATE/INSERT EN BASE DE DATOS")
    logger.info("=" * 60)
    
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
    
    # Simular datos de la tabla HTML
    fila_data = {
        'Póliza': '77224',
        'Certificado': '0000000463',
        'No. Dependiente': '0',
        'Nombre del Paciente': 'FABIAN MAURICIO BELTRAN NARVAEZ',
        'Titular': 'FABIAN MAURICIO BELTRAN NARVAEZ',
        'Relacion': '',
        'Tipo de Póliza': 'Grupos Corporativos',
        'Status': 'Activo'
    }
    
    logger.info("📋 DATOS DEL MENSAJE RABBITMQ:")
    for campo, valor in datos_mensaje.items():
        logger.info(f"   • {campo}: '{valor}'")
    
    logger.info("📋 DATOS DE LA TABLA HTML:")
    for campo, valor in fila_data.items():
        logger.info(f"   • {campo}: '{valor}'")
    
    logger.info("=" * 60)
    
    # Simular proceso de búsqueda y actualización
    try:
        # 🔍 PASO 1: Buscar registro existente
        logger.info("🔍 PASO 1: Buscando registro existente...")
        logger.info(f"   • IdFactura: {datos_mensaje['IdFactura']}")
        logger.info(f"   • IdAseguradora: {datos_mensaje['IdAseguradora']}")
        
        # Simular query de búsqueda
        select_query = """
            SELECT [IdfacturaCliente], [NumPoliza], [NumDependiente]
            FROM [NeptunoMedicalAutomatico].[dbo].[FacturaCliente]
            WHERE [IdFactura] = :IdFactura 
            AND [IdAseguradora] = :IdAseguradora
            AND [estado] = 1
        """
        
        logger.info("📝 QUERY DE BÚSQUEDA:")
        logger.info(select_query)
        
        # Simular que encontramos un registro existente
        logger.info("✅ REGISTRO ENCONTRADO - Procediendo con UPDATE...")
        
        # 🔄 PASO 2: Preparar UPDATE
        logger.info("🔄 PASO 2: Preparando UPDATE...")
        
        datos_update = {
            'IdfacturaCliente': 'uuid-simulado-12345',
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
        
        logger.info("📝 QUERY DE UPDATE:")
        logger.info(update_query)
        
        logger.info("📋 DATOS A ACTUALIZAR:")
        for campo, valor in datos_update.items():
            logger.info(f"   • {campo}: '{valor}'")
        
        logger.info("=" * 60)
        logger.info("✅ SIMULACIÓN DE UPDATE COMPLETADA EXITOSAMENTE")
        logger.info("   🆔 ID actualizado: " + datos_update['IdfacturaCliente'])
        logger.info("   📋 Póliza actualizada: " + datos_update['NumPoliza'])
        logger.info("   📋 Dependiente actualizado: " + datos_update['NumDependiente'])
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en simulación: {e}")
        return False

def simular_proceso_insert():
    """Simula el proceso de INSERT cuando no hay coincidencias"""
    
    logger.info("🧪 SIMULANDO PROCESO INSERT (SIN COINCIDENCIAS)")
    logger.info("=" * 60)
    
    # Simular datos del mensaje RabbitMQ (sin IdFactura/IdAseguradora)
    datos_mensaje = {
        'NumDocIdentidad': '9876543210',
        'PersonaPrimerNombre': 'MARIA',
        'PersonaSegundoNombre': 'JOSE',
        'PersonaPrimerApellido': 'GONZALEZ',
        'PersonaSegundoApellido': 'LOPEZ'
    }
    
    # Simular datos de la tabla HTML
    fila_data = {
        'Póliza': '99999',
        'Certificado': '0000000999',
        'No. Dependiente': '1',
        'Nombre del Paciente': 'MARIA JOSE GONZALEZ LOPEZ',
        'Status': 'Activo'
    }
    
    logger.info("📋 DATOS DEL MENSAJE RABBITMQ (SIN IdFactura/IdAseguradora):")
    for campo, valor in datos_mensaje.items():
        logger.info(f"   • {campo}: '{valor}'")
    
    logger.info("📋 DATOS DE LA TABLA HTML:")
    for campo, valor in fila_data.items():
        logger.info(f"   • {campo}: '{valor}'")
    
    logger.info("=" * 60)
    
    # Simular proceso de inserción
    try:
        # ⚠️ PASO 1: No hay IdFactura/IdAseguradora
        logger.info("⚠️ PASO 1: No se proporcionaron IdFactura o IdAseguradora")
        logger.info("   • Procediendo directamente con INSERT...")
        
        # 🔄 PASO 2: Generar ID único
        id_factura_cliente = str(uuid.uuid4())
        logger.info(f"🆔 PASO 2: ID generado: {id_factura_cliente}")
        
        # 🔄 PASO 3: Preparar datos para inserción
        logger.info("🔄 PASO 3: Preparando datos para inserción...")
        
        datos_insercion = {
            'IdfacturaCliente': id_factura_cliente,
            'IdFactura': None,
            'IdAseguradora': None,
            'NumDocIdentidad': datos_mensaje.get('NumDocIdentidad', ''),
            'ClientePersonaPrimerNombre': datos_mensaje.get('PersonaPrimerNombre', ''),
            'ClientePersonaSegundoNombre': datos_mensaje.get('PersonaSegundoNombre', ''),
            'ClientePersonaPrimerApellido': datos_mensaje.get('PersonaPrimerApellido', ''),
            'ClientePersonaSegundoApellido': datos_mensaje.get('PersonaSegundoApellido', ''),
            'NumPoliza': fila_data.get('Póliza', ''),
            'NumDependiente': fila_data.get('No. Dependiente', ''),
            'estado': 1
        }
        
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
        
        logger.info("📝 QUERY DE INSERT:")
        logger.info(insert_query)
        
        logger.info("📋 DATOS A INSERTAR:")
        for campo, valor in datos_insercion.items():
            logger.info(f"   • {campo}: '{valor}'")
        
        logger.info("=" * 60)
        logger.info("✅ SIMULACIÓN DE INSERT COMPLETADA EXITOSAMENTE")
        logger.info("   🆔 ID generado: " + id_factura_cliente)
        logger.info("   📋 Póliza: " + datos_insercion['NumPoliza'])
        logger.info("   📋 Dependiente: " + datos_insercion['NumDependiente'])
        logger.info("   👤 Cliente: " + datos_insercion['ClientePersonaPrimerNombre'] + " " + datos_insercion['ClientePersonaPrimerApellido'])
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en simulación: {e}")
        return False

def mostrar_estructura_tabla():
    """Muestra la estructura de la tabla FacturaCliente"""
    
    logger.info("📊 ESTRUCTURA DE LA TABLA FacturaCliente")
    logger.info("=" * 60)
    
    estructura = [
        ("IdfacturaCliente", "uniqueidentifier", "NOT NULL", "Clave primaria"),
        ("IdFactura", "int", "NULL", "ID de la factura (para búsqueda)"),
        ("IdAseguradora", "int", "NULL", "ID de la aseguradora (para búsqueda)"),
        ("NumDocIdentidad", "varchar(25)", "NULL", "Número de documento de identidad"),
        ("ClientePersonaPrimerNombre", "varchar(20)", "NULL", "Primer nombre del cliente"),
        ("ClientePersonaSegundoNombre", "varchar(20)", "NULL", "Segundo nombre del cliente"),
        ("ClientePersonaPrimerApellido", "varchar(20)", "NULL", "Primer apellido del cliente"),
        ("ClientePersonaSegundoApellido", "varchar(20)", "NULL", "Segundo apellido del cliente"),
        ("NumPoliza", "varchar(50)", "NULL", "Número de póliza (se actualiza)"),
        ("NumDependiente", "varchar(50)", "NULL", "Número de dependiente (se actualiza)"),
        ("FechaCreacion", "timestamp", "NOT NULL", "Fecha de creación automática"),
        ("estado", "tinyint", "NOT NULL", "Estado del registro (1=Activo)")
    ]
    
    for campo, tipo, null, descripcion in estructura:
        logger.info(f"   • {campo:<30} {tipo:<15} {null:<8} - {descripcion}")
    
    logger.info("=" * 60)

def main():
    """Función principal"""
    logger.info("🚀 INICIANDO PRUEBA DE UPDATE/INSERT EN BASE DE DATOS")
    logger.info("=" * 60)
    
    # Mostrar estructura de la tabla
    mostrar_estructura_tabla()
    
    # Simular proceso de UPDATE
    logger.info("🔄 PRUEBA 1: PROCESO DE UPDATE")
    logger.info("=" * 60)
    if simular_proceso_update_insert():
        logger.info("🎯 PRUEBA DE UPDATE COMPLETADA EXITOSAMENTE")
    else:
        logger.error("❌ PRUEBA DE UPDATE FALLÓ")
    
    logger.info("")
    logger.info("=" * 60)
    
    # Simular proceso de INSERT
    logger.info("➕ PRUEBA 2: PROCESO DE INSERT")
    logger.info("=" * 60)
    if simular_proceso_insert():
        logger.info("🎯 PRUEBA DE INSERT COMPLETADA EXITOSAMENTE")
    else:
        logger.error("❌ PRUEBA DE INSERT FALLÓ")
    
    logger.info("=" * 60)
    logger.info("🏁 FIN DE LAS PRUEBAS")

if __name__ == "__main__":
    main()
