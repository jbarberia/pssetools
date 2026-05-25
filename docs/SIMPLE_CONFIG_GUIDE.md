# Simple Configuration Format Guide

## Overview

The **simple format** is a clean, organized way to define simulations grouped by study type. Instead of manually listing every simulation, you specify:
- Which cases (SAV files) to analyze
- Which study type (ACCC, ASCC, Dynamic)
- Shared configuration files (SUB, CON, MON scripts)

The system automatically expands this into all required simulations.

## Basic Structure

```yaml
workspace:
  base_dir: "."

accc:
  sav: [list of .sav files]
  sub: estudio.sub
  con: estudio.con
  mon: estudio.mon

ascc:
  sav: [list of .sav files]
  sub: estudio.sub

# dinamico:  (optional)
#   sav: [list of .sav files]
#   py: [list of .py control scripts]

execution:
  parallel_jobs: 1
  continue_on_error: false
```

## Study Type: ACCC (AC Contingency Analysis)

### What it does
- Runs contingency analysis on each SAV case
- Uses a SUB (contingency) file to specify contingencies
- Uses a CON (contingency output) file to configure reporting
- Uses a MON (monitor) file for real-time output

### Configuration

```yaml
accc:
  sav:
    - "caso1.sav"
    - "caso2.sav"
    - "caso3.sav"
  sub: "estudio.sub"        # Contingency definition
  con: "estudio.con"        # Contingency output config
  mon: "estudio.mon"        # Monitor output config
```

### Generated Simulations
Each SAV file generates **1 ACCC simulation**:
```
[1] ACCC_caso1
[2] ACCC_caso2
[3] ACCC_caso3
```

---

## Study Type: ASCC (AC Small Signal / Stability)

### What it does
- Analyzes system dynamic stability (eigenvalue analysis)
- Uses a SUB file for setup/switching actions
- No CON or MON needed (uses default reporting)

### Configuration

```yaml
ascc:
  sav:
    - "caso1.sav"
    - "caso2.sav"
  sub: "estudio.sub"        # Setup and switching
```

### Generated Simulations
Each SAV file generates **1 ASCC simulation**:
```
[1] ASCC_caso1
[2] ASCC_caso2
```

---

## Study Type: Dinámico (Dynamic Simulation)

### What it does
- Simulates dynamic system response (transient stability)
- Requires control scripts (Python files) that define events/actions
- Each (case, script) pair generates **3 sequential simulations**:
  1. **CNV** (Convert): Extract steady-state from SAV
  2. **SNP** (Snapshot): Build dynamic snapshot
  3. **DYN** (Dynamic): Run the dynamic simulation

### Configuration

```yaml
dinamico:
  sav:
    - "caso1.sav"
    - "caso2.sav"
  py:
    - "event1.py"
    - "event2.py"
```

### Generated Simulations
With N SAV files and M Python scripts: **N × M × 3 total simulations**

Example (2 cases × 2 scripts = 6 simulations):
```
[1] CNV_caso1_event1
[2] SNP_caso1_event1
[3] DYN_caso1_event1
[4] CNV_caso1_event2
[5] SNP_caso1_event2
[6] DYN_caso1_event2
[7] CNV_caso2_event1
[8] SNP_caso2_event1
[9] DYN_caso2_event1
[10] CNV_caso2_event2
[11] SNP_caso2_event2
[12] DYN_caso2_event2
```

---

## Complete Example

```yaml
workspace:
  base_dir: "."

# Static studies (AC Contingency + Small Signal)
accc:
  sav:
    - "inv25hr.sav"
    - "inv25pi.sav"
    - "inv25va.sav"
    - "ver2526pid.sav"
    - "ver2526pin.sav"
  sub: "estudio.sub"
  con: "estudio.con"
  mon: "estudio.mon"

ascc:
  sav:
    - "inv25hr.sav"
    - "inv25pi.sav"
  sub: "estudio.sub"

# Dynamic studies (Transient)
dinamico:
  sav:
    - "inv25hr.sav"
    - "inv25pi.sav"
    - "inv25va.sav"
  py:
    - "foo1.py"
    - "foo2.py"

execution:
  parallel_jobs: 2           # Run 2 simulations in parallel
  continue_on_error: false   # Stop on first error
  logging:
    level: "normal"

output:
  results_dir: "results"
  logs_dir: "logs"
  build_dir: "build"
```

### Total Simulations Generated
- **ACCC**: 5 simulations (1 per SAV)
- **ASCC**: 2 simulations (1 per SAV)
- **Dinámico**: 9 simulations (3 cases × 2 scripts × 3 phases)
- **Total**: 16 simulations

---

## Usage

### Validate configuration
```bash
pssetools sim-runner --config config.yml --validate
```

### Show summary
```bash
pssetools sim-runner --config config.yml --summary
```

### Run with dry-run (show commands without executing)
```bash
pssetools sim-runner --config config.yml --dry-run
```

### Run with 4 parallel workers
```bash
# Edit config.yml: execution: parallel_jobs: 4
pssetools sim-runner --config config.yml
```

---

## Common Patterns

### Single Case Analysis (Quick Test)
```yaml
accc:
  sav:
    - "test_case.sav"
  sub: "estudio.sub"
  con: "estudio.con"
  mon: "estudio.mon"
```
→ Generates 1 simulation

### Multi-Case Static Study (Many ACCC)
```yaml
accc:
  sav:
    - "case_a.sav"
    - "case_b.sav"
    - "case_c.sav"
    - "case_d.sav"
  sub: "full_network.sub"
  con: "full_network.con"
  mon: "full_network.mon"
```
→ Generates 4 simulations

### Multi-Script Dynamic Study
```yaml
dinamico:
  sav:
    - "base_case.sav"
  py:
    - "event_tripA.py"
    - "event_tripB.py"
    - "event_gen_loss.py"
```
→ Generates 9 simulations (1 case × 3 scripts × 3 phases)

### Combined Study (All Types)
```yaml
accc:
  sav: ["caso.sav"]
  sub: "estudio.sub"
  con: "estudio.con"
  mon: "estudio.mon"

ascc:
  sav: ["caso.sav"]
  sub: "estudio.sub"

dinamico:
  sav: ["caso.sav"]
  py: ["event.py"]
```
→ Generates 5 simulations (1 ACCC + 1 ASCC + 3 Dynamic)

---

## Advantages Over Standard Format

| Feature | Simple Format | Standard Format |
|---------|---------------|-----------------|
| Conciseness | ✓ Very compact | ✗ Lists every simulation |
| DRY (Don't Repeat Yourself) | ✓ No duplication | ✗ Much repetition |
| Multi-Case Easy | ✓ Just add to list | ✗ Must duplicate blocks |
| Readability | ✓ Study-type grouping | ✗ Long list of sims |
| Maintenance | ✓ Change file once | ✗ Change in many places |
| Explicit | ✗ Some magic | ✓ Every simulation visible |

---

## Notes

- **File paths**: Can be relative to `workspace.base_dir` or absolute
- **Windows paths**: Both `\` and `/` are supported; internally normalized
- **Parallel execution**: Respects dependencies within Dynamic (CNV→SNP→DYN must be sequential per combo)
- **Format detection**: Automatic - no need to specify; system detects simple vs standard format
- **Backward compatible**: Standard format still works unchanged

---

## Troubleshooting

### "Configuration must have 'simulations' section"
This error occurs if:
- YAML syntax is invalid (check indentation)
- No `accc`, `ascc`, or `dinamico` sections defined
- Format detection failed

**Solution**: Ensure at least one study type section is defined with proper YAML indentation.

### Dynamic simulations have long names
Naming convention: `{phase}_{case}_{script}`
- `CNV_inv25hr_foo1` = Convert phase, inv25hr.sav case, foo1.py script
- This is intentional for tracking and logging

### Parallel jobs don't improve performance for small configs
Dynamic studies (3 phases per combo) have inherent dependencies:
- CNV must complete before SNP
- SNP must complete before DYN
- Parallelization helps with multiple (case, script) combinations

For best results:
- Use parallel when you have 3+ different (sav, py) combinations
- For pure ACCC/ASCC, parallel is very effective

---

For more info, see:
- `README.md` - Project overview
- `SIM_RUNNER_GUIDE.md` - Detailed sim-runner documentation
- `PARAMETRIZATION_GUIDE.md` - Advanced config techniques
