# PSS/E Simulation Runner - Complete Guide

## Overview

`pssetools sim-runner` is a **unified command** for executing PSS/E simulations from configuration files. It replaces the need for multiple bash/PowerShell scripts with a single, portable **Python-based solution**.

### Key Benefits

- ✅ **Single script in Python** - No bash/PowerShell dependencies
- ✅ **Configuration-driven** - Define simulations in YAML/JSON
- ✅ **Cross-platform** - Works on Windows, Linux, macOS
- ✅ **Easy to maintain** - Pure Python, version-controllable
- ✅ **Flexible** - Support for ACCC, ASCC, Dynamic, and other analyses
- ✅ **Deterministic** - Same results across platforms

---

## Quick Start

### 1. Create a Configuration File

Save as `config.yml`:

```yaml
workspace:
  base_dir: "."

simulations:
  - name: "ACCC_Analysis"
    type: "accc"
    case: "caso.sav"
    options:
      sub: "estudio.sub"
      mon: "estudio.mon"
      con: "estudio.con"
      dfx: "build/caso.dfx"
      acc: "build/caso.acc"

execution:
  continue_on_error: false
  logging: "normal"
```

### 2. Run the Simulations

```bash
pssetools sim-runner --config config.yml
```

### 3. Optional: Validate First

```bash
pssetools sim-runner --config config.yml --validate
```

---

## Configuration Format

### File Format

Both **YAML** and **JSON** are supported:

```bash
# YAML format (recommended)
pssetools sim-runner --config config.yml

# JSON format (also works)
pssetools sim-runner --config config.json
```

### Basic Structure

```yaml
workspace:
  base_dir: "."              # Working directory

simulations:                 # List of simulations
  - name: "Study_Name"       # Unique identifier
    type: "accc|ascc|dyn|..." # Simulation type
    case: "path/to/caso.sav" # PSS/E case file
    options:                 # Command-line options
      sub: "estudio.sub"
      key: "value"

execution:                   # Execution settings
  continue_on_error: false
  logging: "normal"
  interactive: false
```

---

## Simulation Types

### ACCC - Contingency Analysis

```yaml
- name: "ACCC_Study"
  type: "accc"
  case: "casos/caso.sav"
  options:
    sub: "estudio.sub"
    mon: "estudio.mon"
    con: "estudio.con"
    dfx: "build/caso.dfx"
    acc: "build/caso.acc"
    zipfile: "build/caso.zip"
```

### ASCC - Short Circuit Analysis

```yaml
- name: "ASCC_Study"
  type: "ascc"
  case: "casos/caso.sav"
  options:
    sub: "estudio.sub"
    report: "results/cortocircuito.scf"
```

### Dynamic Simulation - Case Conversion

```yaml
- name: "DYN_Convert"
  type: "cnv"
  case: "casos/caso.sav"
  options:
    cnv: "build/caso.cnv"
    py: "convload.py"
```

### Dynamic Simulation - Snapshot Build

```yaml
- name: "DYN_Snapshot"
  type: "snp"
  case: "casos/caso.sav"
  options:
    snp: "build/snapshot.snp"
    dyr: "datos/dinamico.dyr"
    idv: "estudio.idv"
    cc: "build/cc.flx"
    ct: "build/ct.flx"
```

### Dynamic Simulation - Time-Domain Run

```yaml
- name: "DYN_Transient"
  type: "dynamic"
  case: "casos/caso.sav"
  options:
    cnv: "build/caso.cnv"
    snp: "build/snapshot.snp"
    out: "results/dyn_evento.out"
    py: "dyn_1ph.py"
```

---

## Command-Line Options

### Validation

```bash
# Validate configuration without executing
pssetools sim-runner --config config.yml --validate

# Output:
# [OK] Configuration valid
# ======================================================================
#                      CONFIGURATION SUMMARY                           
# ======================================================================
#
# Workspace:
#   Base directory: .
#
# Simulations (3):
#   [1] ACCC_Study (ACCC) - casos/caso.sav
#   [2] ASCC_Study (ASCC) - casos/caso.sav
#   [3] DYN_Transient (DYNAMIC) - casos/caso.sav
#
# Execution Options:
#   Parallel jobs: 1
#   Continue on error: False
#   Logging level: normal
```

### Summary Only

```bash
# Show configuration summary and exit
pssetools sim-runner --config config.yml --summary
```

### Interactive Mode

```bash
# Ask for confirmation before each simulation
pssetools sim-runner --config config.yml --interactive

# Output:
# [1/3] ACCC_Study
# Execute this simulation? [y/n]: y
# [*] Executing: ACCC_Study
# ...
```

### Dry Run (Preview Commands)

```bash
# Show commands but don't execute
pssetools sim-runner --config config.yml --dry-run

# Output:
# [*] Executing: ACCC_Study
# [*] Command: python -m pssetools accc --sav casos/caso.sav ...
# [!] DRY RUN - Command not executed
```

### Continue on Error

```bash
# Don't stop even if a simulation fails
pssetools sim-runner --config config.yml --continue-on-error
```

### Combine Options

```bash
# Interactive + dry-run to preview before executing
pssetools sim-runner --config config.yml --dry-run --interactive

# Validate, then execute with error recovery
pssetools sim-runner --config config.yml --validate --continue-on-error
```

---

## Examples

### Example 1: Simple ACCC Study

**File: accc_study.yml**

```yaml
workspace:
  base_dir: "."

simulations:
  - name: "ACCC_CasoBase_2024"
    type: "accc"
    case: "casos/caso_base.sav"
    options:
      sub: "estudio.sub"
      mon: "estudio.mon"
      con: "estudio.con"
      dfx: "build/caso_base.dfx"
      acc: "build/caso_base.acc"

execution:
  continue_on_error: false
  logging: "normal"
```

**Run:**

```bash
pssetools sim-runner --config accc_study.yml
```

---

### Example 2: Dynamic Simulation Workflow

**File: dynamic_study.yml**

```yaml
workspace:
  base_dir: "."

simulations:
  # Convert case with custom models
  - name: "Step1_CaseConversion"
    type: "cnv"
    case: "casos/caso_base.sav"
    options:
      cnv: "build/caso_base.cnv"
      py: "convload.py"

  # Build transient stability snapshot
  - name: "Step2_Snapshot"
    type: "snp"
    case: "casos/caso_base.sav"
    options:
      snp: "build/snapshot.snp"
      dyr: "datos/dinamico.dyr"
      idv: "estudio.idv"
      cc: "build/cc.flx"
      ct: "build/ct.flx"

  # Run simulation - 1F event
  - name: "Step3_Sim_1F"
    type: "dynamic"
    case: "casos/caso_base.sav"
    options:
      cnv: "build/caso_base.cnv"
      snp: "build/snapshot.snp"
      out: "results/dyn_1f.out"
      py: "dyn_1ph.py"

  # Run simulation - 3F event
  - name: "Step4_Sim_3F"
    type: "dynamic"
    case: "casos/caso_base.sav"
    options:
      cnv: "build/caso_base.cnv"
      snp: "build/snapshot.snp"
      out: "results/dyn_3f.out"
      py: "dyn_3ph.py"

execution:
  continue_on_error: false
  logging: "verbose"
```

**Run:**

```bash
# Preview before executing
pssetools sim-runner --config dynamic_study.yml --dry-run

# Execute if looks good
pssetools sim-runner --config dynamic_study.yml
```

---

### Example 3: Complete Study (ACCC + ASCC + Dynamic)

See: `config_complete.yml` in templates

```bash
pssetools sim-runner --config config_complete.yml
```

---

## Configuration Templates

The following templates are included:

- **`config_accc.yml`** - ACCC (contingency) analysis example
- **`config_ascc.yml`** - ASCC (short circuit) analysis example *(available via setup wizard)*
- **`config_dynamic.yml`** - Dynamic simulation workflow
- **`config_complete.yml`** - All analyses in one workflow

Copy and customize for your project:

```bash
cp config_accc.yml my_study.yml
# Edit my_study.yml with your case files and options
pssetools sim-runner --config my_study.yml
```

---

## Execution Modes

### Sequential Execution (Default)

Simulations run one after another:

```yaml
execution:
  continue_on_error: false  # Stop on first failure
```

**Behavior:**
1. Executes sim 1 → waits for completion
2. Executes sim 2 → waits for completion
3. Executes sim 3 → waits for completion
4. STOP if any fails

### Continue on Error

```yaml
execution:
  continue_on_error: true   # Continue despite failures
```

**Behavior:**
1. Executes sim 1 → fails but continues
2. Executes sim 2 → continues
3. Executes sim 3 → continues
4. Reports all successes and failures

### Interactive Confirmation

```bash
pssetools sim-runner --config config.yml --interactive
```

**Behavior:**
- Before each simulation, asks user: "Execute this simulation? [y/n]"
- User can skip individual simulations

---

## Output and Logging

### Log Levels

```yaml
execution:
  logging: "normal"  # Default: Shows basic info
  # logging: "verbose"  # Shows detailed output
  # logging: "debug"    # Shows everything (not yet implemented)
```

### Output Example

```
[OK] Configuration valid

======================================================================
                     STARTING SIMULATIONS                            
======================================================================

[*] Starting execution of 3 simulation(s)

[1/3] ACCC_Study
[*] Executing: ACCC_Study
[*] Command: python -m pssetools accc --sav casos/caso.sav ...
[OK] Completed: ACCC_Study

[2/3] ASCC_Study
[*] Executing: ASCC_Study
[*] Command: python -m pssetools ascc --sav casos/caso.sav ...
[OK] Completed: ASCC_Study

[3/3] DYN_Transient
[*] Executing: DYN_Transient
[*] Command: python -m pssetools dynamic --cnv build/caso.cnv ...
[ERROR] Failed: Process exited with code 1

[!] Stopping execution (continue_on_error=false)

======================================================================
                       EXECUTION SUMMARY                             
======================================================================

Total simulations: 3
[OK] Successful: 2
[ERROR] Failed: 1

Completed at: 2024-05-24 12:00:00
```

---

## Troubleshooting

### Configuration Not Found

```
[ERROR] Configuration file not found: config.yml
```

**Fix:** Make sure file exists and path is correct:

```bash
pssetools sim-runner --config ./config.yml
pssetools sim-runner --config /full/path/to/config.yml
```

### Configuration Validation Failed

```
[ERROR] Configuration validation failed:
  - Simulation 0 missing required field: name
  - Simulation 1 has invalid type: unknown_type
```

**Fix:** Check that all simulations have:
- `name` - Unique identifier
- `type` - One of: accc, ascc, cnv, snp, dynamic, dfx, dll, acc-pp
- `case` - Path to PSS/E case file

### Simulation Failed

```
[ERROR] Failed: Cannot find file: casos/caso.sav
```

**Fix:** Verify file paths are correct and relative to `workspace.base_dir`

### Dry Run to Debug

```bash
pssetools sim-runner --config config.yml --dry-run
```

Shows all commands that would be executed without actually running them.

---

## Integration with Version Control

**Recommended `.gitignore` entries:**

```
# Build artifacts
build/
log/
results/

# Compiled DLLs
lib/usrdll.dll

# Workspace runtime files
*.pdv
*.out
*.cnv
*.dfx

# Keep configuration files!
!config*.yml
!config*.json
```

**Keep these in version control:**

```
config_accc.yml
config_dynamic.yml
config_complete.yml
convload.py
dyn_*.py
estudio.*
```

---

## Migration from shell scripts

### Before (bash/PowerShell)

```bash
# script.sh (complex, platform-dependent)
./script.sh estatico
./script.sh dinamico
```

### After (Python)

```bash
# Single command, portable
pssetools sim-runner --config config.yml
```

---

## Future Enhancements

Planned features (not yet implemented):

- [ ] Parallel execution of independent simulations
- [ ] Result aggregation and report generation
- [ ] Advanced logging to file
- [ ] Retry logic for failed simulations
- [ ] Integration with CI/CD pipelines
- [ ] Web UI for configuration

---

## API Usage (For Developers)

```python
from pssetools.sim_runner import load_yaml_safe, validate_config, run_simulations

# Load configuration
config = load_yaml_safe('config.yml')

# Validate
valid, errors = validate_config(config)
if not valid:
    print("Errors:", errors)
    sys.exit(1)

# Execute
total, successful, failed = run_simulations(config)
print(f"Results: {successful}/{total} successful")
```

---

## References

- Configuration Examples: `pssetools/template/optional/examples/config_*.yml`
- PSS/E Documentation: `docs/psspy.txt`
- Full CLI: `pssetools --help`

