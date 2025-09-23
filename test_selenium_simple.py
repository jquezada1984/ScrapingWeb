#!/usr/bin/env python3
"""
Script simple para probar Selenium Grid
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_selenium_simple():
    print("🔧 Probando Selenium Grid...")
    
    # Configuración básica
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        print("🔗 Conectando a Selenium Grid...")
        driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            options=chrome_options
        )
        
        print("✅ Conexión exitosa!")
        print("🌐 Navegando a Google...")
        driver.get("https://www.google.com")
        
        print("⏳ Esperando 10 segundos...")
        print("📺 Ve a http://localhost:7900 para ver el navegador")
        time.sleep(10)
        
        print("✅ Prueba completada")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            driver.quit()
            print("🔌 Driver cerrado")
        except:
            pass

if __name__ == "__main__":
    test_selenium_simple()
