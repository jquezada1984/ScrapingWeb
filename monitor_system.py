#!/usr/bin/env python3
"""
Monitoreo del sistema en tiempo real
"""

import time
import json
from datetime import datetime
from src.config import Config
from src.rabbitmq_client import RabbitMQClient
from src.database import DatabaseManager

def check_rabbitmq_status():
    """Verifica el estado de RabbitMQ"""
    try:
        client = RabbitMQClient()
        
        # Obtener información de la cola
        queue_info = client.channel.queue_declare(
            queue=Config.RABBITMQ_QUEUE, 
            durable=True, 
            passive=True
        )
        
        message_count = queue_info.method.message_count
        consumer_count = queue_info.method.consumer_count
        
        status = {
            'status': '🟢 Conectado',
            'messages_in_queue': message_count,
            'active_consumers': consumer_count,
            'queue': Config.RABBITMQ_QUEUE,
            'exchange': Config.RABBITMQ_EXCHANGE
        }
        
        client.close()
        return status
        
    except Exception as e:
        return {
            'status': '🔴 Error',
            'error': str(e),
            'messages_in_queue': 0,
            'active_consumers': 0
        }

def check_database_status():
    """Verifica el estado de la base de datos"""
    try:
        db_manager = DatabaseManager()
        
        # Consulta simple para verificar conexión
        result = db_manager.execute_query("SELECT GETDATE() as current_time")
        
        if result:
            status = {
                'status': '🟢 Conectado',
                'current_time': str(result[0]['current_time']),
                'database': Config.SQL_SERVER_DATABASE
            }
        else:
            status = {
                'status': '🟡 Sin respuesta',
                'database': Config.SQL_SERVER_DATABASE
            }
            
        return status
        
    except Exception as e:
        return {
            'status': '🔴 Error',
            'error': str(e),
            'database': Config.SQL_SERVER_DATABASE
        }

def show_system_status():
    """Muestra el estado completo del sistema"""
    print("\n" + "="*80)
    print(f"🔍 MONITOREO DEL SISTEMA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Verificar RabbitMQ
    print("\n📊 ESTADO DE RABBITMQ:")
    rabbitmq_status = check_rabbitmq_status()
    print(f"   Estado: {rabbitmq_status['status']}")
    print(f"   Cola: {rabbitmq_status['queue']}")
    print(f"   Exchange: {rabbitmq_status['exchange']}")
    print(f"   Mensajes en cola: {rabbitmq_status['messages_in_queue']}")
    print(f"   Consumidores activos: {rabbitmq_status['active_consumers']}")
    
    if 'error' in rabbitmq_status:
        print(f"   Error: {rabbitmq_status['error']}")
    
    # Verificar Base de Datos
    print("\n🗄️  ESTADO DE LA BASE DE DATOS:")
    db_status = check_database_status()
    print(f"   Estado: {db_status['status']}")
    print(f"   Base de datos: {db_status['database']}")
    
    if 'current_time' in db_status:
        print(f"   Hora del servidor: {db_status['current_time']}")
    
    if 'error' in db_status:
        print(f"   Error: {db_status['error']}")
    
    # Resumen del sistema
    print("\n📈 RESUMEN DEL SISTEMA:")
    if rabbitmq_status['status'].startswith('🟢') and db_status['status'].startswith('🟢'):
        print("   🟢 SISTEMA OPERATIVO - Listo para procesar mensajes")
    elif rabbitmq_status['status'].startswith('🔴') or db_status['status'].startswith('🔴'):
        print("   🔴 SISTEMA CON ERRORES - Revisar conexiones")
    else:
        print("   🟡 SISTEMA PARCIALMENTE OPERATIVO - Algunos servicios con problemas")
    
    print("\n" + "="*80)

def continuous_monitoring(interval=30):
    """Monitoreo continuo del sistema"""
    print("🚀 Iniciando monitoreo continuo del sistema...")
    print("💡 Presiona Ctrl+C para detener")
    print("⏱️  Intervalo de monitoreo:", interval, "segundos")
    
    try:
        while True:
            show_system_status()
            print(f"\n⏳ Esperando {interval} segundos... (Ctrl+C para detener)")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoreo detenido por el usuario")

def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        continuous_monitoring()
    else:
        show_system_status()
        print("\n💡 Para monitoreo continuo ejecuta: python monitor_system.py --continuous")

if __name__ == "__main__":
    main()
