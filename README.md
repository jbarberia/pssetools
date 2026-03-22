# pssetools

**pssetools** is a command-line interface (CLI) and GUI utility for automating PSS/E (v34) activities, including ACCC, ASCC, dynamic simulations, and user model DLL compilation.

## Features
- **ACCC Contingency Analysis:** Run and post-process contingency results.
- **ASCC Short Circuit:** Automate short circuit reports.
- **Dynamic Simulation:** Manage snapshots, converted cases, and time-domain runs.
- **User DLLs:** Compile user models using PSSE environment tools.
- **Configuration Wizard (GUI):** Generate subsystem, monitor, contingency, and channel files directly from PSS/E SLD diagrams.

## Prerequisites
- **Python:** 2.7 (required for PSS/E 34 compatibility).
- **PSS/E:** Version 34 must be installed and in the system PATH.
- **Dependencies:** `pandas`, `Tkinter` (included in standard Python 2.7).

## Installation
Clone the repository and install the package in develop mode:
```bash
git clone https://github.com/User/pssetools.git
cd pssetools
python setup.py develop
```

## Quick Start (CLI)

### 1. ACCC Analysis
```bash
pssetools acc --sav case.sav --sub estudio.sub --mon estudio.mon --con estudio.con --acc results.acc
```

### 2. Short Circuit
```bash
pssetools ascc --sav case.sav --sub estudio.sub --report results.scf
```

### 3. Dynamic Simulation
```bash
pssetools dyn --cnv case.cnv --snp snapshot.snp --out results.out --py event.py
```

## GUI Configuration Wizard
The GUI allows you to select elements in a PSS/E SLD (Slider) and automatically generate the necessary configuration files.

**To launch the GUI:**
```bash
pssetools gui
```
- **Tabs:** Manage `.sub`, `.mon`, `.con`, and `.idv` (channels) separately.
- **Shortcuts:**
  - `Ctrl+S`: Save current tab.
  - `Ctrl+Shift+S`: Save all tabs with a base name.
  - `Ctrl+Tab`: Switch tabs.
  - `Alt+1`: Generate content from selected SLD elements.

## Configuration
Activities are controlled via `config.cfg`. You can specify a custom config file using the `--config` flag.

## Documentation
- [Configuration Guide](docs/CONFIG_GUIDE.md)
- [Contributing](CONTRIBUTING.md)
