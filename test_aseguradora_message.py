#!/usr/bin/env python3
"""
Script para publicar un mensaje de prueba de aseguradora en RabbitMQ
"""

import json
from src.rabbitmq_client import RabbitMQClient

def publish_test_message():
    """Publica un mensaje de prueba de aseguradora"""
    try:
        # Crear cliente de RabbitMQ
        client = RabbitMQClient()
        
        # Mensaje de prueba
        test_message = {
            "NombreCompleto": "PAN AMERICAN LIFE DE ECUADOR",
            "IdFactura": "TEST001",
            "IdAseguradora": 14,
            "NumDocIdentidad": "1234567890",
            "PersonaPrimerNombre": "TEST",
            "PersonaPrimerApellido": "USER",
            "FechaProcesamiento": "2025-01-09T15:00:00Z"
        }
        
        # Publicar mensaje
        client.publish_message(test_message)
        print("✅ Mensaje de prueba publicado exitosamente")
        print(f"📝 Contenido: {json.dumps(test_message, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ Error publicando mensaje: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    print("🚀 Publicando mensaje de prueba de aseguradora...")
    publish_test_message()
