# PSS/E Tools - Setup Wizard: Guía de Uso

## ¿Qué cambió?

El comando `pssetools setup` ahora es un **wizard interactivo** que te permite personalizar exactamente qué archivos necesitas para tu proyecto. Ya no copia todo automáticamente.

## Cómo usar

### Inicio básico
```bash
pssetools setup
```

Esto te mostrará un menú interactivo:

```
============================================================
            PSS/E Tools - Workspace Setup Wizard            
============================================================

This wizard will create a standard pssetools workspace structure
and copy templates based on your analysis needs.

[*] Creating workspace structure...
[OK] Created folder: lib
[OK] Created folder: log
[OK] Created folder: build
[OK] Created folder: results

[*] Copying essential configuration files...
[OK] Copied: config.cfg
[OK] Copied: estudio.sub
[OK] Copied: estudio.mon
[OK] Copied: estudio.con
[OK] Copied: estudio.idv

What types of studies will you run?
Select your primary analysis type:
  [1] ACCC (Contingency Analysis)
  [2] ASCC (Short Circuit Analysis)
  [3] Dynamic Simulation
  [4] All of the above
  [5] Just essentials (decide later)

Your choice [1/2/3/4/5]: 
```

## Opciones del Wizard

### 1️⃣ **Contingency Analysis (ACCC)**
- Para estudios de flujos óptimos y análisis de contingencias
- Copia: `config.cfg`, `estudio.sub`, `estudio.mon`, `estudio.con`
- Típicamente: Sin scripts dinámicos

### 2️⃣ **Short Circuit (ASCC)**
- Para cálculos de cortocircuito
- Copia: `config.cfg`, `estudio.sub`, `estudio.idv`
- Típicamente: Sin ejemplos de simulación

### 3️⃣ **Dynamic Simulation**
- Para simulaciones transitorias
- Copia: Esenciales + te pregunta por ejemplos de scripts
- Recomendado: Incluir `convload.py`, `dyn_1ph.py`, `dyn_3ph.py`

### 4️⃣ **All of the above**
- Estudio completo del sistema
- Copia: Todo lo esencial + opcionales si lo quieres
- Te pregunta por: Scripts, ejemplos de simulación, documentación

### 5️⃣ **Just essentials**
- Configuración mínima para empezar
- Copia solo: Archivos de configuración necesarios
- Puedes copiar más archivos manualmente después

## Preguntas Adicionales

### ¿Incluir scripts de ejemplo?
```
Include example dynamic simulation scripts (dyn_1ph.py, dyn_3ph.py, convload.py)? [y/n]:
```
- **y**: Copia archivos Python de ejemplo para simulaciones transitorias
- **n**: No los copia (puedes copiarlos después manualmente)

### ¿Incluir scripts de automatización?
```
Include automation scripts (script.sh for Linux/Mac, script.ps1 for Windows)? [y/n]:
```
- **y**: Copia `script.sh` (bash) y `script.ps1` (PowerShell) para ejecución batch
- **n**: Solo usarás los comandos `pssetools` directamente

### ¿Incluir documentación?
```
Include PSS/E API reference documentation files? [y/n]:
```
- **y**: Copia directorio `docs/` con referencias de PSS/E API
- **n**: No la copia (puedes descargarla después si la necesitas)

## Estructura Generada

Después de ejecutar el wizard, tendrás:

```
my_project/
├── lib/                    # Librerías compiladas
├── log/                    # Logs de ejecución
├── build/                  # Archivos temporales
├── results/                # Resultados finales
├── config.cfg              # [SIEMPRE] Configuración principal
├── estudio.sub             # [SIEMPRE] Definición de subsistema
├── estudio.mon             # [SIEMPRE] Puntos monitoreados
├── estudio.con             # [SIEMPRE] Contingencias
├── estudio.idv             # [SIEMPRE] Canales
├── convload.py             # [OPCIONAL] Script de conversión
├── dyn_1ph.py              # [OPCIONAL] Falta 1F
├── dyn_3ph.py              # [OPCIONAL] Falta 3F
├── script.sh               # [OPCIONAL] Bash automation
├── script.ps1              # [OPCIONAL] PowerShell automation
├── GEMINI.md               # [OPCIONAL] Guía del workspace
└── docs/                   # [OPCIONAL] Documentación PSS/E API
```

## Ejemplos de Uso

### Scenario 1: Solo ACCC
```bash
$ pssetools setup
Choice: 1
Scripts: n
Examples: n
Docs: n
```

Result: Archivos mínimos para ACCC. Total: ~7 archivos.

### Scenario 2: Dynamic Simulation Completo
```bash
$ pssetools setup
Choice: 3
Examples: y
Scripts: y
Docs: n
```

Result: Configuración + ejemplos Python + scripts. Total: ~13 archivos.

### Scenario 3: Estudio Completo
```bash
$ pssetools setup
Choice: 4
Examples: y
Scripts: y
Docs: y
```

Result: Todos los archivos. Total: ~20+ archivos.

## Carpeta `template/` - Nueva Organización

### `essential/`
Archivos que **siempre** se copian:
- `config.cfg` - Configuración central
- `estudio.sub/mon/con/idv` - Definiciones de estudio PSS/E

### `optional/examples/`
Scripts Python de ejemplo (solo si seleccionas "y"):
- `convload.py` - Conversión de casos
- `dyn_1ph.py` - Falta monofásica ejemplo
- `dyn_3ph.py` - Falta trifásica ejemplo

### `optional/scripts/`
Scripts de automatización (solo si seleccionas "y"):
- `script.sh` - Automatización bash/shell
- `script.ps1` - Automatización PowerShell

### `docs/`
Documentación de referencia (solo si seleccionas "y"):
- `psspy.txt`, `pssarrays.txt`, `dyntools.txt`, etc.

### `optional/` 
Otros:
- `GEMINI.md` - Mandatos del workspace

## Archivos que NO se Copian

- `README.md` (este) - Solo en la carpeta template
- Archivos `.pyc` o caché de Python
- Archivos de desarrollo del `pssetools` package

## Después del Setup

1. **Edita los archivos**:
   - `config.cfg` - Ajusta parámetros ACCC/ASCC
   - `estudio.sub/mon/con/idv` - Define tu estudio
   - Scripts Python - Personaliza los ejemplos

2. **Copia tus casos PSS/E**:
   - `*.sav` - Casos de flujo de potencia
   - `*.dyr` - Datos dinámicos

3. **Ejecuta análisis**:
   ```bash
   pssetools acc CASE.sav --acc results.acc
   pssetools dyn --cnv CASE.cnv --snp snapshot.snp --out results.out
   ```

## Referencia Rápida

| Opción | Para qué | Archivos |
|--------|----------|----------|
| 1 (ACCC) | Análisis de contingencias | config.cfg, estudio.* |
| 2 (ASCC) | Cortocircuito | config.cfg, estudio.sub |
| 3 (Dynamic) | Simulaciones transitorias | Esenciales + ejemplos Python |
| 4 (All) | Estudio completo | Todo personalizable |
| 5 (Essentials) | Solo configuración | Archivos mínimos |

---

## ¿Cómo restaurar archivos?

Si necesitas más archivos después del setup inicial:

1. **Copiar manualmente**:
   ```bash
   # Desde el directorio template del package
   cp $(python -c "import pssetools; print(pssetools.__path__[0])")/template/optional/examples/*.py .
   ```

2. **O ejecutar setup nuevamente** (preguntará qué sobrescribir):
   ```bash
   pssetools setup
   ```

---

**Creado con:** `pssetools` - Power Systems Engineering Automation Tool  
**Versión:** 0.2.1+  
**Python:** 2.7+ (PSS/E 34 compatible)
