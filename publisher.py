#!/usr/bin/env python3
"""
Script para publicar tareas de scraping en RabbitMQ
"""

import json
import argparse
import logging
from src.rabbitmq_client import RabbitMQClient
from src.config import Config

def setup_logging():
    """Configura el logging"""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def publish_single_task(url: str, use_selenium: bool = False, selectors: dict = None):
    """Publica una sola tarea de scraping"""
    try:
        with RabbitMQClient() as client:
            message = {
                'url': url,
                'use_selenium': use_selenium,
                'selectors': selectors or {},
                'timestamp': time.time()
            }
            
            success = client.publish_message(message)
            
            if success:
                print(f"✅ Tarea publicada exitosamente para: {url}")
            else:
                print(f"❌ Error al publicar tarea para: {url}")
                
            return success
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def publish_from_file(file_path: str, use_selenium: bool = False, selectors: dict = None):
    """Publica tareas desde un archivo de texto con URLs"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            urls = [line.strip() for line in file if line.strip()]
        
        print(f"📄 Leyendo {len(urls)} URLs desde {file_path}")
        
        with RabbitMQClient() as client:
            success_count = 0
            
            for i, url in enumerate(urls, 1):
                message = {
                    'url': url,
                    'use_selenium': use_selenium,
                    'selectors': selectors or {},
                    'timestamp': time.time()
                }
                
                success = client.publish_message(message)
                
                if success:
                    success_count += 1
                    print(f"✅ [{i}/{len(urls)}] Publicado: {url}")
                else:
                    print(f"❌ [{i}/{len(urls)}] Error: {url}")
            
            print(f"\n📊 Resumen: {success_count}/{len(urls)} tareas publicadas exitosamente")
            
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {file_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Publicar tareas de scraping en RabbitMQ')
    parser.add_argument('--url', help='URL única para hacer scraping')
    parser.add_argument('--file', help='Archivo con URLs (una por línea)')
    parser.add_argument('--selenium', action='store_true', help='Usar Selenium para el scraping')
    parser.add_argument('--selectors', help='Archivo JSON con selectores CSS')
    
    args = parser.parse_args()
    
    setup_logging()
    
    # Cargar selectores si se proporciona archivo
    selectors = None
    if args.selectors:
        try:
            with open(args.selectors, 'r', encoding='utf-8') as f:
                selectors = json.load(f)
            print(f"📋 Selectores cargados desde: {args.selectors}")
        except Exception as e:
            print(f"❌ Error al cargar selectores: {e}")
            return
    
    # Publicar tarea única
    if args.url:
        publish_single_task(args.url, args.selenium, selectors)
    
    # Publicar desde archivo
    elif args.file:
        publish_from_file(args.file, args.selenium, selectors)
    
    else:
        print("❌ Debes especificar --url o --file")
        parser.print_help()

if __name__ == "__main__":
    import time
    main()
