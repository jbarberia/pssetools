# Guía: Setup Wizard - Asistente de Configuración

## ¿Qué es?

`pssetools setup` es un **asistente interactivo completamente en español** que configura automáticamente tu proyecto PSS/E. Crea carpetas, archivos, y **templates de configuración listos para usar**.

## Inicio Rápido

```bash
pssetools setup
```

## Estructura del Proyecto

El wizard crea automáticamente:

```
tu_proyecto/
├── templates/           ← Templates YAML y PSS/E
│   ├── accc.sub        
│   ├── accc.mon        
│   ├── accc.con        
│   ├── config_accc.yml
│   ├── config_ascc.yml
│   └── config_dynamic.yml
├── casos/              ← Aquí pones tus .sav
├── build/              ← Salidas (.dfx, .acc)
├── results/            ← Reportes finales
├── lib/                ← Scripts Python
├── log/                ← Logs
└── config.cfg          ← Config PSS/E
```

## Opciones del Wizard

```
¿Qué análisis ejecutarás?
  1) ACCC (Análisis de Contingencias)
  2) ASCC (Análisis de Cortocircuito)
  3) Simulación Dinámica
  4) Todos
  5) Solo esenciales
```

## Flujo Típico

### 1. Crear proyecto nuevo
```bash
$ pssetools setup
$ Tu elección: 4  # Todos
```

Genera: carpetas + templates para ACCC, ASCC, DYN

### 2. Personalizar templates
```bash
$ nano templates/config_accc.yml
```

### 3. Ejecutar análisis
```bash
$ pssetools sim-runner --config templates/config_accc.yml
```

## Modo: Modificar Proyecto

Si ejecutas setup en un proyecto existente:

```
Proyecto existente detectado

¿Qué deseas?
  1) Modificar      ← Regenerar templates, copiar ejemplos
  2) Crear nuevo    ← Sobrescribir
  3) Salir
```

## Templates Personalizados

Edita `templates/config_accc.yml`:

```yaml
workspace:
  base_dir: "."

simulations:
  - name: "ACCC_Base"
    type: "accc"
    case: "casos/mi_caso.sav"
    options:
      sub: "templates/accc.sub"
      mon: "templates/accc.mon"
      con: "templates/accc.con"
      dfx: "build/accc.dfx"

execution:
  continue_on_error: false
  logging: "normal"
```

## Múltiples Casos (YAML Anchors)

```yaml
base: &base
  type: "accc"
  options: &opts
    sub: "templates/accc.sub"

simulations:
  - <<: *base
    name: "Caso_01"
    case: "casos/caso_01.sav"
    options:
      <<: *opts
      dfx: "build/caso_01.dfx"
  
  - <<: *base
    name: "Caso_02"
    case: "casos/caso_02.sav"
    options:
      <<: *opts
      dfx: "build/caso_02.dfx"
```

Ver: `PARAMETRIZATION_GUIDE.md` para más técnicas

## Integración con sim-runner

Los templates creados funcionan directamente con `sim-runner`:

```bash
pssetools sim-runner --config templates/config_accc.yml --summary
pssetools sim-runner --config templates/config_accc.yml --dry-run
pssetools sim-runner --config templates/config_accc.yml
```

## Próximos Pasos

1. Ejecuta: `pssetools setup`
2. Coloca .sav en: `casos/`
3. Edita: `templates/config_*.yml`
4. Ejecuta: `pssetools sim-runner --config templates/config_accc.yml`

¡Listo! 🚀
