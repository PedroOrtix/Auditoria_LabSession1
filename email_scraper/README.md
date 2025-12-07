# Email Scraper - UPM FI

Script para extraer correos electrónicos, nombres y teléfonos de la página de departamentos de la Facultad de Informática de la UPM.

## Características

- Extrae correos electrónicos de dominios `@fi.upm.es` y `@upm.es`
- Captura nombres y números de teléfono asociados
- Exporta los datos a formato CSV
- Sistema de logging completo
- Configuración externa mediante YAML

## Estructura del Proyecto
````markdown
# Email Scraper - UPM FI

Script para extraer correos electrónicos, nombres y teléfonos de las páginas de departamentos de la Facultad de Informática de la UPM.

## Características

- Extrae correos electrónicos de los dominios `@fi.upm.es` y `@upm.es`
- Captura nombres y números de teléfono asociados
- Exporta los datos a formato CSV
- Sistema de logging completo
- Configuración externa mediante YAML

## Estructura del Proyecto

```
email_scraper/
├── src/                    # Código fuente
│   ├── __init__.py
│   ├── scraper.py         # Lógica de scraping
│   └── logger.py          # Configuración de logging
├── config/                 # Configuración
│   ├── config.yaml        # Parámetros del scraper
│   ├── requirements.txt   # Dependencias pip
│   └── environment.yml    # Entorno Anaconda
├── output/                 # Archivos CSV generados
├── main.py                # Script principal
└── README.md              # Documentación
```

## Instalación

### Opción 1: Usando Conda (Recomendado)

```bash
# Crear el entorno desde el archivo environment.yml
conda env create -f config/environment.yml

# Activar el entorno
conda activate email_scraper
```

### Opción 2: Usando pip

```bash
# Instalar dependencias
pip install -r config/requirements.txt
```

## Uso

```bash
# Asegúrate de tener el entorno activado
conda activate email_scraper

# Ejecutar el script
python main.py
```

El script generará un archivo CSV en el directorio `output/` con el formato:
`contactos_upm_YYYYMMDD_HHMMSS.csv`

## Configuración

Edita el archivo `config/config.yaml` para cambiar:

- **url**: URL de la página a scrapear
- **output_dir**: Directorio donde se guardarán los archivos CSV

## Formato de salida

El archivo CSV contiene las siguientes columnas:

| nombre | email | telefono |
|--------|-------|----------|
| Nombre completo | correo@fi.upm.es | 910673072 |

## Logs

Los logs se guardan en el archivo `scraper.log` en el directorio raíz del proyecto.

## Funcionamiento técnico

1. **Descarga**: Realiza una petición HTTP a la URL configurada
2. **Parseo**: Usa BeautifulSoup para analizar el HTML
3. **Extracción**: Busca elementos con `class="card"` y extrae:
   - Nombres (etiquetas `<strong>`)
   - Emails (regex: `[A-Za-z0-9._%+-]+@(?:fi\.upm\.es|upm\.es)`) 
   - Teléfonos (regex: `\d{9}`)
4. **Exportación**: Guarda los datos en formato CSV

## Requisitos

- Python 3.11+
- BeautifulSoup4
- Requests
- PyYAML
- lxml

## Notas

- El script respeta la estructura de la página y solo extrae datos visibles públicamente
- Los correos se filtran específicamente para dominios UPM
- Se genera un archivo nuevo en cada ejecución para mantener histórico

````
