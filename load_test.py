#!/usr/bin/env python3
"""
Script de prueba de carga para simular mensajes de producción
"""

import json
import time
import random
from datetime import datetime, timedelta
from src.rabbitmq_client import RabbitMQClient

def generate_test_message(aseguradora_name, message_id):
    """Genera un mensaje de prueba realista"""
    
    # Nombres y apellidos de prueba
    nombres = ["JUAN", "MARIA", "CARLOS", "ANA", "LUIS", "SOFIA", "PEDRO", "CAMILA"]
    apellidos = ["GARCIA", "RODRIGUEZ", "LOPEZ", "MARTINEZ", "GONZALEZ", "PEREZ"]
    
    # Generar datos aleatorios
    nombre = random.choice(nombres)
    apellido = random.choice(apellidos)
    documento = f"{random.randint(1000000000, 9999999999)}"
    factura = f"{random.randint(1000000, 9999999)}"
    
    # Fecha de procesamiento (últimas 24 horas)
    fecha_base = datetime.now() - timedelta(hours=random.randint(0, 24))
    fecha_procesamiento = fecha_base.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    
    return {
        "NombreCompleto": aseguradora_name,
        "IdFactura": factura,
        "IdAseguradora": random.randint(1, 50),
        "NumDocIdentidad": documento,
        "PersonaPrimerNombre": nombre,
        "PersonaSegundoNombre": "",
        "PersonaPrimerApellido": apellido,
        "PersonaSegundoApellido": "",
        "FechaProcesamiento": fecha_procesamiento
    }

def load_test(aseguradora_name, message_count, delay=0.1):
    """Ejecuta una prueba de carga"""
    try:
        client = RabbitMQClient()
        
        print(f"🚀 Iniciando prueba de carga...")
        print(f"📊 Aseguradora: {aseguradora_name}")
        print(f"📈 Mensajes a enviar: {message_count}")
        print(f"⏱️  Delay entre mensajes: {delay} segundos")
        print("=" * 60)
        
        start_time = time.time()
        
        for i in range(message_count):
            message = generate_test_message(aseguradora_name, i + 1)
            
            # Publicar mensaje
            client.publish_message(message)
            
            # Mostrar progreso
            if (i + 1) % 10 == 0 or i == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                print(f"✅ Mensaje {i+1:4d}/{message_count} - Rate: {rate:.2f} msg/s")
            
            # Delay entre mensajes
            if delay > 0:
                time.sleep(delay)
        
        total_time = time.time() - start_time
        final_rate = message_count / total_time if total_time > 0 else 0
        
        print("=" * 60)
        print(f"🎉 Prueba de carga completada!")
        print(f"📊 Total mensajes enviados: {message_count}")
        print(f"⏱️  Tiempo total: {total_time:.2f} segundos")
        print(f"🚀 Rate promedio: {final_rate:.2f} mensajes/segundo")
        print(f"💡 Ahora ejecuta el worker para procesar los mensajes")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error en la prueba de carga: {e}")

def main():
    """Función principal"""
    print("🧪 SISTEMA DE PRUEBA DE CARGA")
    print("=" * 60)
    
    # Configuración de la prueba
    aseguradora = "PAN AMERICAN LIFE DE ECUADOR"
    
    print("📋 Opciones de prueba:")
    print("1. Prueba ligera: 50 mensajes (0.1s delay)")
    print("2. Prueba media: 200 mensajes (0.05s delay)")
    print("3. Prueba pesada: 500 mensajes (0.02s delay)")
    print("4. Prueba personalizada")
    
    try:
        opcion = input("\n🎯 Selecciona una opción (1-4): ").strip()
        
        if opcion == "1":
            load_test(aseguradora, 50, 0.1)
        elif opcion == "2":
            load_test(aseguradora, 200, 0.05)
        elif opcion == "3":
            load_test(aseguradora, 500, 0.02)
        elif opcion == "4":
            count = int(input("📊 Número de mensajes: "))
            delay = float(input("⏱️  Delay entre mensajes (segundos): "))
            load_test(aseguradora, count, delay)
        else:
            print("❌ Opción no válida")
            
    except ValueError:
        print("❌ Valor no válido")
    except KeyboardInterrupt:
        print("\n⏹️  Prueba cancelada por el usuario")

if __name__ == "__main__":
    main()
