# Configuraciones de Ejemplo - Estudios Estáticos

Esta carpeta contiene ejemplos de configuración YAML lista para usar con el `sim-runner`.

## 📋 Archivos Disponibles

### `config_simple.yml` ⭐ **RECOMENDADO PARA EMPEZAR**
- **Descripción:** Un solo caso con ACCC + ASCC
- **Casos:** 1 (Base)
- **Estudios:** 2 (1 ACCC + 1 ASCC)
- **Ejecución:** Secuencial
- **Tiempo:** ~10 minutos

**Uso:**
```bash
# Copiar a tu proyecto
cp config_simple.yml config.yml

# Editar rutas
nano config.yml  # o tu editor preferido

# Validar
python -m pssetools sim-runner --config config.yml --validate

# Ejecutar
python -m pssetools sim-runner --config config.yml
```

### `config_estaticos.yml` - Producción Completa
- **Descripción:** Múltiples casos con ACCC + ASCC
- **Casos:** 3 (Base, Punta, Valle)
- **Estudios:** 6 (3 ACCC + 3 ASCC)
- **Ejecución:** Paralela (2 workers)
- **Tiempo:** ~15 minutos (vs 30 secuencial)

**Uso:**
```bash
python -m pssetools sim-runner --config config_estaticos.yml
```

### `config_accc.yml` - ACCC Solo
- **Descripción:** Análisis de contingencias solamente
- **Casos:** 2
- **Estudios:** 2 ACCC
- **Ejecución:** Secuencial

**Uso:**
```bash
python -m pssetools sim-runner --config config_accc.yml
```

### `config_accc_parallel.yml` - ACCC Paralelo
- **Descripción:** Múltiples ACCC en paralelo
- **Casos:** 4
- **Estudios:** 4 ACCC
- **Ejecución:** Paralela (2 workers)

**Uso:**
```bash
python -m pssetools sim-runner --config config_accc_parallel.yml
```

### `config_parallel_full.yml` - Todos los Tipos
- **Descripción:** ACCC, ASCC y Dynamic simultáneos
- **Casos:** 2
- **Estudios:** 6 (2 ACCC + 2 ASCC + 2 Dynamic)
- **Ejecución:** Paralela (4 workers)

**Uso:**
```bash
python -m pssetools sim-runner --config config_parallel_full.yml
```

---

## 🚀 Guía Rápida (3 Pasos)

### 1. Copiar Archivo
```bash
cp config_simple.yml mi_estudio.yml
```

### 2. Editar Rutas
Abre `mi_estudio.yml` y cambia:
```yaml
case: "casos/tu_caso_aqui.sav"  # Tu archivo
sub: "tu_estudio.sub"            # Tu subsistema
mon: "tu_estudio.mon"            # Tus puntos de monitoreo
con: "tu_estudio.con"            # Tus contingencias
```

### 3. Ejecutar
```bash
# Validar primero
python -m pssetools sim-runner --config mi_estudio.yml --validate

# Ejecutar
python -m pssetools sim-runner --config mi_estudio.yml
```

---

## 📝 Estructura YAML Mínima

```yaml
workspace:
  base_dir: "."

simulations:
  - name: "MiEstudio"
    type: "accc"
    case: "casos/caso.sav"
    options:
      sub: "estudio.sub"
      mon: "estudio.mon"
      con: "estudio.con"
      acc: "build/resultado.acc"

execution:
  parallel: 1
  continue_on_error: false
```

**Campos obligatorios:**
- ✓ `workspace:` (puede estar vacío)
- ✓ `simulations:` (debe tener al menos 1)
- ✓ `name:` (identificador único)
- ✓ `type:` ("accc" o "ascc")
- ✓ `case:` (ruta del .sav)
- ✓ `options:` (parámetros del estudio)
- ✓ `execution:` (cómo ejecutar)

---

## ⚙️ Opciones por Tipo de Estudio

### ACCC (Contingency Analysis)
```yaml
type: "accc"
options:
  sub: "estudio.sub"      # [requerido] Subsistema
  mon: "estudio.mon"      # [requerido] Monitor points
  con: "estudio.con"      # [requerido] Contingencies
  dfx: "build/dfx"        # [opcional] Distribution factors
  acc: "build/resultado.acc"  # [opcional] Salida ACCC
  zipfile: "build/reporte.zip"  # [opcional] Reporte comprimido
```

### ASCC (Short Circuit)
```yaml
type: "ascc"
options:
  sub: "estudio.sub"      # [requerido] Subsistema
  mon: "estudio.mon"      # [requerido] Monitor points
  asc: "build/resultado.asc"  # [opcional] Salida ASCC
  dfx: "build/dfx"        # [opcional] Distribution factors
```

---

## 🔄 Ejecución Paralela

Para acelerar estudios, usa:

```yaml
execution:
  parallel: 2  # Ejecuta 2 estudios simultáneamente
```

**Efectivo para:**
- ✓ Múltiples casos del mismo tipo (3x ACCC = 50% más rápido)
- ✓ ACCC + ASCC juntos (2 workers, alterna entre tipos)
- ✓ Análisis de escenarios (5+ casos)

**Recomendaciones por sistema:**
- Laptop: `parallel: 2` (4 cores máximo)
- PC Estación: `parallel: 4` (8 cores)
- Servidor: `parallel: 8` (16 cores)

---

## ✅ Validación

Siempre valida antes de ejecutar:

```bash
python -m pssetools sim-runner --config config.yml --validate
```

**Salida esperada (correcta):**
```
[OK] Configuration valid

Workspace:
  Base directory: .

Simulations (2):
  [1] ACCC_Base (ACCC) - casos/caso.sav
  [2] ASCC_Base (ASCC) - casos/caso.sav
```

---

## 🐛 Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| "simulations" section | YAML sin `simulations:` | Copia de `config_simple.yml` |
| "Case file not found" | Ruta incorrecta | Verifica que exista `casos/caso.sav` |
| "subsystem file not found" | .sub no existe | Copia `.sub` a la carpeta del proyecto |
| "Indentation error" | Espacios mal alineados | Usa 2 espacios, nunca tabs |
| Configuration not valid | YAML malformado | Valida con `--validate` |

---

## 📚 Documentación Completa

- **`QUICK_START_ESTATICOS.md`** - Guía rápida de 5 minutos
- **`PARALLELIZATION_GUIDE.md`** - Ejecución en paralelo avanzada
- **`docs/SIM_RUNNER_GUIDE.md`** - Manual completo (repo raíz)
- **`docs/PARAMETRIZATION_GUIDE.md`** - Evitar repetición en configs

---

## 💡 Ejemplos de Adaptación

### Cambiar Nombre del Estudio
```yaml
- name: "MiAnalisisPersonalizado"  # ← Cambia esto
  type: "accc"
```

### Agregar Más Casos
```yaml
simulations:
  - name: "ACCC_Base"
    type: "accc"
    case: "casos/caso_base.sav"
    ...
  
  - name: "ACCC_Punta"  # ← Nuevo caso
    type: "accc"
    case: "casos/caso_punta.sav"
    ...
```

### Aumentar Paralelismo
```yaml
execution:
  parallel: 4  # Cambia de 2 a 4
```

### Continuar ante Errores
```yaml
execution:
  continue_on_error: true  # Si falla uno, continúa con otros
```

---

## 🎯 Casos de Uso

### Escenario 1: Probar con Un Solo Caso
```bash
# Usa: config_simple.yml
# Tiempo: ~10 min
# Riesgo: Bajo (solo 1 caso)
```

### Escenario 2: Análisis de 3 Casos (Base, Punta, Valle)
```bash
# Usa: config_estaticos.yml
# Tiempo: ~15 min (6 estudios en paralelo)
# Riesgo: Medio (completo)
```

### Escenario 3: Batch de 50+ Casos
```bash
# Genera config automáticamente con:
# pssetools setup → Opción de generador de configs
# O copia y modifica manualmente
```

---

## ✨ Próximos Pasos

1. **Copia:** `config_simple.yml` → `config.yml`
2. **Edita:** Rutas de tus archivos
3. **Valida:** `--validate`
4. **Prueba:** `--dry-run`
5. **Ejecuta:** Sin opciones

¡Listo para usar! 🚀
