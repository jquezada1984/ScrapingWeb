#!/usr/bin/env python3
"""
Script final para probar VNC con Selenium
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_vnc_final():
    print("🔧 Probando VNC con Selenium...")
    
    # Configuración mínima
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    # NO usar headless
    chrome_options.add_argument("--no-headless")
    
    try:
        print("🔗 Conectando a Selenium Grid...")
        driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            options=chrome_options
        )
        
        print("✅ Conexión exitosa!")
        print("🌐 Navegando a Google...")
        driver.get("https://www.google.com")
        
        print("⏳ Esperando 20 segundos...")
        print("📺 Ve a http://localhost:7900 para ver el navegador")
        
        for i in range(20):
            print(f"⏰ {20-i} segundos restantes...")
            time.sleep(1)
        
        print("🔍 Escribiendo en el campo de búsqueda...")
        search_box = driver.find_element("name", "q")
        search_box.send_keys("Selenium VNC Test - Deberías ver esto en VNC")
        
        print("⏳ Esperando otros 10 segundos...")
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
    test_vnc_final()
