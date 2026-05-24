# Guía de Parametrización: Evitar Repetición en Configuraciones

## Problema

Cuando ejecutas el mismo análisis para múltiples casos, tienes dos opciones malas:

1. **Copiar y pegar** - Crear un archivo YAML por cada caso
   ```
   config_caso_01.yml
   config_caso_02.yml
   config_caso_03.yml
   ... (10+ archivos, cada uno con 90% del contenido igual)
   ```
   ❌ Difícil de mantener: cambiar el `sub` requiere editar 10 archivos

2. **Un archivo gigante** - Todas las simulaciones en un YAML de 500 líneas
   ```yaml
   simulations:
     - name: Case 1
       case: caso_01.sav
       options:
         sub: "studies/accc.sub"
         mon: "studies/accc.mon"
         ...
     - name: Case 2
       case: caso_02.sav
       options:
         sub: "studies/accc.sub"    # ← REPETIDO
         mon: "studies/accc.mon"    # ← REPETIDO
         ...
   ```
   ❌ Dificil de leer y mantener: cambios se pierden en la masa

## Solución: Dos Niveles de Parametrización

### Nivel 1: YAML Anchors (Recomendado - Simple)

**Cuándo usar**: Para 2-10 casos similares. Es nativo de YAML, sin herramientas adicionales.

**Cómo funciona**: Define bloques comunes una vez, reutiliza con `&` y `*`

#### Ejemplo Simple

```yaml
# Definir opciones comunes una sola vez
default_accc_options: &accc_options
  sub: "studies/accc.sub"
  mon: "studies/accc.mon"
  con: "studies/accc.con"

simulations:
  # Caso 1: Usar las opciones comunes
  - name: "ACCC_Caso_01"
    type: "accc"
    case: "casos/caso_01.sav"
    options:
      <<: *accc_options          # ← Hereda todas las opciones
      dfx: "build/caso_01.dfx"   # ← Específico de este caso

  # Caso 2: Mismas opciones, diferente caso
  - name: "ACCC_Caso_02"
    type: "accc"
    case: "casos/caso_02.sav"
    options:
      <<: *accc_options
      dfx: "build/caso_02.dfx"

  # ... más casos ...
```

**Ventajas:**
- ✅ Cambiar `sub` requiere editar una línea (la definición del anchor)
- ✅ No necesita herramientas externas
- ✅ Funciona con cualquier YAML parser
- ✅ Fácil de leer

**Desventajas:**
- ❌ Si tenés 50+ casos, el archivo sigue siendo largo
- ❌ No puedes generar desde una lista de variables

#### Ejemplo Avanzado: Múltiples Niveles

```yaml
# Nivel 1: Configuración global
workspace: &workspace
  base_dir: "."

# Nivel 2: Configuración por tipo de estudio
accc_base: &accc_base
  type: "accc"
  options: &accc_opts
    sub: "studies/accc.sub"
    mon: "studies/accc.mon"
    con: "studies/accc.con"

ascc_base: &ascc_base
  type: "ascc"
  options: &ascc_opts
    sub: "studies/ascc.sub"

# Nivel 3: Ejecución
execution: &exec
  continue_on_error: false
  logging: "normal"

# Nivel 4: Simulaciones específicas (heredan todo)
workspace: *workspace

simulations:
  - <<: *accc_base
    name: "ACCC_Caso_01"
    case: "casos/caso_01.sav"
    options:
      <<: *accc_opts
      dfx: "build/caso_01.dfx"

  - <<: *ascc_base
    name: "ASCC_Caso_01"
    case: "casos/caso_01.sav"
    options:
      <<: *ascc_opts
      report: "results/ascc_01.scf"

execution: *exec
```

**Beneficio**: Cambios cascada automáticamente
- Cambiar `type` del ACCC? Editar `*accc_base` una vez
- Cambiar workspace? Editar `*workspace` una vez

### Nivel 2: Config Generator (Avanzado - Automático)

**Cuándo usar**: Para 50+ casos o cuando necesitas actualizar fácilmente desde una lista

**Herramientas:**
- `generate_config.py` - Script que crea configs desde templates
- Variables en JSON - Lista de casos y parámetros

#### Flujo

```
accc_sweep.yml (template)
       +
variables.json (5 casos)
       |
       v
generate_config.py
       |
       v
config_Caso_01.yml
config_Caso_02.yml
config_Caso_03.yml
config_Caso_04.yml
config_Caso_05.yml
```

#### Ejemplo: Template

`accc_sweep.yml`:
```yaml
# {{VAR}} será reemplazado con valores de variables.json

workspace:
  base_dir: "."

simulations:
  - name: "ACCC_{{CASE_NAME}}"
    type: "accc"
    case: "casos/{{CASE_FILE}}"
    options:
      sub: "estudios/{{SUB_FILE}}"
      mon: "estudios/accc.mon"
      con: "estudios/accc.con"
      dfx: "build/{{CASE_NAME}}.dfx"

execution:
  continue_on_error: false
  logging: "normal"
```

#### Ejemplo: Variables

`variables.json`:
```json
{
  "cases": [
    {
      "CASE_NAME": "Caso_01_Base",
      "CASE_FILE": "caso_01.sav",
      "SUB_FILE": "accc_base.sub"
    },
    {
      "CASE_NAME": "Caso_02_Crecimiento",
      "CASE_FILE": "caso_02.sav",
      "SUB_FILE": "accc_growth.sub"
    },
    {
      "CASE_NAME": "Caso_03_Punta",
      "CASE_FILE": "caso_03.sav",
      "SUB_FILE": "accc_peak.sub"
    }
  ]
}
```

#### Uso

```bash
# Generar configs separados (uno por caso)
python generate_config.py \
  --template accc_sweep.yml \
  --variables variables.json \
  --output ./configs

# Genera:
# - config_Caso_01_Base.yml
# - config_Caso_02_Crecimiento.yml
# - config_Caso_03_Punta.yml

# O generar un solo archivo combinado
python generate_config.py \
  --template accc_sweep.yml \
  --variables variables.json \
  --output ./configs \
  --combined

# Genera:
# - config_combined.yml (todas las simulaciones)
```

**Ventajas:**
- ✅ Perfecto para 50+ casos
- ✅ Una sola línea de comando para generar todos
- ✅ Fácil de actualizar (solo edita variables.json)
- ✅ Escalable: agregar casos es solo agregar líneas al JSON

**Desventajas:**
- ❌ Requiere aprender a usar generate_config.py
- ❌ Más pasos que YAML anchors

## Comparativa

| Característica | YAML Anchors | Generator |
|---|---|---|
| Casos 2-10 | ✅ Mejor | ⚠️ Overkill |
| Casos 50+ | ⚠️ Lento | ✅ Mejor |
| Sin dependencias | ✅ Sí | ✅ Sí (Python nativo) |
| Fácil de aprender | ✅ Sí | ⚠️ Un poco |
| Escalable | ⚠️ Limitado | ✅ Sí |
| Lee como YAML | ✅ Sí | ✅ Sí |

## Recomendación

1. **Comienza con YAML Anchors** - Es más simple y no necesita herramientas
2. **Si crece a 50+ casos** - Cambia a Generator
3. **Puedes combinar** - Usa anchors + generator juntos

## Ejemplos Completos

### Ejemplo 1: ACCC Multi-Caso con Anchors

Ver: `config_accc_multi.yml` (en template/optional/examples/)

```bash
pssetools sim-runner --config config_accc_multi.yml --summary
```

### Ejemplo 2: Generator para Sweep Paramétrico

```bash
# En template/optional/templates/ hay ejemplos listos:
# - accc_sweep.yml (template)
# - variables_example.json (5 casos de ejemplo)

cd pssetools/template/optional/templates
python ../scripts/generate_config.py \
  --template accc_sweep.yml \
  --variables variables_example.json \
  --output ../../..

# Genera config_Caso_0X.yml en la carpeta principal
```

## Troubleshooting

### "El YAML anchor no funciona"
- Revisa la sintaxis: `&nombre` para definir, `*nombre` o `<<: *nombre` para usar
- Los anchors son case-sensitive

### "El generator no reemplaza variables"
- Usa `{{NOMBRE}}` (con llaves dobles)
- Las claves en JSON deben coincidir exactamente (case-sensitive)

### "Generé muchos archivos config_*.yml y no sé cuál ejecutar"
- Usar `--combined` para generar un solo archivo
- O ejecutarlos en secuencia: `for f in config_*.yml; do pssetools sim-runner --config $f; done`

## Ver También

- `config_pattern.yml` - Referencia completa de sintaxis YAML
- `SIM_RUNNER_GUIDE.md` - Cómo ejecutar las configs generadas
- `generate_config.py --help` - Ayuda del generador
