# Entrega 1 — Auditoría de Seguridad

**Resumen:** Este repositorio contiene las herramientas y la estructura usadas para la entrega: descubrimiento de subdominios, verificación / extracción basada en `crt.sh`, reconocimiento visual (pipeline con Aquatone y GoWitness) y un scrapper de correos implementado como parte del ejercicio 5 de Automated Information Gathering.

**Estructura y Componentes**
- **`subdomain_discovery/`**: Aquí se realiza el descubrimiento de subdominios utilizando SubFinder. Los resultados se almacenan en los ficheros de `output/` del propio subproyecto.
- **`subdomain_checker/`**: Implementación propia para la extracción y verificación de dominios utilizando la plataforma `crt.sh` (consulta pública de certificados). El código relevante está en `subdomain_checker/src/` y se ha desarrollado un scraper/verificador propio para este propósito.
- **`visual_recon/`**: Carpeta destinada al reconocimiento visual y la organización de los resultados de los subdominios. Contiene el pipeline que procesa las URLs con Aquatone y captura con GoWitness; se incluyen los informes (`aquatone_report/`) y capturas (`gowitness_screens/`).
- **`email_scraper/`**: Implementación del email scrapper incluida en el ejercicio 5 de Automated Information Gathering. El scrapper y sus configuraciones se encuentran en `email_scraper/` (`main.py`, `config/`, `run.sh`).

**Cómo ejecutar (rápido)**
- Subdomain Discovery:
  - `cd subdomain_discovery`
  - Ejecutar: `./run.sh` o `python3 main.py` (según el entorno)
- Domain Checker (crt.sh):
  - `cd subdomain_checker`
  - Ejecutar: `./run.sh` o `python3 main.py` (el script consulta `crt.sh` y procesa los resultados en `output/`)
- Visual Recon (Aquatone + GoWitness):
  - `cd visual_recon`
  - Ejecutar: `./run_aquatone.sh` para generar reports con Aquatone
  - Ejecutar: `./run_gowitness.sh` para capturas con GoWitness
- Email Scraper (Ejercicio 5):
  - `cd email_scraper`
  - Ejecutar: `./run.sh` o `python3 main.py`

**Configuración y dependencias**
- Cada subproyecto incluye su `config/config.yaml` y un fichero de entorno `environment.yml` o `requirements.txt` para recrear dependencias.
- No incluir credenciales ni datos sensibles en los ficheros de código; usar `config/config.yaml` para parámetros variables.

**Notas y recomendaciones**
- Los logs y salidas se guardan en los directorios `output/` de cada subproyecto.
- Recomendado usar un entorno virtual (Conda o venv) y recrear el entorno con `environment.yml` o `pip install -r requirements.txt` según corresponda.
