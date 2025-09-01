#!/usr/bin/env python3
"""
Script para probar las conexiones a SQL Server y RabbitMQ
"""

import sys
import logging
from src.database import DatabaseManager
from src.rabbitmq_client import RabbitMQClient
from src.config import Config

def test_sql_server():
    """Prueba la conexión a SQL Server"""
    print("🔍 Probando conexión a SQL Server...")
    
    try:
        db_manager = DatabaseManager()
        
        if db_manager.test_connection():
            print("✅ Conexión a SQL Server exitosa")
            
            # Probar una consulta simple
            result = db_manager.execute_query("SELECT @@VERSION as version")
            if result:
                print(f"📊 Versión de SQL Server: {result[0]['version'][:50]}...")
            
            db_manager.close()
            return True
        else:
            print("❌ Error al conectar con SQL Server")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión a SQL Server: {e}")
        return False

def test_rabbitmq():
    """Prueba la conexión a RabbitMQ"""
    print("\n🔍 Probando conexión a RabbitMQ...")
    
    try:
        rabbitmq_client = RabbitMQClient()
        
        # Probar publicación de un mensaje de prueba
        test_message = {
            'test': True,
            'message': 'Mensaje de prueba de conexión'
        }
        
        if rabbitmq_client.publish_message(test_message):
            print("✅ Conexión a RabbitMQ exitosa")
            print("✅ Publicación de mensajes funcionando")
            
            # Obtener información de la cola
            queue_info = rabbitmq_client.get_queue_info()
            if queue_info:
                print(f"📊 Cola: {queue_info['queue_name']}")
                print(f"📊 Mensajes en cola: {queue_info['message_count']}")
                print(f"📊 Consumidores: {queue_info['consumer_count']}")
            
            rabbitmq_client.close()
            return True
        else:
            print("❌ Error al publicar mensaje en RabbitMQ")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión a RabbitMQ: {e}")
        return False

def show_config():
    """Muestra la configuración actual"""
    print("⚙️ Configuración actual:")
    print(f"   SQL Server: {Config.SQL_SERVER_HOST}:{Config.SQL_SERVER_PORT}")
    print(f"   Base de datos: {Config.SQL_SERVER_DATABASE}")
    print(f"   Usuario SQL: {Config.SQL_SERVER_USERNAME}")
    print(f"   RabbitMQ: {Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}")
    print(f"   Usuario RabbitMQ: {Config.RABBITMQ_USERNAME}")
    print(f"   Cola: {Config.RABBITMQ_QUEUE}")
    print(f"   Exchange: {Config.RABBITMQ_EXCHANGE}")

def main():
    """Función principal"""
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Iniciando pruebas de conexión...\n")
    
    # Mostrar configuración
    show_config()
    print()
    
    # Probar conexiones
    sql_success = test_sql_server()
    rabbitmq_success = test_rabbitmq()
    
    print("\n" + "="*50)
    print("📋 RESUMEN DE PRUEBAS")
    print("="*50)
    print(f"SQL Server: {'✅ OK' if sql_success else '❌ ERROR'}")
    print(f"RabbitMQ: {'✅ OK' if rabbitmq_success else '❌ ERROR'}")
    
    if sql_success and rabbitmq_success:
        print("\n🎉 ¡Todas las conexiones están funcionando correctamente!")
        print("   Puedes ejecutar el worker con: python main.py")
        return 0
    else:
        print("\n⚠️  Algunas conexiones fallaron. Revisa la configuración en .env")
        return 1

if __name__ == "__main__":
    sys.exit(main())
