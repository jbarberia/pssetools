# PSS/E Tools CLI

Una herramienta de línea de comandos profesional para automatizar actividades en PSS/E (Power System Simulator for Engineering) utilizando Python.

## Características Principales

- **CLI Centralizada:** Acceso a todas las actividades a través de un único punto de entrada (`pssetools`).
- **DRY (Don't Repeat Yourself):** Inicialización de PSS/E y carga de casos abstraída mediante decoradores.
- **Auto-asignación Inteligente:** Capacidad de reconocer archivos por su extensión (`.sav`, `.dyr`, `.acc`, etc.) para simplificar los comandos.
- **Flujos de Trabajo Automatizados:** Soporte para análisis de contingencias (ACCC), cortocircuito (ASCC), simulaciones dinámicas y generación de snapshots.

---

## Instalación

Se recomienda instalar el paquete en modo editable para habilitar el comando `pssetools` directamente:

```bash
pip install -e .
```

Si no se desea instalar, se puede ejecutar mediante el módulo de Python:
```bash
python -m pssetools --help
```

---

## Uso de la CLI

### Sintaxis General
```bash
pssetools [actividad] [opciones] [archivos...]
```

### Comandos Disponibles

| Comando | Actividad |
| :--- | :--- |
| `acc` | Análisis de contingencias AC (ACCC). |
| `acc-pp` | Post-procesamiento de archivos `.acc` a reportes CSV/TSV. |
| `ascc` | Análisis de cortocircuito (ASCC). |
| `dfx` | Construcción de factores de distribución (DFAX). |
| `snp` | Generación de snapshots dinámicos (`.snp`). |
| `cnv` | Conversión de casos estáticos a dinámicos. |
| `dyn` | Ejecución de simulaciones dinámicas. |
| `dll` | Compilación de modelos de usuario (DLL). |
| `runner` | Ejecución de scripts de Python personalizados dentro del entorno PSS/E. |

---

## Ejemplo de Flujo de Trabajo (Carpeta `example`)

La carpeta `example` contiene un entorno de trabajo completo con scripts de automatización:

### 1. Análisis Estático (Flujos y Contingencias)
Genera factores de distribución, corre el análisis de contingencias y exporta resultados a tablas legibles:
```bash
cd example
./script.sh estatico
```

### 2. Preparación Dinámica (Snapshot y DLL)
Compila los modelos de usuario y genera el archivo de snapshot necesario para simulaciones:
```bash
./script.sh compila
```

### 3. Simulación Dinámica
Convierte el caso y corre las simulaciones definidas en los archivos `.py` (ej. `flat1.py`):
```bash
./script.sh dinamico
```

---

## Lógica de Auto-asignación

Para facilitar el uso, el CLI asigna automáticamente los archivos pasados como argumentos posicionales según su extensión:

**Comando explícito:**
```bash
pssetools acc --sav sistema.sav --dfx estudio.dfx --acc salida.acc
```

**Comando simplificado (Equivalente):**
```bash
pssetools acc sistema.sav estudio.dfx salida.acc
```

---

## Configuración

El comportamiento de los comandos se puede ajustar mediante el archivo `pssetools/config.cfg`. Se puede pasar un archivo de configuración personalizado con el flag `--config`:

```bash
pssetools acc sistema.sav --config mi_configuracion.cfg
```

---

## Requisitos

- PSS/E 34 (instalado en la ruta por defecto).
- Python compatible con la versión de PSS/E (usualmente 2.7 o 3.x).
- Dependencias: `pandas` (para post-procesamiento), `arrbox` (dependencia externa de PSS/E).
