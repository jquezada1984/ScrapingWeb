#!/usr/bin/env python3
import pika
import json
from datetime import datetime

def send_test_message():
    try:
        # Conectar a RabbitMQ con credenciales
        credentials = pika.PlainCredentials('admin', 'admin123')
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost', 5672, '/', credentials)
        )
        channel = connection.channel()
        
        # Crear mensaje de prueba
        mensaje_prueba = {
            "TipoMensaje": "procesamiento_aseguradora",
            "IdFactura": "TEST-001",
            "FechaProcesamiento": datetime.now().isoformat(),
            "TotalClientes": 1,
            "Clientes": [
                {
                    "IdFactura": "TEST-001",
                    "NumDocIdentidad": "0702094525",
                    "NombreCompleto": "PAN AMERICAN LIFE DE ECUADOR",
                    "FechaNacimiento": "1990-01-01",
                    "Estado": "Pendiente"
                }
            ]
        }
        
        # Enviar mensaje
        channel.basic_publish(
            exchange='aseguradora_exchange',
            routing_key='aseguradora',
            body=json.dumps(mensaje_prueba),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Hacer el mensaje persistente
                content_type='application/json'
            )
        )
        
        print("Mensaje de prueba enviado exitosamente")
        print(f"Contenido del mensaje:")
        print(f"   - ID: {mensaje_prueba['IdFactura']}")
        print(f"   - Cliente: {mensaje_prueba['Clientes'][0]['NombreCompleto']}")
        print(f"   - Total clientes: {mensaje_prueba['TotalClientes']}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"Error enviando mensaje de prueba: {e}")
        return False

if __name__ == "__main__":
    send_test_message()
