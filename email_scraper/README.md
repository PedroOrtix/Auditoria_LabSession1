# Email Scraper

Extrae nombres, correos y teléfonos públicos de páginas UPM y guarda los resultados en CSV.

## Qué hace
- Detecta correos `@fi.upm.es` y `@upm.es`.
- Captura nombre y teléfono asociados.
- Exporta a CSV y registra logs.

## Configuración
- Edita `config/config.yaml` y ajusta:
   - `url`: página objetivo.
   - `output_dir`: carpeta para CSV.

## Instalación rápida
```bash
conda env create -f config/environment.yml
conda activate email_scraper
# Alternativa
pip install -r config/requirements.txt
```

## Uso
```bash
python main.py
```
Salida en `output/` con nombre `contactos_upm_<timestamp>.csv`. Logs en `scraper.log`.

## Estructura mínima
```
email_scraper/
├── config/ (config.yaml, requirements.txt, environment.yml)
├── src/ (scraper.py, logger.py)
├── output/
└── main.py
```
