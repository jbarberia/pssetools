# pssetools

**pssetools** is a command-line interface (CLI) and GUI utility for automating PSS/E (v34) activities, including ACCC, ASCC, dynamic simulations, and user model DLL compilation. It simplifies complex PSS/E workflows by providing a modern interface and automatic file assignment.

## Features
- **ACCC Contingency Analysis:** Run and post-process contingency results with support for parallel execution.
- **ASCC Short Circuit:** Automate short circuit reports for various fault types (3PH, LG, LL, LLG).
- **Dynamic Simulation:** Manage snapshots (.snp), converted cases (.cnv), and time-domain runs with custom event scripts.
- **User DLLs:** Compile user models using PSSE environment tools (Intel oneAPI, MSVC).
- **Auto-assignment:** Automatically detects and assigns input files based on their extensions (.sav, .dyr, .sub, etc.).
- **Configuration Wizard (GUI):** Generate subsystem (.sub), monitor (.mon), contingency (.con), and channel (.idv) files directly from PSS/E SLD diagrams.
- **Workspace Setup:** Initialize a standard project structure with templates and folder organization.

## Prerequisites
- **Python:** 2.7 (required for PSS/E 34 compatibility).
- **PSS/E:** Version 34 must be installed and in the system PATH.
- **Dependencies:** `pandas`, `Tkinter` (included in standard Python 2.7).

## Installation

### For Users
Install the package directly from the repository:
```bash
git clone https://github.com/User/pssetools.git
cd pssetools
make install
```


## Quick Start (CLI)

### 1. Initialize Workspace
Create the standard folder structure (`build/`, `log/`, `results/`) and copy templates:
```bash
pssetools setup
```

### 2. ACCC Analysis
Run ACCC and post-process results into reports:
```bash
# Run ACCC
pssetools acc case.sav estudio.sub estudio.mon estudio.con --acc results.acc

# Post-process to CSV reports
pssetools acc-pp results.acc --frp flow_report.csv --vrp volt_report.csv
```

### 3. Short Circuit
```bash
pssetools ascc --sav case.sav --sub estudio.sub --report fault_study.scf
```

### 4. Dynamic Simulation
Build a snapshot and run a simulation with a custom event script:
```bash
# Create Snapshot
pssetools snp --sav case.sav --dyr data.dyr --snp snapshot.snp

# Run simulation
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
Activities are controlled via `config.cfg`. You can specify a custom config file using the `--config` flag to override defaults.

```bash
pssetools acc case.sav --config custom_settings.cfg
```

## Documentation
- [Configuration Guide](docs/CONFIG_GUIDE.md)
- [Contributing](CONTRIBUTING.md)
