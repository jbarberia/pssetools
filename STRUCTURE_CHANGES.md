# Simplificación de Estructura - Cambios Importantes

## 🎯 Principales Cambios

### ❌ ELIMINADO
- ✓ Templates genéricos ACCC.sub, ACCC.mon, ACCC.con, ACCC.idv
  - Estos eran innecesarios - cada proyecto tiene sus propios archivos
  - El usuario debe proporcionar sus propios estudio.sub, estudio.mon, etc.

### ✅ NUEVO
- ✓ **config.yml unificado**: Un solo archivo con TODOS los tipos de análisis
- ✓ **Estructura clara**: Usuario descomentar solo lo que ejecuta
- ✓ **Mejor organización**: convload.py con Dynamic en lib/

---

## 📁 Nueva Estructura Post-Setup

```
proyecto/
├── config.cfg                 # Configuración general (PSS/E, DLL)
├── estudio.sub               # Tu subsistema (usuario proporciona)
├── estudio.mon               # Tus puntos de monitoreo
├── estudio.con               # Tus contingencias
├── estudio.idv               # Tus canales dinámicos
├── estudio.dyr               # Datos dinámicos (usuario proporciona)
│
├── casos/                     # Tus archivos .sav
│   ├── caso_base.sav
│   ├── caso_punta.sav
│   └── caso_valle.sav
│
├── lib/                       # Scripts Python y DLLs
│   ├── convload.py           # Carga custom (dinámico)
│   ├── dyn_1ph.py            # Evento: falta monofásica
│   ├── dyn_3ph.py            # Evento: falta trifásica
│   └── *.dll, *.lib          # Modelos de usuario
│
├── templates/
│   └── config.yml            # ⭐ ARCHIVO UNIFICADO (único)
│
├── build/                     # Archivos intermedios
│   ├── caso_base.dfx         # Factores de distribución
│   ├── caso_base.acc         # Resultados ACCC
│   ├── caso_base.asc         # Resultados ASCC
│   ├── caso_base.cnv         # Caso convertido
│   └── snapshot.snp          # Snapshot dinámico
│
├── results/                   # Reportes
│   └── *.out, *.outx, *.zip
│
└── log/                       # Logs de ejecución
    └── *.log
```

---

## 🔄 Flujo de Uso

### Paso 1: Setup Inicial
```bash
pssetools setup
# → Crea carpetas
# → Copia archivos esenciales (config.cfg, estudio.*)
# → Crea templates/config.yml unificado
# → Pregunta si incluir scripts dinámicos (convload.py, dyn_*.py)
```

### Paso 2: Proporcionar Archivos
```bash
# Copiar tus archivos a proyecto
casos/
  ├── caso_base.sav       # ← Usuario proporciona
  ├── caso_punta.sav
  └── caso_valle.sav

lib/                       # Ya incluidos por setup si selecciona Dynamic
  ├── convload.py
  ├── dyn_1ph.py
  └── dyn_3ph.py
```

### Paso 3: Configurar config.yml
```bash
# Editar templates/config.yml
# Descomentar estudios que quieras ejecutar
nano templates/config.yml
```

### Paso 4: Validar
```bash
pssetools sim-runner --config templates/config.yml --validate
# Debe mostrar [OK] Configuration valid
```

### Paso 5: Ejecutar
```bash
pssetools sim-runner --config templates/config.yml
```

---

## 📝 Archivo config.yml Unificado

### Estructura
```yaml
workspace:
  base_dir: "."

simulations:
  # Descomentar lo que quieras ejecutar
  - name: "ACCC_CasoBase"      # ← Descomentar/comentar
    type: "accc"
    case: "casos/caso_base.sav"
    options: ...

  - name: "ASCC_CasoBase"       # ← Descomentar/comentar
    type: "ascc"
    case: "casos/caso_base.sav"
    options: ...

  # - name: "CNV_DynamicCase"  # ← Comentado (dinámico)
  #   type: "cnv"
  #   ...

execution:
  parallel: 1
  continue_on_error: false
```

### Ventajas
✓ Un solo archivo para todas las simulaciones  
✓ Descomentar lo que necesites (no copiar/pegar configs)  
✓ Fácil de mantener versión del proyecto  
✓ Paralelo + Sequential en el mismo archivo  

---

## 🎯 Organización de Scripts

### En lib/ (después de setup)
```
lib/
├── convload.py          # Dinámico: carga custom
├── dyn_1ph.py           # Dinámico: evento monofásico
├── dyn_3ph.py           # Dinámico: evento trifásico
├── my_model.dll         # Tu DLL compilado
└── user_models.lib      # Tu librería de modelos
```

### Usados en config.yml
```yaml
# Dinámico con convload.py
- name: "CNV_Case"
  type: "cnv"
  options:
    py: "lib/convload.py"    # ← Aquí

# Dinámico con evento personalizado
- name: "DYN_Sim"
  type: "dyn"
  options:
    py: "lib/dyn_1ph.py"     # ← O aquí
```

---

## 🔌 Tipos de Simulaciones en config.yml

Todos incluidos en template, comentados:

| Tipo | Nombre | Descripción | Archivos Base |
|------|--------|---|---|
| `accc` | Contingency | Análisis de contingencias | .sub, .mon, .con |
| `ascc` | Short Circuit | Cortocircuito | .sub |
| `cnv` | Conversion | Preparación dinámica | convload.py |
| `snp` | Snapshot | Construcción de snapshot | .dyr, .idv |
| `dyn` | Dynamic | Simulación transient stability | dyn_*.py |
| `dfx` | Factors | Factores de distribución | .sub, .mon, .con |

---

## ✅ Checklist Post-Setup

```
Después de: pssetools setup

☐ Revisar templates/config.yml
☐ Copiar casos/ .sav files
☐ Confirmar archivos esenciales:
  ☐ config.cfg
  ☐ estudio.sub
  ☐ estudio.mon
  ☐ estudio.con
  ☐ estudio.idv (si dinámico)
  ☐ estudio.dyr (si dinámico)
☐ Editar config.yml (comentar/descomentar estudios)
☐ Validar: pssetools sim-runner --config templates/config.yml --validate
☐ Ejecutar: pssetools sim-runner --config templates/config.yml
```

---

## 🎓 Ejemplo Completo

### Setup Inicial
```bash
cd /mi/proyecto
pssetools setup
# ¿Qué análisis ejecutarás? → "Todos"
# ¿Incluir scripts dinámicos? → "s"
```

### Archivos Creados
```
proyecto/
├── config.cfg          # ✓ Copiado
├── estudio.sub         # ✓ Copiado
├── estudio.mon         # ✓ Copiado
├── estudio.con         # ✓ Copiado
├── estudio.idv         # ✓ Copiado
├── lib/
│   ├── convload.py     # ✓ Copiado (dinámico)
│   ├── dyn_1ph.py      # ✓ Copiado
│   └── dyn_3ph.py      # ✓ Copiado
├── templates/
│   └── config.yml      # ✓ Creado (unificado)
└── [otras carpetas]
```

### Editar config.yml
```yaml
# Quiero ACCC + ASCC del caso base
# Descomentar esto:
- name: "ACCC_CasoBase"
  type: "accc"
  ...

- name: "ASCC_CasoBase"
  type: "ascc"
  ...

# Dejar comentado (dinámico):
# - name: "CNV_DynamicCase"
#   type: "cnv"
```

### Ejecutar
```bash
pssetools sim-runner --config templates/config.yml --validate
pssetools sim-runner --config templates/config.yml
```

✅ **¡Listo!**

---

## 📌 Notas Importantes

1. **Templates ACCC.* ya NO se generan**
   - Innecesarios (cada proyecto tiene sus propios)
   - Usuario proporciona sus archivos .sub, .mon, .con

2. **config.yml es único**
   - Todos los estudios en un archivo
   - Comentar/descomentar según necesidad

3. **convload.py va en lib/**
   - No en templates/ ni en ejemplos
   - Directamente accesible para Dynamic

4. **lib/ es para scripts + DLLs**
   - convload.py (dinámico)
   - dyn_*.py (eventos)
   - *.dll, *.lib (modelos de usuario)

---

## 🚀 Resumen

| Antes | Ahora |
|-------|-------|
| Múltiples config_*.yml | Un config.yml único |
| Templates ACCC.* genéricos | No se generan (innecesarios) |
| Scripts dinámicos en lib/ | ✓ convload.py en lib/ |
| Preguntas tipo de análisis | Sin preguntas (config unificado) |
| Copiar/pegar configs | Comentar/descomentar en YAML |

**Resultado:** Proyecto más limpio, estructura unificada, menos archivos innecesarios.
