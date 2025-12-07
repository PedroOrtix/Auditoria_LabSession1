# Subdomain Checker

Herramienta automatizada para descubrir y verificar subdominios activos utilizando Certificate Transparency logs (crt.sh).

## 🎯 Características

- 🔍 **Descubrimiento de subdominios** mediante crt.sh (Certificate Transparency logs)
- ✅ **Verificación automática** de subdominios activos (HTTP 200)
- ⚡ **Verificación concurrente** para mayor velocidad
- 📝 **Logging detallado** de todas las operaciones
- ⚙️ **Configuración externa** mediante YAML
- 🎯 **CLI flexible** con múltiples opciones
- 🚀 **API JSON** para búsquedas eficientes
- 🔄 **Fallback HTML scraping** cuando la API no está disponible

## 📁 Estructura del Proyecto

```
subdomain_checker/
├── src/                        # Código fuente Python
│   ├── __init__.py             # Paquete Python
│   ├── crtsh_scraper.py        # Módulo de scraping de crt.sh
│   ├── subdomain_verifier.py   # Módulo de verificación HTTP
│   └── logger.py               # Configuración de logging
├── config/                     # Archivos de configuración
│   ├── config.yaml             # Configuración principal ⚙️
│   ├── environment.yml         # Entorno Anaconda
│   └── requirements.txt        # Dependencias pip
├── main.py                     # Script principal y CLI ⭐
├── run.sh                      # Script wrapper interactivo 🎨
├── test_quick.py               # Script de prueba rápida
├── README.md                   # Este archivo
└── EJEMPLOS.md                 # Ejemplos detallados de uso 📖
```

## 🚀 Instalación

### Opción 1: Usando Anaconda (Recomendado)

```bash
# Crear el entorno desde environment.yml
conda env create -f config/environment.yml

# Activar el entorno
conda activate subdomain_checker
```

### Opción 2: Usando pip

```bash
# Crear entorno virtual (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac

# Instalar dependencias
pip install -r config/requirements.txt
```

## ⚙️ Configuración

Edita el archivo `config/config.yaml` para personalizar el comportamiento:

```yaml
# Query de búsqueda para crt.sh
# Ejemplos:
#   - "%.upm.es" -> Busca TODOS los subdominios (puede tardar o fallar)
#   - "moodle.upm.es" -> Busca solo ese subdominio específico
#   - "%.fi.upm.es" -> Busca subdominios de fi.upm.es
search_query: "moodle.upm.es"

# Usar API JSON (más rápido) o scraping HTML
use_json_api: true

# Timeouts
request_timeout: 30
verification_timeout: 3

# Protocolos a verificar
protocols:
  - "https"
  - "http"

# Número de workers concurrentes
max_workers: 20

# Archivo de salida
output_file: "subdominios_activos.txt"
```

## 💻 Uso

### 🎨 Método 1: Script Interactivo (Más Fácil)

```bash
bash run.sh
```

Obtendrás un menú interactivo:

```
╔════════════════════════════════════════════════════╗
║          SUBDOMAIN CHECKER - UPM                   ║
║    Descubrimiento y Verificación de Subdominios   ║
╚════════════════════════════════════════════════════╝

¿Qué deseas hacer?

  1) Buscar subdominios y verificar cuáles están activos
  2) Solo buscar subdominios (sin verificar)
  3) Buscar con consulta personalizada
  4) Ver ayuda completa
  5) Salir
```

### 🔧 Método 2: Línea de Comandos

#### Uso básico (con configuración por defecto)

```bash
python3 main.py
```

#### Especificar un dominio diferente

```bash
python3 main.py -q "%.fi.upm.es"
```

#### Solo descubrir subdominios (sin verificar)

```bash
python3 main.py -q "moodle.upm.es" --no-verify
```

#### Especificar archivo de salida

```bash
python3 main.py -q "%.fi.upm.es" -o resultados_fi.txt
```

#### Usar archivo de configuración personalizado

```bash
python3 main.py -c mi_config.yaml
```

#### Ver todas las opciones

```bash
python3 main.py --help
```

### 📚 Más Ejemplos

Consulta el archivo **[EJEMPLOS.md](EJEMPLOS.md)** para ver:
- Búsquedas avanzadas
- Uso con wildcards
- Automatización con cron
- Integración con otras herramientas
- Tips y trucos

## 📊 Ejemplos de Salida

### Búsqueda con Verificación

```bash
$ python3 main.py -q "%.fi.upm.es"
```

```
============================================================
Subdomain Checker - Iniciando...
============================================================
INFO - Query de búsqueda: %.fi.upm.es
INFO - Buscando subdominios para: %.fi.upm.es
INFO - Certificados encontrados: 156
INFO - Subdominios únicos extraídos: 78
INFO - Subdominios descubiertos: 78
INFO - Verificando 78 subdominios...
INFO - Total de verificaciones a realizar: 156
INFO - ✓ https://www.fi.upm.es - HTTP 200
INFO - ✓ https://moodle.fi.upm.es - HTTP 200
INFO - ✓ https://www.oeg.fi.upm.es - HTTP 200
...
INFO - Subdominios activos encontrados: 45
============================================================
RESULTADOS
============================================================
INFO - Total subdominios descubiertos: 78
INFO - Total subdominios activos (HTTP 200): 45

Subdominios activos:
  ✓ https://moodle.fi.upm.es
  ✓ https://www.fi.upm.es
  ✓ https://www.oeg.fi.upm.es
  ...

✓ Resultados guardados en: subdominios_activos.txt
```

### Solo Descubrimiento (sin verificar)

```bash
$ python3 main.py -q "moodle.upm.es" --no-verify
```

```
INFO - Subdominios descubiertos: 2
INFO - Verificación desactivada. Mostrando solo subdominios descubiertos:
  - moodle.upm.es
  - www.moodle.upm.es
```

## 📄 Archivos Generados

- **subdomain_checker.log**: Log detallado de todas las operaciones
- **subdominios_activos.txt**: Lista de subdominios activos (HTTP 200)

Ejemplo de `subdominios_activos.txt`:

```
# Subdominios Activos (HTTP 200)
# Total encontrados: 45

https://moodle.fi.upm.es
https://www.fi.upm.es
https://www.oeg.fi.upm.es
...
```

## 🔄 Funcionamiento

1. **Descubrimiento**: Consulta crt.sh usando Certificate Transparency logs
2. **Extracción**: Parsea la respuesta JSON (o HTML como fallback) para extraer subdominios
3. **Deduplicación**: Elimina duplicados y limpia wildcards (*.domain.com)
4. **Verificación**: Realiza peticiones HTTP/HTTPS concurrentes a cada subdominio
5. **Filtrado**: Identifica solo aquellos que responden con HTTP 200
6. **Reporte**: Genera log detallado y archivo con resultados

```
┌─────────────┐
│   crt.sh    │  Certificate Transparency Logs
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ API JSON    │  Extrae subdominios de certificados
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Dedup &     │  Limpia y deduplica
│ Clean       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Concurrent  │  Verifica HTTP 200 (multithreading)
│ Verify      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Results    │  Genera informe y archivos
└─────────────┘
```

## 🔍 Casos de Uso Comunes

### Para Auditoría de Seguridad

```bash
# Descubrir toda la superficie de ataque de una organización
python3 main.py -q "%.upm.es"

# Enfocarse en una facultad específica
python3 main.py -q "%.fi.upm.es"

# Verificar servicios críticos
python3 main.py -q "moodle.upm.es"
```

### Para Reconocimiento

```bash
# Descubrir subdominios sin hacer ruido (solo descubrimiento)
python3 main.py -q "%.target.com" --no-verify

# Guardar resultados con timestamp
python3 main.py -q "%.target.com" -o "scan_$(date +%Y%m%d).txt"
```

## ⚠️ Notas de Seguridad

- La herramienta desactiva la verificación SSL para testing
- Se recomienda usar solo en entornos controlados y con autorización
- Los logs pueden contener información sensible
- Respeta los términos de servicio de crt.sh y no abuses de la API
- Las búsquedas muy amplias (`%.domain.com`) pueden fallar o tardar mucho

## 🐛 Solución de Problemas

### Error: Timeout en crt.sh

**Problema**: La búsqueda `%.upm.es` es demasiado amplia.

**Solución**: Usa búsquedas más específicas:
```bash
python3 main.py -q "%.fi.upm.es"  # En vez de %.upm.es
```

### Error: ModuleNotFoundError

**Problema**: Faltan dependencias.

**Solución**:
```bash
pip install -r requirements.txt
```

### Pocos subdominios encontrados

**Problema**: Búsqueda demasiado específica.

**Solución**: Usa wildcards:
```bash
python3 main.py -q "%.moodle.upm.es"  # En vez de moodle.upm.es
```

## 📚 Recursos Adicionales

- **[EJEMPLOS.md](EJEMPLOS.md)**: Guía completa de ejemplos
- **Certificate Transparency**: https://crt.sh/
- **UPM**: https://www.upm.es/

## 👨‍💻 Autor

Proyecto creado para la asignatura de **Auditoría de Seguridad** - Master en Ciberseguridad

## 📝 Licencia

Uso educativo - Master Ciberseguridad UPM

---

## 🎓 Aprendizajes del Proyecto

Este proyecto demuestra:
- ✅ Uso de Certificate Transparency logs para reconocimiento
- ✅ Scraping web con BeautifulSoup
- ✅ Programación concurrente con ThreadPoolExecutor
- ✅ Logging estructurado y profesional
- ✅ Configuración externa con YAML
- ✅ Diseño modular y reutilizable
- ✅ Manejo de errores y timeouts
- ✅ CLI amigable con argparse
- ✅ Buenas prácticas de Python (PEP 8)

---

**¿Necesitas ayuda?** Consulta `EJEMPLOS.md` o ejecuta `python3 main.py --help`
