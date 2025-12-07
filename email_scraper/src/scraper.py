"""
Módulo para extraer correos electrónicos de páginas web
"""
import re
import csv
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from .logger import setup_logger


logger = setup_logger()


class EmailScraper:
    """Clase para extraer información de contacto de páginas web"""
    
    def __init__(self, url: str):
        """
        Inicializa el scraper con una URL.
        
        Args:
            url: URL de la página web a scrapear
        """
        self.url = url
        self.soup = None
        
    def fetch_page(self) -> bool:
        """
        Descarga el contenido HTML de la página.
        
        Returns:
            True si la descarga fue exitosa, False en caso contrario
        """
        try:
            logger.info(f"Descargando página: {self.url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            self.soup = BeautifulSoup(response.text, 'html.parser')
            logger.info("Página descargada correctamente")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al descargar la página: {e}")
            return False
    
    def extract_contacts(self) -> List[Dict[str, str]]:
        """
        Extrae información de contacto de los elementos con class="card".
        
        Returns:
            Lista de diccionarios con nombre, email y teléfono
        """
        if not self.soup:
            logger.error("No hay contenido HTML cargado")
            return []
        
        contacts = []
        
        # Buscar todos los elementos con class="card"
        cards = self.soup.find_all(class_="card")
        logger.info(f"Encontrados {len(cards)} elementos con class='card'")
        
        # Patrón para emails normales
        email_pattern = r'[A-Za-z0-9._%+-]+@(?:fi\.upm\.es|upm\.es)'
        phone_pattern = r'\d{9}'  # Teléfonos de 9 dígitos
        
        for idx, card in enumerate(cards, 1):
            # Primero intentar buscar emails en el texto normal
            card_text = card.get_text()
            emails = re.findall(email_pattern, card_text, re.IGNORECASE)
            
            # Si no encontramos emails, buscar patrón con imagen (@ oculto)
            if not emails:
                # Buscar imágenes que puedan ser el símbolo @
                img_tags = card.find_all('img')
                for img in img_tags:
                    # Obtener el texto antes y después de la imagen
                    prev_text = ""
                    next_text = ""
                    
                    # Navegar hacia atrás para encontrar el usuario
                    prev_sibling = img.previous_sibling
                    if prev_sibling:
                        prev_text = str(prev_sibling).strip()
                    
                    # Navegar hacia adelante para encontrar el dominio
                    next_sibling = img.next_sibling
                    if next_sibling:
                        next_text = str(next_sibling).strip()
                    
                    # Extraer usuario (última palabra antes de la imagen)
                    user_match = re.search(r'([A-Za-z0-9._-]+)\s*$', prev_text)
                    # Extraer dominio (primera palabra después de la imagen)
                    domain_match = re.search(r'^\s*(fi\.upm\.es|upm\.es)', next_text, re.IGNORECASE)
                    
                    if user_match and domain_match:
                        reconstructed_email = f"{user_match.group(1)}@{domain_match.group(1)}"
                        emails.append(reconstructed_email)
                        logger.debug(f"Email reconstruido: {reconstructed_email}")
            
            # Extraer teléfonos
            phones = re.findall(phone_pattern, card_text)
            
            # Extraer nombre (generalmente está en <strong>)
            name_tag = card.find('strong')
            name = name_tag.get_text().strip() if name_tag else ""
            
            # Si encontramos al menos un email, guardar la información
            if emails:
                contact = {
                    'nombre': name,
                    'email': emails[0] if emails else "",  # Primer email encontrado
                    'telefono': phones[0] if phones else ""  # Primer teléfono encontrado
                }
                contacts.append(contact)
                logger.debug(f"Contacto {idx}: {contact}")
        
        logger.info(f"Extraídos {len(contacts)} contactos")
        return contacts
    
    def save_to_csv(self, contacts: List[Dict[str, str]], output_file: str):
        """
        Guarda los contactos en un archivo CSV.
        
        Args:
            contacts: Lista de diccionarios con información de contacto
            output_file: Ruta del archivo CSV de salida
        """
        if not contacts:
            logger.warning("No hay contactos para guardar")
            return
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['nombre', 'email', 'telefono']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(contacts)
                
            logger.info(f"Contactos guardados en: {output_file}")
            logger.info(f"Total de contactos guardados: {len(contacts)}")
            
        except Exception as e:
            logger.error(f"Error al guardar el archivo CSV: {e}")
    
    def run(self, output_file: str):
        """
        Ejecuta el proceso completo de scraping.
        
        Args:
            output_file: Ruta del archivo CSV de salida
        """
        logger.info("=== Iniciando proceso de scraping ===")
        
        if not self.fetch_page():
            logger.error("No se pudo descargar la página")
            return
        
        contacts = self.extract_contacts()
        
        if contacts:
            self.save_to_csv(contacts, output_file)
            logger.info("=== Proceso completado exitosamente ===")
        else:
            logger.warning("No se encontraron contactos")
