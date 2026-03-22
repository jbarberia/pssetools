# Configuration Guide

The `config.cfg` file (INI format) defines default parameters for all PSS/E activities. You can override these defaults by passing a custom `.cfg` file via the `--config` CLI flag.

## Sections

### [ACC] - Contingency Analysis (ACCC)
- **ACTIVITY:** The PSS/E ACCC activity name (e.g., `ACCC_WITH_DSP_3`, `ACCC_PARALLEL_2`).
- **TOLN:** MW tolerance for convergence.
- **OPTACC[1-11]:** Solution and model flags.
  - `OPTACC1`: Tap flag (0: disable, 1: step, 2: direct).
  - `OPTACC6`: Solution method (1: FNSL).
  - `OPTACC11`: ZIP report (0: disable, 1: enable).
- **OPTCOR[1-8]:** Corrective action settings.
- **VALUES[1-8]:** Violation tolerances (voltage, flow) and control weights.
- **LABELS[1-7]:** Subsystem names for control (generator, load, etc.).

### [ASCC] - Short Circuit Analysis
- **FLT3PH, FLTLG, FLTLLG, FLTLL:** Flags (0/1) to enable specific fault types.
- **VOLTOP:** Voltage source option (0: solution, 2: set at `VOLTS`).
- **GENXOP:** Generator reactance option (0: X'', 1: X', 2: X).
- **VOLTS:** Voltage magnitude for fixed source.

### [ARRBOX] - Reports and Formatting
- **RATING:** Default rating level for flow reports ("a", "b", or "c").
- **NUMFMT_FLOW:** Python format string for flows (e.g., `%.0f`).
- **NUMFMT_VOLT:** Python format string for voltages (e.g., `%.4f`).

### [DLL] - User Model Compilation
- **PATH:** List of directories for the C/Fortran compiler (Intel oneAPI, MSVC).
- **LIB:** List of directories for static libraries and SDKs.
- **INCLUDE:** List of directories for header and include files.

## Example Custom Config
```ini
[ACC]
ACTIVITY = "ACCC_PARALLEL_2"
TOLN = 10
OPTACC5 = 1  # Switched Shunts Enable

[ARRBOX]
RATING = "b"
```
