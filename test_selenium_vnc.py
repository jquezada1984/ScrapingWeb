#!/usr/bin/env python3
"""
Script de prueba para verificar que Selenium Grid y VNC funcionen correctamente
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def test_selenium_vnc():
    """Prueba básica de Selenium con VNC"""
    print("🔧 Configurando Selenium para prueba...")
    
    # Opciones de Chrome
    chrome_options = Options()
    # NO usar headless para poder ver en VNC
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    
    try:
        # Conectar a Selenium Grid
        print("🔗 Conectando a Selenium Grid...")
        driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            options=chrome_options
        )
        
        print("✅ Conexión exitosa a Selenium Grid")
        
        # Navegar a una página simple
        print("🌐 Navegando a Google...")
        driver.get("https://www.google.com")
        
        print("⏳ Esperando 10 segundos para que puedas ver en VNC...")
        time.sleep(10)
        
        # Buscar el campo de búsqueda
        print("🔍 Buscando campo de búsqueda...")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("Selenium Grid VNC Test")
        
        print("⏳ Esperando otros 5 segundos...")
        time.sleep(5)
        
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
    test_selenium_vnc()
