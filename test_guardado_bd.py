#!/usr/bin/env python3
"""
Script de prueba para verificar el guardado en base de datos
"""

import logging
import uuid
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_guardado_bd.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def simular_guardado_bd():
    """Simula el proceso de guardado en base de datos"""
    
    logger.info("🧪 SIMULANDO GUARDADO EN BASE DE DATOS")
    logger.info("=" * 60)
    
    # Simular datos del mensaje RabbitMQ
    datos_mensaje = {
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
    
    # Simular proceso de guardado
    try:
        # Generar ID único
        id_factura_cliente = str(uuid.uuid4())
        logger.info(f"🆔 ID generado: {id_factura_cliente}")
        
        # Preparar datos para inserción
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
        
        logger.info("📋 DATOS A INSERTAR EN FacturaCliente:")
        for campo, valor in datos_insercion.items():
            logger.info(f"   • {campo}: '{valor}'")
        
        # Simular query de inserción
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
        
        logger.info("📝 QUERY DE INSERCIÓN:")
        logger.info(insert_query)
        
        logger.info("=" * 60)
        logger.info("✅ SIMULACIÓN COMPLETADA EXITOSAMENTE")
        logger.info("   🆔 ID: " + id_factura_cliente)
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
        ("IdFactura", "int", "NULL", "ID de la factura"),
        ("IdAseguradora", "int", "NULL", "ID de la aseguradora"),
        ("NumDocIdentidad", "varchar(25)", "NULL", "Número de documento de identidad"),
        ("ClientePersonaPrimerNombre", "varchar(20)", "NULL", "Primer nombre del cliente"),
        ("ClientePersonaSegundoNombre", "varchar(20)", "NULL", "Segundo nombre del cliente"),
        ("ClientePersonaPrimerApellido", "varchar(20)", "NULL", "Primer apellido del cliente"),
        ("ClientePersonaSegundoApellido", "varchar(20)", "NULL", "Segundo apellido del cliente"),
        ("NumPoliza", "varchar(50)", "NULL", "Número de póliza"),
        ("NumDependiente", "varchar(50)", "NULL", "Número de dependiente"),
        ("FechaCreacion", "timestamp", "NOT NULL", "Fecha de creación automática"),
        ("estado", "tinyint", "NOT NULL", "Estado del registro (1=Activo)")
    ]
    
    for campo, tipo, null, descripcion in estructura:
        logger.info(f"   • {campo:<30} {tipo:<15} {null:<8} - {descripcion}")
    
    logger.info("=" * 60)

def main():
    """Función principal"""
    logger.info("🚀 INICIANDO PRUEBA DE GUARDADO EN BASE DE DATOS")
    logger.info("=" * 60)
    
    # Mostrar estructura de la tabla
    mostrar_estructura_tabla()
    
    # Simular guardado
    if simular_guardado_bd():
        logger.info("🎯 PRUEBA COMPLETADA EXITOSAMENTE")
    else:
        logger.error("❌ PRUEBA FALLÓ")
    
    logger.info("=" * 60)
    logger.info("🏁 FIN DE LA PRUEBA")

if __name__ == "__main__":
    main()
