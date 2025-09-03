#!/usr/bin/env python3
"""
Script para enviar mensaje de prueba con NumDocIdentidad a RabbitMQ
Versión 2 - Corregida con selectores HTML reales
"""

import json
import pika
import sys
from src.config import Config

def enviar_mensaje_prueba():
    """Envía un mensaje de prueba a RabbitMQ"""
    
    # Mensaje de prueba con NumDocIdentidad
    mensaje_prueba = {
        "Clientes": [
            {
                "NombreCompleto": "PAN AMERICAN LIFE DE ECUADOR",
                "NumDocIdentidad": "0102158896",  # Número de documento a buscar
                "TipoDocumento": "Cédula",
                "FechaNacimiento": "1985-03-15",
                "Genero": "F",
                "EstadoCivil": "Soltero",
                "Direccion": "Av. Amazonas N45-123",
                "Ciudad": "Quito",
                "Provincia": "Pichincha",
                "Telefono": "0987654321",
                "Email": "cliente@ejemplo.com",
                "Ocupacion": "Ingeniero",
                "IngresosMensuales": 2500.00,
                "FechaSolicitud": "2025-09-02"
            }
        ],
        "FechaProcesamiento": "2025-09-02T15:55:00",
        "TotalClientes": 1,
        "Origen": "Script de Prueba V2",
        "Version": "2.0",
        "Notas": "Selectores HTML corregidos según la página real"
    }
    
    try:
        # Conectar a RabbitMQ
        print("🔌 Conectando a RabbitMQ...")
        credentials = pika.PlainCredentials(Config.RABBITMQ_USERNAME, Config.RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                credentials=credentials
            )
        )
        
        channel = connection.channel()
        
        # Declarar la cola y el exchange
        channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True)
        channel.exchange_declare(
            exchange=Config.RABBITMQ_EXCHANGE, 
            exchange_type='direct', 
            durable=True
        )
        
        # Vincular la cola al exchange
        channel.queue_bind(
            exchange=Config.RABBITMQ_EXCHANGE,
            queue=Config.RABBITMQ_QUEUE,
            routing_key=Config.RABBITMQ_ROUTING_KEY
        )
        
        print("✅ Conectado a RabbitMQ exitosamente")
        print("=" * 60)
        
        # Mostrar información del mensaje
        print("📨 Mensaje de prueba a enviar:")
        print(f"   • Aseguradora: {mensaje_prueba['Clientes'][0]['NombreCompleto']}")
        print(f"   • NumDocIdentidad: {mensaje_prueba['Clientes'][0]['NumDocIdentidad']}")
        print(f"   • Tipo Documento: {mensaje_prueba['Clientes'][0]['TipoDocumento']}")
        print(f"   • Origen: {mensaje_prueba['Origen']}")
        print(f"   • Versión: {mensaje_prueba['Version']}")
        print("=" * 60)
        
        # Mostrar configuración de selectores
        print("🎯 Configuración de Selectores HTML:")
        print("   • Campo Input: input[name=\"ctl00$ContenidoPrincipal$CtrlBuscaAseguradoProv$txtIdentificacionAseg\"]")
        print("   • Botón Buscar: a[id=\"ContenidoPrincipal_CtrlBuscaAseguradoProv_lnkBuscar\"]")
        print("   • Texto del Botón: 'Buscar Pólizas'")
        print("=" * 60)
        
        # Enviar mensaje
        mensaje_json = json.dumps(mensaje_prueba, ensure_ascii=False, indent=2)
        
        channel.basic_publish(
            exchange=Config.RABBITMQ_EXCHANGE,
            routing_key=Config.RABBITMQ_ROUTING_KEY,
            body=mensaje_json,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Hacer el mensaje persistente
                content_type='application/json'
            )
        )
        
        print("✅ Mensaje enviado exitosamente a RabbitMQ")
        print("=" * 60)
        print("🔄 PRÓXIMOS PASOS:")
        print("   1. Ejecutar el script SQL en tu base de datos:")
        print("      datos_ejemplo_informacion_capturada_v2.sql")
        print("   2. Ejecutar el worker para procesar el mensaje:")
        print("      python run_production_worker.py")
        print("=" * 60)
        
        # Cerrar conexión
        connection.close()
        
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Enviando mensaje de prueba V2 a RabbitMQ...")
    print("=" * 60)
    enviar_mensaje_prueba()
    print("=" * 60)
    print("✅ Script completado")
