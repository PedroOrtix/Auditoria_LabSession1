# Subdomain Discovery

Descubre subdominios con `subfinder`, verifica cuáles están vivos (DNS + HTTP/HTTPS) y genera informes en `output/`.

## Qué hace
- `discover`: usa subfinder para enumerar subdominios.
- `verify`: resuelve DNS y comprueba accesibilidad.
- `analyze`: encadena todo y produce métricas e informes.

## Prerrequisitos
- `subfinder` instalado y en `PATH`.
- Entorno Python (Conda recomendado).

## Instalación rápida
```bash
conda env create -f config/environment.yml
conda activate subdomain_discovery
# Alternativa
pip install -r config/requirements.txt
```

## Uso
```bash
# Descubrir
python main.py discover upm.es -o subdomains.txt

# Verificar
python main.py verify -i subdomains.txt

# Flujo completo
python main.py analyze upm.es
```
Resultados en `output/` (`*_raw.txt`, `*_live.txt`, `*_results.json`, `*_report.txt`).

## Estructura mínima
```
subdomain_discovery/
├── config/ (config.yaml, requirements.txt, environment.yml)
├── src/ (subdomain_verifier.py, asset_analyzer.py, logger.py)
├── output/
└── main.py
```

## 📋 Prerrequisitos

### 1. Go y subfinder

Instala Go si no está instalado:
```bash
# En Ubuntu/Debian
sudo apt install golang-go

# En macOS
brew install go
```

Instala subfinder:
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Asegúrate de que $GOPATH/bin esté en tu PATH
export PATH=$PATH:$(go env GOPATH)/bin

# Verificar instalación
subfinder -version
```

Explora subfinder:
```bash
# Listar fuentes disponibles
subfinder -ls

# Ver ayuda
subfinder -h
```

### 2. Entorno Python (Recomendado: Anaconda)

Crea y activa el entorno con conda:
```bash
cd subdomain_discovery
conda env create -f config/environment.yml
conda activate subdomain_discovery
```

O instala dependencias con pip:
```bash
pip install -r config/requirements.txt
```

## 🚀 Uso

### Análisis completo (Recomendado)

Descubre, verifica y analiza en un solo comando:
```bash
python main.py analyze www.upm.es
```

O bien usa el script wrapper:
```bash
./run.sh analyze www.upm.es
```

Esto realizará:
1. Ejecutar `subfinder` para descubrir subdominios
2. Verificar cada subdominio (DNS + HTTP/HTTPS)
3. Analizar y categorizar resultados
4. Identificar objetivos de alto valor
5. Calcular métricas de eficiencia
6. Generar un informe completo

### Solo Descubrimiento

Descubrir subdominios sin verificación:
```bash
python main.py discover www.upm.es -o subdomains.txt
```

### Solo Verificación

Verificar subdominios desde un fichero:
```bash
python main.py verify -i subdomains.txt
```

Encadenar la salida de subfinder directamente:
```bash
subfinder -d www.upm.es | python main.py verify
```

## 📊 Archivos de salida

Todos los resultados se guardan en el directorio `output/` con marcas de tiempo:

- `{domain}_{timestamp}_raw.txt` - Todos los subdominios descubiertos
- `{domain}_{timestamp}_live.txt` - Solo subdominios vivos y accesibles
- `{domain}_{timestamp}_results.json` - Resultados detallados en JSON
- `{domain}_{timestamp}_report.txt` - Informe en formato legible

## 🎯 Qué analiza la herramienta

### 1. Métricas de eficiencia
- **Candidatos totales**: Todos los subdominios descubiertos por subfinder
- **DNS resueltos**: Subdominios que resuelven vía DNS
- **Assets vivos**: Subdominios accesibles por HTTP/HTTPS
- **Relación señal/ruido**: Porcentaje de assets vivos sobre candidatos totales
- **Ruido filtrado**: Dominios muertos descartados

### 2. Análisis de códigos de estado
- **200 OK**: Servidores plenamente activos
- **403 Forbidden**: Acceso restringido (⚠️ INTERÉS ALTO - suele indicar assets internos)
- **401 Unauthorized**: Requiere autenticación
- **3xx Redirects**: Redirecciones
- **Otros**: Respuestas diversas

### 3. Identificación de objetivos de alto valor

Se priorizan subdominios que contienen keywords como:
- `vpn`, `citrix` - Portales de acceso remoto
- `portal`, `employee`, `staff` - Portales de empleados/admin
- `admin`, `management` - Interfaces administrativas
- `intranet`, `internal` - Sistemas internos

**Criterios de puntuación**:
- Keywords: +10 puntos por keyword
- 403 Forbidden: +20 puntos (asset interno restringido)
- 401 Unauthorized: +15 puntos
- 200 OK: +10 puntos

### 4. Por qué 403 Forbidden es de interés

Un 403 indica frecuentemente:
- Asset expuesto pero restringido
- Controles de acceso mal configurados
- Potencial punto de entrada para pruebas adicionales
- Asset que no debería ser público

## ⚙️ Configuración

Edita `config/config.yaml` para personalizar:

```yaml
# Timeouts
http_timeout: 3  # segundos
dns_timeout: 2   # segundos

# Keywords de alto valor
high_value_keywords:
  - "vpn"
  - "citrix"
  - "portal"
  - "employee"
  # Añadir más...

# Códigos de estado interesantes
interesting_status_codes:
  - 200
  - 403
  - 401
  # Añadir más...
```

## 🔍 Flujo de ejemplo

```bash
# 1. Descubrir subdominios
python main.py discover www.upm.es -o upm_subdomains.txt

# 2. Revisar la lista
head upm_subdomains.txt

# 3. Verificar cuáles están vivos
python main.py verify -i upm_subdomains.txt

# 4. O hacer todo en un solo paso
python main.py analyze www.upm.es
```

## 📈 Ejemplo de informe

```
================================================================================
INFORME DE DESCUBRIMIENTO Y ANÁLISIS DE SUBDOMINIOS
================================================================================

1. MÉTRICAS DE EFICIENCIA EN RECONNAISSANCE
--------------------------------------------------------------------------------
Total candidatos (salida de subfinder): 150
DNS resueltos: 45 (30.00%)
Assets vivos (hosts validados): 12 (8.00%)
Ruido filtrado: 138 (92.00%)

Relación señal/ruido: 8.00%
Eficiencia de descubrimiento: 12/150 assets vivos encontrados

2. DISTRIBUCIÓN DE CÓDIGOS HTTP
--------------------------------------------------------------------------------
HTTP 200: 8 assets
HTTP 403: 3 assets
HTTP 401: 1 asset

3. CATEGORIZACIÓN DE ASSETS
--------------------------------------------------------------------------------
Fully Active (200 OK): 8 assets
Restricted Access (403 Forbidden): 3 assets ⚠️ INTERÉS ALTO
Authentication Required (401): 1 asset
...

4. OBJETIVOS DE ALTO VALOR (Priorizados)
--------------------------------------------------------------------------------
1. vpn.example.upm.es [Puntuación: 30]
   Estado: HTTP 403 (HTTPS)
   Keywords: vpn
   Razones: Keyword: vpn, 403 Forbidden - Acceso restringido
...
```

## 🛡️ Consideraciones de seguridad

- **Siempre obtener autorización** antes de escanear dominios
- Respetar `robots.txt` y políticas del sitio
- Usar timeouts razonables para evitar sobrecargar servidores
- Registrar todas las actividades para auditoría
- Solo realizar reconocimiento pasivo y semi-pasivo salvo autorización

## 🔧 Solución de problemas

### subfinder no encontrado
```bash
# Asegúrate de que Go bin esté en PATH
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.zshrc
source ~/.zshrc
```

### Permiso denegado en run.sh
```bash
chmod +x run.sh
```

### ImportError
```bash
# Asegúrate de estar en el entorno correcto
conda activate subdomain_discovery
# O reinstala dependencias
pip install -r config/requirements.txt
```

## 📝 Logging

Todas las actividades se registran en `subdomain_discovery.log` con marcas de tiempo. Consulta este fichero para:
- Información detallada de ejecución
- Errores y advertencias
- Resultados individuales de verificación

## 🎓 Valor educativo

Este proyecto demuestra:
- Uso real de Certificate Transparency logs para reconocimiento
- Técnicas de filtrado de ruido
- Estrategias de priorización de assets
- Uso eficiente de herramientas pasivas
- Buenas prácticas en Python (logging, configuración, diseño modular)

## 📚 Referencias

- [subfinder](https://github.com/projectdiscovery/subfinder) - Herramienta de enumeración pasiva rápida
- Certificate Transparency Logs
- OWASP Testing Guide - Information Gathering

## 📄 Licencia

Proyecto educativo para la asignatura de auditoría de seguridad.

---

**Nota**: Esta herramienta está diseñada con fines educativos y para pruebas de seguridad autorizadas únicamente. Obtén autorización antes de escanear cualquier dominio.

````
