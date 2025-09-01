#!/usr/bin/env python3
"""
Script de inicio rápido para probar el sistema completo
"""

import time
import json
import logging
from src.scraping_worker import ScrapingWorker
from src.config import Config

def setup_logging():
    """Configura el logging"""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def run_quick_test():
    """Ejecuta una prueba rápida del sistema"""
    print("🚀 Iniciando prueba rápida del sistema de scraping...")
    
    try:
        # Inicializar worker
        worker = ScrapingWorker()
        
        if not worker.initialize():
            print("❌ Error al inicializar el worker")
            return False
        
        print("✅ Worker inicializado correctamente")
        
        # URLs de prueba
        test_urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://example.com"
        ]
        
        print(f"📤 Publicando {len(test_urls)} tareas de prueba...")
        
        # Publicar tareas de prueba
        for i, url in enumerate(test_urls, 1):
            success = worker.publish_scraping_task(url)
            if success:
                print(f"✅ [{i}/{len(test_urls)}] Tarea publicada: {url}")
            else:
                print(f"❌ [{i}/{len(test_urls)}] Error al publicar: {url}")
        
        print("\n📊 Estado de la cola:")
        status = worker.get_queue_status()
        print(f"   Mensajes en cola: {status.get('message_count', 0)}")
        print(f"   Consumidores: {status.get('consumer_count', 0)}")
        
        print("\n⏳ Iniciando procesamiento de mensajes...")
        print("   Presiona Ctrl+C para detener después de procesar algunos mensajes")
        
        # Iniciar procesamiento (se detendrá con Ctrl+C)
        worker.start_consuming()
        
    except KeyboardInterrupt:
        print("\n⏹️  Detención solicitada por el usuario")
        worker.stop()
        return True
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False

def main():
    """Función principal"""
    setup_logging()
    
    print("="*60)
    print("🔧 SISTEMA DE SCRAPING WEB - PRUEBA RÁPIDA")
    print("="*60)
    print()
    print("Este script realizará una prueba completa del sistema:")
    print("1. Inicializará el worker")
    print("2. Publicará tareas de prueba en RabbitMQ")
    print("3. Procesará los mensajes y guardará en SQL Server")
    print()
    
    # Confirmar ejecución
    response = input("¿Deseas continuar? (y/N): ").strip().lower()
    if response not in ['y', 'yes', 'sí', 'si']:
        print("❌ Prueba cancelada")
        return
    
    print()
    
    # Ejecutar prueba
    success = run_quick_test()
    
    if success:
        print("\n🎉 ¡Prueba completada exitosamente!")
        print("   Revisa la base de datos para ver los resultados")
    else:
        print("\n❌ La prueba falló. Revisa los logs para más detalles")

if __name__ == "__main__":
    main()

