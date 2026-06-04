# pssetools

**pssetools** es una utilidad de línea de comandos (CLI) y GUI para automatizar actividades de PSS/E (v34/v36), incluyendo ACCC, ASCC, simulaciones dinámicas y compilación de DLLs de modelos de usuario. Simplifica los flujos de trabajo complejos de PSS/E proporcionando una interfaz moderna y asignación automática de archivos.

## Características
- **Análisis de Contingencias ACCC:** Ejecuta y procesa resultados de contingencias.
- **Cortocircuito ASCC:** Automatiza reportes de cortocircuito para varios tipos de fallas (3PH, LG, LL, LLG).
- **Simulación Dinámica:** Gestiona snapshots (.snp), casos convertidos (.cnv) y ejecuciones en el dominio del tiempo con scripts de eventos personalizados.
- **Post-procesamiento Dinámico:** Convierte archivos de salida (.out) a CSV de canales.
- **DLLs de Usuario:** Compila modelos de usuario utilizando las herramientas del entorno PSSE (Intel oneAPI, MSVC).
- **Asignación Automática:** Detecta y asigna automáticamente archivos de entrada basados en sus extensiones (.sav, .dyr, .sub, etc.).
- **Asistente de Configuración (GUI):** Genera archivos de subsistema (.sub), monitoreo (.mon), contingencias (.con) y canales (.idv) directamente desde diagramas SLD de PSS/E.
- **Configuración del Espacio de Trabajo:** Inicializa una estructura de proyecto estándar con plantillas, un Makefile y organización de carpetas.

## Requisitos Previos
- **Python:** 32-bit para PSS/E 34 o 64-bit para PSS/E 36.
- **PSS/E:** Versión 34 (32-bit) o 36 (64-bit) instalado y en el PATH del sistema.
- **Dependencias:** `pandas`, `Tkinter` (incluido en Python 2.7 estándar).

## Instalación

### Para Usuarios
Instala el paquete directamente desde el repositorio:
```bash
git clone https://github.com/User/pssetools.git
cd pssetools
make install
```

## Inicio Rápido (CLI)

### 1. Inicializar Espacio de Trabajo
Crea la estructura de carpetas estándar (`build/`, `log/`, `results/`) y copia las plantillas:
```bash
pssetools setup
```

### 2. Análisis ACCC
Ejecuta ACCC y procesa los resultados en reportes:
```bash
# Ejecutar ACCC
pssetools acc case.sav estudio.sub estudio.mon estudio.con --acc results.acc

# Post-procesar a reportes CSV
pssetools acc-pp results.acc --frp flow_report.csv --vrp volt_report.csv
```

### 3. Cortocircuito
```bash
pssetools ascc --sav case.sav --sub estudio.sub --report fault_study.scf
```

### 4. Simulación Dinámica
Construye un snapshot y ejecuta una simulación con un script de eventos personalizado:
```bash
# Crear Snapshot
pssetools snp --sav case.sav --dyr data.dyr --snp snapshot.snp

# Ejecutar simulación
pssetools dyn --cnv case.cnv --snp snapshot.snp --out results.out --py event.py

# Post-procesar canales a CSV
pssetools dyn-pp results.out --ofile channels.csv
```

### 5. Automatización (Makefile)
El espacio de trabajo inicializado con `pssetools setup` incluye un `Makefile` para ejecutar todos los estudios en modo lote:
```bash
make estatico       # Todos los análisis de contingencias
make cortocircuito  # Todos los reportes de cortocircuito
make dinamico       # Todas las corridas de estabilidad transitoria
```

## Asistente de Configuración GUI
La GUI te permite seleccionar elementos en un diagrama SLD (Slider) de PSS/E y generar automáticamente los archivos de configuración necesarios.

**Para lanzar la GUI:**
```bash
pssetools gui
```
- **Pestañas:** Gestiona `.sub`, `.mon`, `.con` y `.idv` (canales) por separado.
- **Atajos:**
  - `Ctrl+S`: Guardar pestaña actual.
  - `Ctrl+Shift+S`: Guardar todas las pestañas con un nombre base.
  - `Ctrl+Tab`: Cambiar de pestaña.
  - `Alt+1`: Generar contenido a partir de los elementos seleccionados en el SLD.

## Configuración
Las actividades se controlan a través de `config.cfg`. Puedes especificar un archivo de configuración personalizado usando la bandera `--config` para sobrescribir los valores por defecto.

```bash
pssetools acc case.sav --config custom_settings.cfg
```

## Documentación
- [Guía de Configuración](docs/CONFIG_GUIDE.md) - Cómo personalizar las actividades de PSS/E mediante archivos .cfg
- [Referencia de API (Interna)](docs/docs/GEMINI.md) - Guía para LLMs y flujos de trabajo automatizados
- [Contribución](CONTRIBUTING.md)
