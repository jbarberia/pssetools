# Configuration Guide

The `config.cfg` file (INI format) defines default parameters for all PSS/E activities. You can override these defaults by passing a custom `.cfg` file via the `--config` CLI flag.

## Sections

### [ACC] - Contingency Analysis (ACCC)
Controls the behavior of the `acc` and `acc-pp` commands.

- **ACTIVITY:** The PSS/E ACCC activity name.
  - `"ACCC_WITH_DSP_3"`: Standard ACCC with dispatch.
  - `"ACCC_PARALLEL_2"`: ACCC using parallel processing.
- **TOLN:** MW tolerance for convergence.
- **OPTACC[1-11]:** Solution and model flags.
  - `OPTACC1`: Tap flag (0: disable, 1: step, 2: direct).
  - `OPTACC5`: Switched shunt flag (0: disable, 1: enable, 2: continuous).
  - `OPTACC6`: Solution method (1: FNSL).
  - `OPTACC10`: Dispatch mode (0: disable, 1: enable).
  - `OPTACC11`: ZIP report (0: disable, 1: enable).
- **OPTCOR[1-8]:** Corrective action settings (e.g., `OPTCOR1` to enable/disable).
- **VALUES[1-8]:** Violation tolerances and control weights.
  - `VALUES1`: Bus voltage violation tolerance (p.u.).
  - `VALUES2`: Branch flow violation tolerance (p.u.).
- **LABELS[1-7]:** Subsystem names for specific controls (e.g., `LABELS2` for generator control subsystem).

### [ASCC] - Short Circuit Analysis
Controls the `ascc` command.

- **FLT3PH, FLTLG, FLTLL, FLTLLG:** Flags (0/1) to enable 3-Phase, Line-to-Ground, Line-to-Line, and Line-to-Line-to-Ground faults.
- **VOLTOP:** Voltage source option (0: Use bus voltage solution; 2: set at `VOLTS`).
- **GENXOP:** Generator reactance option (0: X'', 1: X', 2: X).
- **VOLTS:** Specified bus voltage for fixed source (e.g., `1.0`).
- **DCLOAD:** DC load representation (0: Blocked, 1: Represent as load).

### [ARRBOX] - Reports and Formatting
Controls report formatting in post-processing tools.

- **RATING:** Default rating level for flow reports (`"a"`, `"b"`, or `"c"`).
- **NUMFMT_FLOW:** Python format string for flows (e.g., `"%%.0f"`). Note the double `%` for INI escaping.
- **NUMFMT_VOLT:** Python format string for voltages (e.g., `"%%.4f"`).

### [DLL] - User Model Compilation
Paths for the compilation environment (Intel oneAPI and MSVC).

- **PATH:** List of directories for compiler binaries.
- **LIB:** List of directories for static libraries.
- **INCLUDE:** List of directories for header files.

## Customizing Configuration
Create a new file (e.g., `my_study.cfg`) and override only the values you need:

```ini
[ACC]
ACTIVITY = "ACCC_PARALLEL_2"
TOLN = 10
OPTACC5 = 1  # Enable Switched Shunts

[ARRBOX]
RATING = "b"
```

Then run the tool with the `--config` flag:
```bash
pssetools acc case.sav estudio.sub estudio.mon estudio.con --config my_study.cfg
```
