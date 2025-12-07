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
# Reconocimiento Visual (Aquatone / Gowitness)

Captura screenshots de subdominios vivos y genera un reporte HTML para revisar visualmente.

## Qué hace
- `run_aquatone.sh`: ejecuta Aquatone con parámetros seguros.
- `run_gowitness.sh`: alternativa con Gowitness.

## Prerrequisitos
- Tener una lista de subdominios vivos (por ejemplo, desde `../subdomain_discovery/output/*_live.txt`).
- Chrome/Chromium instalado (o usar ruta con `-chrome-path`).

## Uso rápido
```bash
# Aquatone con lista
./run_aquatone.sh subdominios_activos.txt aquatone_output

# Gowitness (si lo prefieres)
./run_gowitness.sh subdominios_activos.txt gowitness_output
```

Reporte en `aquatone_output/aquatone_report.html`. Screenshots en `screenshots/`.

## Consejos
- Si ves muchos fallos, baja `-threads` o sube timeouts.
- Algunos sitios no se capturan por WAF/SSL: es normal.

## Estructura mínima
```
visual_recon/
├── run_aquatone.sh
├── run_gowitness.sh
├── aquatone_report/
└── gowitness_screens/
```
# Screenshot de mayor resolución
