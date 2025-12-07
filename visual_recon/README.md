# Aquatone - Reconocimiento Visual

Aquatone es una herramienta que captura screenshots de sitios web y los agrupa automáticamente por similitud, permitiendo identificar rápidamente páginas diferentes o interesantes.

## 🔧 Solución de problemas

### Error "exit status 21" (Captura fallida)

Este es el error más común. Ocurre cuando Chrome/Chromium no puede renderizar la página por:
- Problemas SSL/TLS
- Páginas con protección anti-scraping
- Timeouts internos del navegador
- Falta de fuentes o dependencias

**Soluciones:**

```bash
# 1. Instalar Chromium (más confiable que Google Chrome)
sudo dnf install chromium

# 2. Usar el script optimizado run_aquatone.sh
./run_aquatone.sh iberiaexpress_live.txt

# 3. Aumentar timeouts
cat subdomains.txt | aquatone -screenshot-timeout 15000 -http-timeout 10000 -out ./output

# 4. Reducir threads (menos presión al navegador)
cat subdomains.txt | aquatone -threads 1 -out ./output

# 5. Probar con Google Chrome en lugar de Chromium
cat subdomains.txt | aquatone -chrome-path /usr/bin/google-chrome -out ./output
```

**Nota importante:** Algunos sitios web NUNCA se capturarán correctamente debido a:
- Protección anti-bot avanzada
- Certificados SSL inválidos/autofirmados
- JavaScript que previene capturas
- **Esto es NORMAL** - Aquatone captura ~50-70% exitosamente

### Chrome no encontrado

```bash
# Error: "Failed to find Chrome"
# Solución: Instalar Chrome o especificar ruta
aquatone -chrome-path /usr/bin/google-chrome
```

# Con directorio personalizado
./run_aquatone.sh iberiaexpress_live.txt custom_output
```

### Comando Genérico Manual

```bash
cat <archivo_subdominios.txt> | aquatone -out <directorio_output>
```

### Ejemplo con Iberia Express

```bash
# Método manual (puede tener más fallos)
cat iberiaexpress_live.txt | aquatone -out ./aquatone_iberiaexpress

# Método optimizado (recomendado)
./run_aquatone.sh iberiaexpress_live.txt aquatone_iberiaexpress
```

### Ejemplo con cualquier dominio

```bash
# Desde el output del subdomain_discovery
cat ../subdomain_discovery/output/upm.es_*_live.txt | aquatone -out ./aquatone_upm

# O copiar primero y usar el script
cp ../subdomain_discovery/output/upm.es_*_live.txt upm_live.txt
./run_aquatone.sh upm_live.txt aquatone_upm
```

## 📊 Parámetros Útiles

### Opciones Básicas

```bash
# Especificar puertos adicionales
cat subdomains.txt | aquatone -ports 80,443,8080,8443 -out ./output

# Aumentar número de threads (más rápido)
cat subdomains.txt | aquatone -threads 10 -out ./output

# Capturar solo HTTPS
cat subdomains.txt | aquatone -scan-timeout 300 -http-timeout 5000 -out ./output
```

### Opciones Avanzadas

```bash
# Screenshot de mayor resolución
cat subdomains.txt | aquatone -screenshot-timeout 30000 -resolution 1920,1080 -out ./output

# Con proxy
cat subdomains.txt | aquatone -proxy http://localhost:8080 -out ./output

# Silent mode (menos verbose)
cat subdomains.txt | aquatone -silent -out ./output
```

## 📁 Estructura de Output

Después de ejecutar Aquatone, encontrarás:

```
aquatone_output/
├── aquatone_report.html    # ⭐ ABRIR ESTE ARCHIVO EN NAVEGADOR
├── aquatone_session.json   # Datos de la sesión
├── aquatone_urls.txt       # URLs descubiertas
├── headers/                # Respuestas HTTP capturadas
│   ├── http__blog.example.com__80.txt
│   └── https__www.example.com__443.txt
└── screenshots/            # Screenshots capturados
    ├── http__blog.example.com__80.png
    └── https__www.example.com__443.png
```

## 🔍 Análisis del Reporte

### 1. Abrir el Reporte

```bash
# En el navegador
firefox aquatone_output/aquatone_report.html
# o
google-chrome aquatone_output/aquatone_report.html
```

### 2. Qué Buscar

**✅ Páginas que se ven diferentes:**
- Login forms (pueden ser puntos de entrada)
- Páginas de error personalizadas
- Paneles de administración
- Interfaces de desarrollo/staging

**❌ Páginas repetitivas (para ignorar):**
- 50 páginas idénticas de "Default IIS"
- Páginas de error genéricas 404
- Redirecciones a la misma página principal

### 3. Tips de Análisis

1. **Scroll rápido** - El ojo humano es excelente detectando lo diferente
2. **Filtrar por código HTTP** - Enfócate en 200, 403, 401
3. **Agrupar similares** - Aquatone lo hace automáticamente
4. **Buscar keywords** - admin, login, dev, staging, api

## 🎯 Flujo completo: Descubrimiento de subdominios → Aquatone

### Paso 1: Descubrir y Verificar Subdominios

```bash
# Desde el directorio subdomain_discovery
cd ../subdomain_discovery
python main.py analyze iberiaexpress.com
```

### Paso 2: Copiar Lista de Vivos

```bash
# Volver a visual_recon
cd ../visual_recon

# Copiar subdominios vivos
cp ../subdomain_discovery/output/iberiaexpress.com_*_live.txt subdominios_vivos.txt
```

### Paso 3: Ejecutar Aquatone

```bash
# Capturar screenshots
cat subdominios_vivos.txt | aquatone -out ./aquatone_report
```

### Paso 4: Analizar Resultados

```bash
# Abrir reporte HTML
firefox aquatone_report/aquatone_report.html
```

## 📝 Ejemplos prácticos

### Ejemplo 1: Análisis Rápido

```bash
# Solo 8 subdominios de Iberia Express
cat iberiaexpress_live.txt | aquatone -out ./quick_scan
```

**Resultado esperado:**
- 8 screenshots capturados
- Agrupación automática de páginas similares
- Identificación visual de páginas únicas

### Ejemplo 2: Análisis Completo de UPM

```bash
# Si tienes muchos subdominios
cat ../subdomain_discovery/output/upm.es_*_live.txt | aquatone -threads 5 -out ./upm_visual
```

### Ejemplo 3: Pipeline Completo

```bash
# Descubrir, verificar y visualizar en un solo flujo
cd ../subdomain_discovery
python main.py analyze target.com

cd ../visual_recon
cat ../subdomain_discovery/output/target.com_*_live.txt | aquatone -out ./target_recon
firefox target_recon/aquatone_report.html
```

## 🔧 Troubleshooting

### Error "exit status 21" (Screenshot Failed)

Este es el error más común. Ocurre cuando Chrome/Chromium no puede renderizar la página por:
- Problemas SSL/TLS
- Páginas con protección anti-scraping
- Timeouts internos del navegador
- Falta de fuentes o dependencias

**Soluciones:**

```bash
# 1. Instalar Chromium (más confiable que Google Chrome)
sudo dnf install chromium

# 2. Usar el script optimizado run_aquatone.sh
./run_aquatone.sh iberiaexpress_live.txt

# 3. Aumentar timeouts
cat subdomains.txt | aquatone -screenshot-timeout 15000 -http-timeout 10000 -out ./output

# 4. Reducir threads (menos presión al navegador)
cat subdomains.txt | aquatone -threads 1 -out ./output

# 5. Probar con Google Chrome en lugar de Chromium
cat subdomains.txt | aquatone -chrome-path /usr/bin/google-chrome -out ./output
```

**Nota importante:** Algunos sitios web NUNCA se capturarán correctamente debido a:
- Protección anti-bot avanzada
- Certificados SSL inválidos/autofi rmados
- JavaScript que previene capturas
- **Esto es NORMAL** - Aquatone captura ~50-70% exitosamente

### Chrome no encontrado

```bash
# Error: "Failed to find Chrome"
# Solución: Instalar Chrome o especificar ruta
aquatone -chrome-path /usr/bin/google-chrome
```

### Timeouts frecuentes

```bash
# Aumentar timeouts
cat subdomains.txt | aquatone -scan-timeout 500 -http-timeout 10000 -out ./output
```

### Muy lento

```bash
# Reducir threads si hay muchos errores
cat subdomains.txt | aquatone -threads 2 -out ./output

# O aumentar threads si la red es estable
cat subdomains.txt | aquatone -threads 10 -out ./output
```

### Solo algunos screenshots funcionan

**Esto es ESPERADO**. Resultados típicos:
- ✅ Screenshots exitosos: 40-70%
- ❌ Screenshots fallidos: 30-60%

**¿Por qué?**
- Sitios con WAF (Web Application Firewall)
- Certificados SSL problemáticos
- JavaScript complejo
- Protección anti-scraping

**Estrategia:**
1. Ejecuta Aquatone normalmente
2. Revisa los screenshots que SÍ funcionaron
3. Para los fallidos, visita manualmente con navegador

## 💡 Tips Profesionales

### 1. Filtrar por Status Code

```bash
# Solo mostrar 200 OK
cat all_subdomains.txt | aquatone -out ./output
# Luego filtrar en el reporte HTML por código 200
```

### 2. Combinación con otras herramientas

```bash
# Con subfinder directo
subfinder -d example.com -silent | aquatone -out ./recon

# Con httpx (verificar primero)
cat subdomains.txt | httpx -silent | aquatone -out ./recon
```

### 3. Análisis Iterativo

```bash
# Primera pasada rápida
cat subdomains.txt | aquatone -threads 10 -scan-timeout 100 -out ./quick

# Segunda pasada detallada (solo interesantes)
cat interesting_only.txt | aquatone -screenshot-timeout 30000 -out ./detailed
```

## 📚 Casos de Uso Real

### Bug Bounty

```bash
# 1. Descubrir subdominios
subfinder -d hackerone.com -silent > subs.txt

# 2. Verificar vivos
cat subs.txt | httpx -silent > live.txt

# 3. Screenshot visual
cat live.txt | aquatone -out ./h1_recon

# 4. Buscar manualmente en el reporte páginas interesantes
```

### Auditoría de Seguridad

```bash
# Identificar assets expuestos no documentados
python ../subdomain_discovery/main.py analyze company.com
cat output/company.com_*_live.txt | aquatone -out ./audit_visual

# Revisar en el reporte:
# - Paneles de admin expuestos
# - Entornos dev/staging públicos
# - Información sensible visible
```

## 🎨 Interpretación del Reporte HTML

### Elementos Clave

1. **Similarity Clusters** - Grupos de páginas similares
2. **Screenshots** - Capturas visuales de cada sitio
3. **Headers** - Respuestas HTTP capturadas
4. **Technology Stack** - Tecnologías detectadas

### Qué Priorizar

- 🔴 **Alta Prioridad**: Páginas únicas con forms de login
- 🟡 **Media Prioridad**: Páginas con 403/401
- 🟢 **Baja Prioridad**: Páginas agrupadas similares

---

## Comando Rápido para Copiar

```bash
cat iberiaexpress_live.txt | aquatone -out ./aquatone_iberiaexpress
```

Luego abre: `aquatone_iberiaexpress/aquatone_report.html` en tu navegador
