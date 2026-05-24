# Configuration Parametrization Guide

See **`pssetools/template/optional/docs/PARAMETRIZATION_GUIDE.md`** in the template folder for detailed documentation on:

- **YAML Anchors** - For 2-10 similar cases (DRY pattern, no tools needed)
- **Config Generator** - For 50+ cases (batch mode with template + variables)
- **Examples** - Real-world patterns for ACCC, ASCC, and dynamic simulations

## Quick Start

### Option 1: YAML Anchors (Recommended for most users)

Define common settings once, reference multiple times:

```yaml
accc_defaults: &accc_options
  sub: "studies/accc.sub"
  mon: "studies/accc.mon"
  con: "studies/accc.con"

simulations:
  - name: "ACCC_Caso_01"
    type: "accc"
    case: "casos/caso_01.sav"
    options:
      <<: *accc_options    # ← Inherit all settings
      dfx: "build/caso_01.dfx"

  - name: "ACCC_Caso_02"
    type: "accc"
    case: "casos/caso_02.sav"
    options:
      <<: *accc_options    # ← Inherit all settings
      dfx: "build/caso_02.dfx"
```

**Benefit**: Change `accc.sub` once, applies to all cases

### Option 2: Config Generator (For 50+ similar cases)

Template + variables → Multiple configs in one command

```bash
# 1. Create template with {{PLACEHOLDER}}
# 2. Create JSON with variables
# 3. Generate configs

python generate_config.py \
  --template accc_sweep.yml \
  --variables variables.json \
  --output ./configs

# Generates: config_Caso_01.yml, config_Caso_02.yml, ...
```

See `template/optional/templates/` for ready-to-use examples.

## Related Documentation

- **SIM_RUNNER_GUIDE.md** - How to execute the generated/parameterized configs
- **SETUP_WIZARD_GUIDE.md** - Creating your workspace
- **template/README.md** - Template folder structure
