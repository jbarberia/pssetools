# Guía Rápida - Estudios Estáticos (ACCC + ASCC)

## Problema Común: "Configuration must have 'simulations' section"

Este error ocurre cuando el archivo YAML no tiene la estructura correcta.

### ✅ Estructura Correcta

```yaml
workspace:
  base_dir: "."

simulations:
  - name: "ACCC_MiEstudio"
    type: "accc"
    case: "mi_caso.sav"
    options:
      sub: "estudio.sub"
      mon: "estudio.mon"
      con: "estudio.con"
      dfx: "build/resultado.dfx"
      acc: "build/resultado.acc"

execution:
  parallel: 1
  continue_on_error: false
```

**Puntos críticos:**
- ✓ `workspace:` debe estar presente
- ✓ `simulations:` debe ser una lista (empieza con `-`)
- ✓ Cada simulación tiene `name`, `type`, `case`, `options`
- ✓ `execution:` sección de configuración

---

## Empezar en 3 Pasos

### Paso 1: Copiar Archivo Listo
```bash
# Opción A: Un solo caso (recomendado para empezar)
cp config_simple.yml config.yml

# Opción B: Múltiples casos (ACCC+ASCC combinados)
cp config_estaticos.yml config.yml
```

### Paso 2: Editar Rutas
Abre `config.yml` y cambia:
- `casos/mi_caso.sav` → Tu archivo .sav real
- `estudio.sub` → Tu archivo .sub real
- Carpetas de salida (`build/`) pueden quedar igual

### Paso 3: Ejecutar
```bash
# Validar primero (recomendado)
python -m pssetools sim-runner --config config.yml --validate

# Ejecutar
python -m pssetools sim-runner --config config.yml
```

---

## Archivos Listos para Usar

### `config_simple.yml` - Recomendado para Empezar
- ✓ 1 ACCC + 1 ASCC (un solo caso)
- ✓ Minimal y fácil de entender
- ✓ Perfecto para probar
- Uso: `pssetools sim-runner --config config_simple.yml`

### `config_estaticos.yml` - Producción
- ✓ 3 casos (Base, Punta, Valle)
- ✓ ACCC + ASCC para cada caso (6 simulaciones)
- ✓ Ejecución paralela: 2 trabajadores
- Uso: `pssetools sim-runner --config config_estaticos.yml`

---

## Validación Rápida

Antes de ejecutar, siempre valida:

```bash
python -m pssetools sim-runner --config config.yml --validate
```

**Salida correcta:**
```
[OK] Configuration valid

Workspace:
  Base directory: .

Simulations (2):
  [1] ACCC_EstudioPrincipal (ACCC) - casos/mi_caso.sav
  [2] ASCC_EstudioPrincipal (ASCC) - casos/mi_caso.sav

Execution Options:
  Parallel jobs: 1
  Continue on error: False
```

**Si da error:** El YAML tiene problemas de sintaxis (indentación, etc.)

---

## Estudios Estáticos (ACCC + ASCC)

### ACCC (Análisis de Contingencias)
```yaml
- name: "ACCC_MiEstudio"
  type: "accc"
  case: "casos/caso.sav"
  options:
    sub: "estudio.sub"      # Subsistema a analizar
    mon: "estudio.mon"      # Puntos de monitoreo
    con: "estudio.con"      # Lista de contingencias
    dfx: "build/result.dfx" # Factores de distribución
    acc: "build/result.acc" # Resultados ACCC
```

### ASCC (Análisis de Cortocircuito)
```yaml
- name: "ASCC_MiEstudio"
  type: "ascc"
  case: "casos/caso.sav"
  options:
    sub: "estudio.sub"      # Subsistema
    asc: "build/result.asc" # Resultados ASCC
```

**Pueden ir juntos en la misma configuración:**
```yaml
simulations:
  - name: "ACCC_Caso1"
    type: "accc"
    ...
  
  - name: "ASCC_Caso1"
    type: "ascc"
    ...
```

---

## Ejecución Paralela (Estudios Estáticos)

Para ACCC + ASCC en paralelo:

```yaml
execution:
  parallel: 2  # Ejecuta 2 al mismo tiempo
  continue_on_error: true
```

**Ejemplo con 3 casos:**
```
Caso 1 ACCC ──┐
Caso 1 ASCC ──┤─→ Worker 1, Worker 2
Caso 2 ACCC ──┤
Caso 2 ASCC ──┘

Tiempo total: ~50% menos que secuencial
```

---

## Comandos Útiles

### Validar Configuración
```bash
python -m pssetools sim-runner --config config.yml --validate
```

### Preview (sin ejecutar)
```bash
python -m pssetools sim-runner --config config.yml --dry-run
```

### Ejecutar y Continuar ante Errores
```bash
python -m pssetools sim-runner --config config.yml --continue-on-error
```

### Usar Script Interactivo (Windows)
```bash
run_simulations.bat
# Selecciona config → Elige modo → Ejecuta
```

---

## Troubleshooting

### "Configuration must have 'simulations' section"
**Causa:** El YAML no tiene la clave `simulations:`
**Solución:** Copia de `config_simple.yml` y personaliza

### "Case file not found: casos/caso.sav"
**Causa:** La ruta del archivo .sav es incorrecta
**Solución:** Verifica que exista el archivo en esa ruta

### "subsystem file not found: estudio.sub"
**Causa:** El archivo .sub no existe en la carpeta
**Solución:** Crea con `pssetools setup` o copia manualmente

### Indentation errors en YAML
**Causa:** Espacios incorrectos (usar 2 o 4 espacios, no tabs)
**Solución:** Usa un editor de texto con validación YAML

---

## Próximos Pasos

1. Copia `config_simple.yml` → `config.yml`
2. Edita rutas (casos, archivos .sub/.mon/.con)
3. Valida: `pssetools sim-runner --config config.yml --validate`
4. Prueba: `pssetools sim-runner --config config.yml --dry-run`
5. Ejecuta: `pssetools sim-runner --config config.yml`

¡Listo para usar! 🚀
