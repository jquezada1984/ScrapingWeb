#!/usr/bin/env python3
"""
Script para encontrar la URL correcta de la página de búsqueda
después del login en PAN AMERICAN LIFE DE ECUADOR
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def encontrar_url_busqueda():
    """Encuentra la URL correcta de la página de búsqueda"""
    
    print("🔍 Buscando URL de la página de búsqueda...")
    print("=" * 60)
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        # Crear driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("✅ Driver de Chrome configurado")
        
        # 1. Ir a la página de login
        url_login = "https://attest.palig.com/as/authorization.oauth2?client_id=cf7770f3699048ca9c61358b4dff25f5&redirect_uri=https%3A%2F%2Fbenefitsdirect.palig.com%2FInicio%2FLogin.aspx&response_type=code%20id_token&scope=openid%20profile%20email%20phone&state=OpenIdConnect.AuthenticationProperties%3DTBYyPWZT_d1ZE_uAG3CKh3HsoxTt77sdU39y8JDs7IOuNQ90L-8LKm0LywIZTuOPxnSIZ3tQ280RiX9A7UhlbevOoIWavNKgzAePmzzGeVs7BEZJ30VOFBrDb1lOuZZHXPBPyFjAB79z2H16-4ZMdbeXsll9vvQYwGEZ-wsT_V6XBo_n6rvja_bvMdoSTLq9qZNpRunGJp5OAURWnVJ64vS_7M3A6nDhPnwa-f97XD50MvEduGmNxJU4c4GTKZX7baDKXCit8orDw2iJfjFaaiXmgssMdAaTYs8Dj3c7Jvm7KshZhcC9nXdk9KnB2i0t&response_mode=form_post&nonce=638919538746530905.MzI3NGIzOTItZTA3OS00YmUwLThkZTQtNDg2N2NiOGU1NzMyMDNjMmZlNTMtN2E3Yy00ZjM2LTg0YWEtM2YwMDUyMjY4MTM0&x-client-SKU=ID_NET451&x-client-ver=5.6.0.0"
        
        print(f"🌐 Navegando a página de login...")
        driver.get(url_login)
        time.sleep(3)
        
        print(f"✅ Página de login cargada")
        print(f"   📍 URL: {driver.current_url}")
        print(f"   📄 Título: {driver.title}")
        
        # 2. Hacer login
        print("\n🔐 Ejecutando login...")
        
        # Usuario
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
        )
        username_field.clear()
        username_field.send_keys("conveniosyseguros@mediglobal.com.ec")
        print("✅ Usuario ingresado")
        
        # Contraseña
        password_field = driver.find_element(By.CSS_SELECTOR, "#password")
        password_field.clear()
        password_field.send_keys("Mediglobal1")
        print("✅ Contraseña ingresada")
        
        # Botón de login
        login_button = driver.find_element(By.CSS_SELECTOR, "a[title='Inicio de sesión']")
        print(f"🎯 Botón encontrado: {login_button.tag_name} - Texto: '{login_button.text}'")
        print(f"   📝 Atributos: id='{login_button.get_attribute('id')}', class='{login_button.get_attribute('class')}'")
        
        # Hacer click y verificar
        login_button.click()
        print("✅ Botón de login clickeado")
        
        # Verificar si hay algún mensaje de error inmediato
        time.sleep(2)
        try:
            mensajes = driver.find_elements(By.CSS_SELECTOR, '.message, .alert, .notification, [class*="message"]')
            if mensajes:
                print("📢 Mensajes encontrados después del click:")
                for msg in mensajes[:3]:
                    print(f"   • {msg.text.strip()}")
        except:
            pass
        
        # 3. Esperar redirección
        print("\n⏳ Esperando redirección...")
        
        # Esperar más tiempo y verificar cambios
        for i in range(1, 11):  # Esperar hasta 30 segundos
            time.sleep(3)
            url_actual = driver.current_url
            titulo_actual = driver.title
            
            print(f"   ⏳ Intento {i}/10 - URL: {url_actual[:80]}...")
            print(f"      Título: {titulo_actual}")
            
            # Verificar si cambió la URL (no es la de login)
            if "attest.palig.com" not in url_actual or "authorization.oauth2" not in url_actual:
                print(f"✅ ¡Redirección detectada en intento {i}!")
                break
                
            # Verificar si hay errores en la página
            try:
                errores = driver.find_elements(By.CSS_SELECTOR, '.error, .alert, .message-error, [class*="error"]')
                if errores:
                    print(f"⚠️ Errores encontrados en la página:")
                    for error in errores[:3]:
                        print(f"      • {error.text.strip()}")
                    break
            except:
                pass
        
        print(f"✅ Redirección completada")
        print(f"   📍 URL actual: {driver.current_url}")
        print(f"   📄 Título actual: {driver.title}")
        
        # 4. Buscar campos de búsqueda
        print("\n🔍 Buscando campos de búsqueda...")
        
        # Buscar el campo de identificación
        try:
            campo_identificacion = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="ctl00$ContenidoPrincipal$CtrlBuscaAseguradoProv$txtIdentificacionAseg"]'))
            )
            print("✅ Campo de identificación encontrado!")
            print(f"   📝 Atributos: id='{campo_identificacion.get_attribute('id')}', name='{campo_identificacion.get_attribute('name')}'")
            
            # Buscar el botón de búsqueda
            boton_buscar = driver.find_element(By.CSS_SELECTOR, 'a[id="ContenidoPrincipal_CtrlBuscaAseguradoProv_lnkBuscar"]')
            print("✅ Botón de búsqueda encontrado!")
            print(f"   📝 Texto: '{boton_buscar.text}'")
            
            print("\n🎯 ¡PÁGINA DE BÚSQUEDA ENCONTRADA!")
            print(f"   🌐 URL: {driver.current_url}")
            print(f"   📄 Título: {driver.title}")
            
            # Guardar la URL encontrada
            with open('url_busqueda_encontrada.txt', 'w') as f:
                f.write(f"URL de búsqueda encontrada: {driver.current_url}\n")
                f.write(f"Título: {driver.title}\n")
                f.write(f"Campo identificación: {campo_identificacion.get_attribute('name')}\n")
                f.write(f"Botón búsqueda: {boton_buscar.get_attribute('id')}\n")
            
            print("\n💾 URL guardada en 'url_busqueda_encontrada.txt'")
            
        except Exception as e:
            print(f"❌ No se encontraron los campos de búsqueda: {e}")
            print("\n🔍 Buscando elementos en la página...")
            
            # Mostrar todos los inputs
            inputs = driver.find_elements(By.CSS_SELECTOR, 'input')
            print(f"📝 Inputs encontrados: {len(inputs)}")
            for i, inp in enumerate(inputs[:10]):  # Mostrar solo los primeros 10
                print(f"   {i+1}. id='{inp.get_attribute('id')}', name='{inp.get_attribute('name')}', placeholder='{inp.get_attribute('placeholder')}'")
            
            # Mostrar todos los enlaces
            enlaces = driver.find_elements(By.CSS_SELECTOR, 'a')
            print(f"\n🔗 Enlaces encontrados: {len(enlaces)}")
            for i, enlace in enumerate(enlaces[:10]):  # Mostrar solo los primeros 10
                texto = enlace.text.strip()
                if texto:
                    print(f"   {i+1}. '{texto}' - id='{enlace.get_attribute('id')}'")
        
        print("\n" + "=" * 60)
        print("✅ Análisis completado")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("🔌 Driver cerrado")

if __name__ == "__main__":
    print("🚀 Iniciando búsqueda de URL de búsqueda...")
    print("=" * 60)
    encontrar_url_busqueda()
    print("=" * 60)
    print("✅ Script completado")
