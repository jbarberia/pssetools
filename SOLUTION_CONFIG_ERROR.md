# Solución: Error "Configuration must have 'simulations' section"

## El Problema

```
[ERROR] Configuration validation failed:
  - Configuration must have 'simulations' section
```

Este error ocurre cuando el archivo YAML no tiene la estructura correcta.

---

## ¿Por Qué Ocurre?

El `sim-runner` espera esta estructura mínima:

```yaml
workspace:
  base_dir: "."

simulations:
  - name: "MiEstudio"
    type: "accc"
    case: "casos/caso.sav"
    options:
      sub: "estudio.sub"
      acc: "build/resultado.acc"

execution:
  parallel: 1
```

**Si le falta `simulations:`** → Error

---

## ✅ Solución Rápida

### Opción 1: Usar Archivo Listo (RECOMENDADO)

```bash
# Copiar archivo simple y validado
cp pssetools/template/optional/examples/config_simple.yml config.yml

# Editar solo las rutas
nano config.yml
```

**Cambiar:**
```yaml
case: "casos/mi_caso.sav"  # ← Tu archivo .sav
sub: "estudio.sub"         # ← Tu archivo .sub
mon: "estudio.mon"         # ← Tu archivo .mon
con: "estudio.con"         # ← Tu archivo .con
```

**Ejecutar:**
```bash
python -m pssetools sim-runner --config config.yml
```

---

### Opción 2: Crear Archivo Manualmente

Si quieres crear `config.yml` desde cero:

```yaml
workspace:
  base_dir: "."

simulations:
  - name: "ACCC_MiCaso"
    type: "accc"
    case: "casos/tu_caso.sav"
    options:
      sub: "estudio.sub"
      mon: "estudio.mon"
      con: "estudio.con"
      acc: "build/resultado.acc"

  - name: "ASCC_MiCaso"
    type: "ascc"
    case: "casos/tu_caso.sav"
    options:
      sub: "estudio.sub"
      asc: "build/resultado.asc"

execution:
  parallel: 1
  continue_on_error: false
```

**Puntos críticos:**
- ✓ `simulations:` está presente
- ✓ Es una **lista** (empieza con `-`)
- ✓ Cada item tiene `name`, `type`, `case`, `options`
- ✓ Indentación correcta (2 espacios, nunca tabs)

---

## 🔍 Verificar Archivo

Antes de ejecutar, siempre valida:

```bash
python -m pssetools sim-runner --config config.yml --validate
```

**Si dice `[OK] Configuration valid`** → Archivo está bien

**Si da error** → Hay problema en el YAML

---

## 📋 Archivos Listos para Usar

En la carpeta `pssetools/template/optional/examples/`:

| Archivo | Descripción | Casos | Estudios |
|---------|---|---|---|
| `config_simple.yml` | ⭐ Empezar aquí | 1 | ACCC + ASCC |
| `config_estaticos.yml` | Producción | 3 | 3 ACCC + 3 ASCC |
| `config_accc.yml` | Solo contingencias | 2 | ACCC |
| `config_accc_parallel.yml` | ACCC paralelo | 4 | 4 ACCC |

**Uso:**
```bash
# Copiar cualquiera
cp pssetools/template/optional/examples/config_simple.yml config.yml

# Editar rutas
nano config.yml

# Ejecutar
python -m pssetools sim-runner --config config.yml
```

---

## 🎯 Caso de Uso: Estudios Estáticos

**ACCC** (Análisis de Contingencias) + **ASCC** (Cortocircuito) **van juntos:**

```yaml
simulations:
  # Ambos análisis del MISMO caso
  - name: "ACCC_CasoBase"
    type: "accc"
    case: "casos/caso_base.sav"
    options:
      sub: "estudio.sub"
      mon: "estudio.mon"
      con: "estudio.con"
      acc: "build/caso_base.acc"

  - name: "ASCC_CasoBase"
    type: "ascc"
    case: "casos/caso_base.sav"
    options:
      sub: "estudio.sub"
      asc: "build/caso_base.asc"
```

---

## 📝 Guía Paso a Paso

### 1️⃣ Ir a Carpeta del Proyecto
```bash
cd C:\Users\User\Desktop\prueba_pssetool
```

### 2️⃣ Copiar Archivo Listo
```bash
# Desde la raíz del repo de pssetools
cp C:\path\to\pssetools\pssetools\template\optional\examples\config_simple.yml .\config.yml
```

O copiar manualmente el contenido.

### 3️⃣ Editar `config.yml`
```yaml
simulations:
  - name: "ACCC_MiEstudio"
    type: "accc"
    case: "casos/MI_CASO.sav"        # ← Cambiar aquí
    options:
      sub: "MI_ESTUDIO.sub"          # ← Cambiar aquí
      mon: "MI_ESTUDIO.mon"          # ← Cambiar aquí
      con: "MI_ESTUDIO.con"          # ← Cambiar aquí
      acc: "build/resultado.acc"

  - name: "ASCC_MiEstudio"
    type: "ascc"
    case: "casos/MI_CASO.sav"
    options:
      sub: "MI_ESTUDIO.sub"
      asc: "build/resultado_ascc.asc"
```

### 4️⃣ Validar
```bash
python -m pssetools sim-runner --config config.yml --validate
```

**Debe mostrar:**
```
[OK] Configuration valid
```

### 5️⃣ Ejecutar
```bash
python -m pssetools sim-runner --config config.yml
```

---

## 🚨 Errores y Soluciones

| Mensaje | Causa | Solución |
|---------|-------|----------|
| `simulations' section` | Falta la clave `simulations:` | Añadir `simulations:` |
| `Case file not found` | Ruta incorrecta | Verificar que existe `casos/caso.sav` |
| `subsystem file not found` | No existe `.sub` | Usar archivo correcto |
| `Indentation error` | Espacios mal | Usar 2 espacios siempre |
| `yaml parsing error` | YAML malformado | Usar validador YAML online |

---

## ✨ Resumen

1. **Copiar** archivo listo: `config_simple.yml`
2. **Editar** rutas de tus archivos
3. **Validar** con `--validate`
4. **Ejecutar** sin opciones extra

Listo para usar. No hay que crear nada desde cero. 🚀
