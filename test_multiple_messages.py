#!/usr/bin/env python3
"""
Script para publicar múltiples mensajes de prueba y verificar el caché
"""

import json
import time
from src.rabbitmq_client import RabbitMQClient

def publish_multiple_test_messages():
    """Publica múltiples mensajes de prueba para verificar el caché"""
    try:
        # Crear cliente de RabbitMQ
        client = RabbitMQClient()
        
        # Mensajes de prueba con la misma aseguradora
        test_messages = [
            {
                "NombreCompleto": "PAN AMERICAN LIFE DE ECUADOR",
                "IdFactura": "TEST001",
                "IdAseguradora": 14,
                "NumDocIdentidad": "1234567890",
                "PersonaPrimerNombre": "TEST1",
                "PersonaPrimerApellido": "USER1",
                "FechaProcesamiento": "2025-01-09T15:00:00Z"
            },
            {
                "NombreCompleto": "PAN AMERICAN LIFE DE ECUADOR",
                "IdFactura": "TEST002",
                "IdAseguradora": 14,
                "NumDocIdentidad": "1234567891",
                "PersonaPrimerNombre": "TEST2",
                "PersonaPrimerApellido": "USER2",
                "FechaProcesamiento": "2025-01-09T15:01:00Z"
            },
            {
                "NombreCompleto": "PAN AMERICAN LIFE DE ECUADOR",
                "IdFactura": "TEST003",
                "IdAseguradora": 14,
                "NumDocIdentidad": "1234567892",
                "PersonaPrimerNombre": "TEST3",
                "PersonaPrimerApellido": "USER3",
                "FechaProcesamiento": "2025-01-09T15:02:00Z"
            }
        ]
        
        print(f"🚀 Publicando {len(test_messages)} mensajes de prueba...")
        
        for i, message in enumerate(test_messages, 1):
            client.publish_message(message)
            print(f"✅ Mensaje {i} publicado: {message['IdFactura']}")
            time.sleep(0.5)  # Pequeña pausa entre mensajes
        
        print(f"\n📊 Total de mensajes publicados: {len(test_messages)}")
        print("💡 Ahora ejecuta el procesador para ver el caché en acción")
        
    except Exception as e:
        print(f"❌ Error publicando mensajes: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    publish_multiple_test_messages()
