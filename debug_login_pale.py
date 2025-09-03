#!/usr/bin/env python3
"""
Script para debuggear el proceso de login de PAN AMERICAN LIFE DE ECUADOR
y encontrar por qué no funciona la autenticación
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def debug_login_pale():
    """Debuggea el proceso de login para encontrar el problema"""
    
    print("🔍 Debuggeando login de PAN AMERICAN LIFE DE ECUADOR...")
    print("=" * 70)
    
    # Configurar Chrome SIN headless para ver qué pasa
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Comentado para debugging
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        # Crear driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("✅ Driver de Chrome configurado (modo visible para debugging)")
        
        # 1. Ir a la página de login
        url_login = "https://attest.palig.com/as/authorization.oauth2?client_id=cf7770f3699048ca9c61358b4dff25f5&redirect_uri=https%3A%2F%2Fbenefitsdirect.palig.com%2FInicio%2FLogin.aspx&response_type=code%20id_token&scope=openid%20profile%20email%20phone&state=OpenIdConnect.AuthenticationProperties%3DTBYyPWZT_d1ZE_uAG3CKh3HsoxTt77sdU39y8JDs7IOuNQ90L-8LKm0LywIZTuOPxnSIZ3tQ280RiX9A7UhlbevOoIWavNKgzAePmzzGeVs7BEZJ30VOFBrDb1lOuZZHXPBPyFjAB79z2H16-4ZMdbeXsll9vvQYwGEZ-wsT_V6XBo_n6rvja_bvMdoSTLq9qZNpRunGJp5OAURWnVJ64vS_7M3A6nDhPnwa-f97XD50MvEduGmNxJU4c4GTKZX7baDKXCit8orDw2iJfjFaaiXmgssMdAaTYs8Dj3c7Jvm7KshZhcC9nXdk9KnB2i0t&response_mode=form_post&nonce=638919538746530905.MzI3NGIzOTItZTA3OS00YmUwLThkZTQtNDg2N2NiOGU1NzMyMDNjMmZlNTMtN2E3Yy00ZjM2LTg0YWEtM2YwMDUyMjY4MTM0&x-client-SKU=ID_NET451&x-client-ver=5.6.0.0"
        
        print(f"🌐 Navegando a página de login...")
        driver.get(url_login)
        time.sleep(3)
        
        print(f"✅ Página de login cargada")
        print(f"   📍 URL: {driver.current_url}")
        print(f"   📄 Título: {driver.title}")
        
        # 2. Analizar la página de login
        print("\n🔍 Analizando página de login...")
        
        # Buscar todos los elementos importantes
        try:
            # Verificar si hay algún mensaje de error inicial
            errores_iniciales = driver.find_elements(By.CSS_SELECTOR, '.error, .alert, .message, [class*="error"], [class*="alert"]')
            if errores_iniciales:
                print("⚠️ Mensajes/errores encontrados en la página inicial:")
                for error in errores_iniciales[:5]:
                    texto = error.text.strip()
                    if texto:
                        print(f"   • {texto}")
            
            # Verificar si hay captcha
            captchas = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="captcha"], .captcha, [class*="captcha"]')
            if captchas:
                print("🎯 CAPTCHA detectado en la página!")
                for captcha in captchas:
                    print(f"   • Tipo: {captcha.tag_name}, src: {captcha.get_attribute('src')}")
            
            # Verificar si hay campos ocultos
            campos_ocultos = driver.find_elements(By.CSS_SELECTOR, 'input[type="hidden"]')
            if campos_ocultos:
                print(f"🔍 Campos ocultos encontrados: {len(campos_ocultos)}")
                for campo in campos_ocultos[:5]:
                    nombre = campo.get_attribute('name') or campo.get_attribute('id') or 'sin-nombre'
                    valor = campo.get_attribute('value') or 'sin-valor'
                    print(f"   • {nombre}: {valor}")
                    
        except Exception as e:
            print(f"⚠️ Error analizando página inicial: {e}")
        
        # 3. Hacer login paso a paso
        print("\n🔐 Ejecutando login paso a paso...")
        
        # Usuario
        try:
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
            )
            username_field.clear()
            username_field.send_keys("conveniosyseguros@mediglobal.com.ec")
            print("✅ Usuario ingresado")
            
            # Verificar que se ingresó correctamente
            valor_username = username_field.get_attribute('value')
            print(f"   📝 Valor en campo: '{valor_username}'")
            
        except Exception as e:
            print(f"❌ Error con campo usuario: {e}")
            return
        
        # Contraseña
        try:
            password_field = driver.find_element(By.CSS_SELECTOR, "#password")
            password_field.clear()
            password_field.send_keys("Mediglobal1")
            print("✅ Contraseña ingresada")
            
            # Verificar que se ingresó correctamente
            valor_password = password_field.get_attribute('value')
            print(f"   📝 Valor en campo: '{valor_password[:3]}***'")
            
        except Exception as e:
            print(f"❌ Error con campo contraseña: {e}")
            return
        
        # 4. Verificar si hay campos adicionales requeridos
        print("\n🔍 Verificando campos adicionales...")
        
        try:
            # Buscar campos requeridos o con validación
            campos_requeridos = driver.find_elements(By.CSS_SELECTOR, 'input[required], input[aria-required="true"], .required')
            if campos_requeridos:
                print(f"⚠️ Campos marcados como requeridos: {len(campos_requeridos)}")
                for campo in campos_requeridos:
                    nombre = campo.get_attribute('name') or campo.get_attribute('id') or 'sin-nombre'
                    tipo = campo.get_attribute('type') or 'text'
                    print(f"   • {nombre} (tipo: {tipo})")
            
            # Buscar campos con validación JavaScript
            campos_validacion = driver.find_elements(By.CSS_SELECTOR, 'input[onchange], input[onblur], input[onkeyup]')
            if campos_validacion:
                print(f"🔍 Campos con validación JavaScript: {len(campos_validacion)}")
                for campo in campos_validacion[:3]:
                    nombre = campo.get_attribute('name') or campo.get_attribute('id') or 'sin-nombre'
                    onchange = campo.get_attribute('onchange') or ''
                    onblur = campo.get_attribute('onblur') or ''
                    onkeyup = campo.get_attribute('onkeyup') or ''
                    print(f"   • {nombre}: onchange='{onchange[:50]}...', onblur='{onblur[:50]}...', onkeyup='{onkeyup[:50]}...'")
                    
        except Exception as e:
            print(f"⚠️ Error verificando campos adicionales: {e}")
        
        # 5. Hacer click en el botón de login
        print("\n🎯 Haciendo click en botón de login...")
        
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, "a[title='Inicio de sesión']")
            print(f"✅ Botón encontrado: {login_button.tag_name}")
            print(f"   📝 Texto: '{login_button.text}'")
            print(f"   📝 Atributos: id='{login_button.get_attribute('id')}', class='{login_button.get_attribute('class')}'")
            
            # Verificar si el botón está habilitado
            if not login_button.is_enabled():
                print("⚠️ Botón de login NO está habilitado!")
                return
            
            # Hacer click
            login_button.click()
            print("✅ Botón de login clickeado")
            
        except Exception as e:
            print(f"❌ Error con botón de login: {e}")
            return
        
        # 6. Monitorear cambios después del click
        print("\n⏳ Monitoreando cambios después del click...")
        
        url_inicial = driver.current_url
        titulo_inicial = driver.title
        
        print(f"   📍 URL inicial: {url_inicial}")
        print(f"   📄 Título inicial: {titulo_inicial}")
        
        # Esperar y monitorear cambios
        for i in range(1, 16):  # Esperar hasta 45 segundos
            time.sleep(3)
            
            url_actual = driver.current_url
            titulo_actual = driver.title
            
            print(f"   ⏳ Intento {i}/15 - URL: {url_actual[:80]}...")
            print(f"      Título: {titulo_actual}")
            
            # Verificar si cambió la URL
            if url_actual != url_inicial:
                print(f"✅ ¡Cambio de URL detectado en intento {i}!")
                print(f"   📍 De: {url_inicial}")
                print(f"   📍 A: {url_actual}")
                break
            
            # Verificar si cambió el título
            if titulo_actual != titulo_inicial:
                print(f"✅ ¡Cambio de título detectado en intento {i}!")
                print(f"   📄 De: {titulo_inicial}")
                print(f"   📄 A: {titulo_actual}")
                break
            
            # Verificar si hay errores o mensajes
            try:
                errores = driver.find_elements(By.CSS_SELECTOR, '.error, .alert, .message, [class*="error"], [class*="alert"], [class*="message"]')
                if errores:
                    print(f"⚠️ Mensajes/errores encontrados en intento {i}:")
                    for error in errores[:3]:
                        texto = error.text.strip()
                        if texto:
                            print(f"      • {texto}")
                    break
            except:
                pass
            
            # Verificar si aparecieron nuevos elementos
            try:
                nuevos_inputs = driver.find_elements(By.CSS_SELECTOR, 'input:not([id="username"]):not([id="password"])')
                if len(nuevos_inputs) > 6:  # Más de los 6 iniciales
                    print(f"✅ Nuevos campos detectados en intento {i}: {len(nuevos_inputs)}")
                    break
            except:
                pass
        
        # 7. Análisis final
        print("\n🔍 Análisis final de la página...")
        
        url_final = driver.current_url
        titulo_final = driver.title
        
        print(f"   📍 URL final: {url_final}")
        print(f"   📄 Título final: {titulo_final}")
        
        # Verificar si llegamos a la página de búsqueda
        if "attest.palig.com" not in url_final or "authorization.oauth2" not in url_final:
            print("🎯 ¡REDIRECCIÓN EXITOSA! Ahora buscar campos de búsqueda...")
            
            # Buscar campos de búsqueda
            try:
                campo_identificacion = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="ctl00$ContenidoPrincipal$CtrlBuscaAseguradoProv$txtIdentificacionAseg"]'))
                )
                print("✅ Campo de identificación encontrado!")
                
                boton_buscar = driver.find_element(By.CSS_SELECTOR, 'a[id="ContenidoPrincipal_CtrlBuscaAseguradoProv_lnkBuscar"]')
                print("✅ Botón de búsqueda encontrado!")
                
                print(f"\n🎯 ¡PÁGINA DE BÚSQUEDA ENCONTRADA!")
                print(f"   🌐 URL: {url_final}")
                print(f"   📄 Título: {titulo_final}")
                
                # Guardar la URL encontrada
                with open('url_busqueda_encontrada.txt', 'w') as f:
                    f.write(f"URL de búsqueda encontrada: {url_final}\n")
                    f.write(f"Título: {titulo_final}\n")
                
                print("\n💾 URL guardada en 'url_busqueda_encontrada.txt'")
                
            except Exception as e:
                print(f"❌ No se encontraron campos de búsqueda: {e}")
                
        else:
            print("❌ NO se detectó redirección - Login falló")
            
            # Mostrar elementos disponibles
            try:
                inputs = driver.find_elements(By.CSS_SELECTOR, 'input')
                print(f"\n📝 Inputs disponibles: {len(inputs)}")
                for i, inp in enumerate(inputs[:10]):
                    print(f"   {i+1}. id='{inp.get_attribute('id')}', name='{inp.get_attribute('name')}', placeholder='{inp.get_attribute('placeholder')}'")
                
                enlaces = driver.find_elements(By.CSS_SELECTOR, 'a')
                print(f"\n🔗 Enlaces disponibles: {len(enlaces)}")
                for i, enlace in enumerate(enlaces[:10]):
                    texto = enlace.text.strip()
                    if texto:
                        print(f"   {i+1}. '{texto}' - id='{enlace.get_attribute('id')}'")
                        
            except Exception as e:
                print(f"⚠️ Error mostrando elementos: {e}")
        
        print("\n" + "=" * 70)
        print("✅ Debugging completado")
        
        # Pausa para que el usuario pueda ver la página
        print("\n⏸️ Pausando para inspección manual...")
        print("   Presiona Enter para continuar...")
        input()
        
    except Exception as e:
        print(f"❌ Error durante el debugging: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("🔌 Driver cerrado")

if __name__ == "__main__":
    print("🚀 Iniciando debugging de login...")
    print("=" * 70)
    debug_login_pale()
    print("=" * 70)
    print("✅ Script completado")
