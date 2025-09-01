import requests
import time
import logging
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from .config import Config

logger = logging.getLogger(__name__)

class WebScraper:
    """Clase para manejar las operaciones de scraping web"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
        self._setup_selenium()
    
    def _setup_selenium(self):
        """Configura Selenium para casos que requieren JavaScript"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver configurado correctamente")
        except Exception as e:
            logger.warning(f"No se pudo configurar Selenium: {e}")
            self.driver = None
    
    def scrape_with_requests(self, url: str, selectors: Dict[str, str] = None) -> Dict[str, Any]:
        """Realiza scraping usando requests y BeautifulSoup"""
        try:
            logger.info(f"Iniciando scraping de: {url}")
            
            # Realizar petición HTTP
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parsear HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer datos según selectores
            scraped_data = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'timestamp': time.time(),
                'status_code': response.status_code
            }
            
            if selectors:
                for key, selector in selectors.items():
                    try:
                        element = soup.select_one(selector)
                        scraped_data[key] = element.get_text(strip=True) if element else ''
                    except Exception as e:
                        logger.warning(f"Error al extraer {key}: {e}")
                        scraped_data[key] = ''
            
            # Extraer enlaces si no hay selectores específicos
            if not selectors:
                links = soup.find_all('a', href=True)
                scraped_data['links'] = [link['href'] for link in links[:10]]  # Primeros 10 enlaces
            
            logger.info(f"Scraping completado exitosamente para: {url}")
            return scraped_data
            
        except requests.RequestException as e:
            logger.error(f"Error en la petición HTTP para {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Error inesperado durante scraping de {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def scrape_with_selenium(self, url: str, selectors: Dict[str, str] = None, wait_time: int = 10) -> Dict[str, Any]:
        """Realiza scraping usando Selenium para páginas con JavaScript"""
        if not self.driver:
            logger.error("Selenium WebDriver no está disponible")
            return self.scrape_with_requests(url, selectors)
        
        try:
            logger.info(f"Iniciando scraping con Selenium de: {url}")
            
            # Navegar a la URL
            self.driver.get(url)
            
            # Esperar a que la página cargue
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Obtener el HTML de la página
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extraer datos según selectors
            scraped_data = {
                'url': url,
                'title': self.driver.title,
                'timestamp': time.time(),
                'selenium_used': True
            }
            
            if selectors:
                for key, selector in selectors.items():
                    try:
                        # Intentar con Selenium primero
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        scraped_data[key] = element.text.strip()
                    except:
                        try:
                            # Fallback a BeautifulSoup
                            element = soup.select_one(selector)
                            scraped_data[key] = element.get_text(strip=True) if element else ''
                        except Exception as e:
                            logger.warning(f"Error al extraer {key}: {e}")
                            scraped_data[key] = ''
            
            logger.info(f"Scraping con Selenium completado para: {url}")
            return scraped_data
            
        except TimeoutException:
            logger.error(f"Timeout al cargar la página: {url}")
            return {
                'url': url,
                'error': 'Timeout al cargar la página',
                'timestamp': time.time()
            }
        except WebDriverException as e:
            logger.error(f"Error de WebDriver para {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Error inesperado durante scraping con Selenium de {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def scrape_url(self, url: str, use_selenium: bool = False, selectors: Dict[str, str] = None) -> Dict[str, Any]:
        """Método principal para realizar scraping de una URL"""
        # Aplicar delay para ser respetuoso con el servidor
        time.sleep(Config.SCRAPING_DELAY)
        
        if use_selenium and self.driver:
            return self.scrape_with_selenium(url, selectors)
        else:
            return self.scrape_with_requests(url, selectors)
    
    def scrape_multiple_urls(self, urls: List[str], use_selenium: bool = False, selectors: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Realiza scraping de múltiples URLs"""
        results = []
        
        for url in urls:
            try:
                result = self.scrape_url(url, use_selenium, selectors)
                results.append(result)
            except Exception as e:
                logger.error(f"Error al procesar URL {url}: {e}")
                results.append({
                    'url': url,
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        return results
    
    def extract_links_from_page(self, url: str, link_selector: str = 'a[href]') -> List[str]:
        """Extrae enlaces de una página específica"""
        try:
            scraped_data = self.scrape_url(url)
            
            if 'error' in scraped_data:
                return []
            
            # Parsear HTML para extraer enlaces
            soup = BeautifulSoup(scraped_data.get('html', ''), 'html.parser')
            links = soup.select(link_selector)
            
            return [link.get('href') for link in links if link.get('href')]
            
        except Exception as e:
            logger.error(f"Error al extraer enlaces de {url}: {e}")
            return []
    
    def close(self):
        """Cierra las conexiones y libera recursos"""
        if self.session:
            self.session.close()
        
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver cerrado")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
