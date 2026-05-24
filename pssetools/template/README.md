# PSS/E Tools - Template Files

This directory contains template files and examples for pssetools workspaces.

## Structure

### `essential/` - Required Configuration Files
These files are **always** copied during `pssetools setup`:

- **`config.cfg`** - Main configuration for all analyses
  - ACCC options (tap control, area interchange, phase shift, etc.)
  - ASCC short circuit analysis parameters
  - DLL compiler paths (Intel oneAPI, MSVC, Windows Kits)

- **`estudio.sub`** - PSS/E Subsystem definition
  - Defines which buses/branches are included in the study area
  - Used by ACCC and ASCC analyses
  - In ASCC look for CORTOCIRCUITO subsystem

- **`estudio.mon`** - PSS/E Monitor points definition
  - Specifies which buses are monitored for voltage violations
  - Used during contingency analysis

- **`estudio.con`** - PSS/E Contingency list
  - Defines single-line-to-ground and three-phase faults
  - Contingencies to analyze in ACCC

- **`estudio.idv`** - PSS/E Channel/Channel list
  - Defines which signals are recorded during dynamic simulations
  - Includes generator outputs, bus voltages, line flows

### `optional/examples/` - Example Python Scripts
Optional scripts copied only if needed:

- **`convload.py`** - Case conversion helper
  - Custom load and generator model for case conversion
  - Used with `pssetools cnv` for dynamic simulation setup

- **`dyn_1ph.py`** - Single-phase fault event script
  - Example of a one-phase-to-ground fault event
  - Template for custom dynamic simulation scenarios

- **`dyn_3ph.py`** - Three-phase fault event script
  - Example of a three-phase fault event
  - Template for custom transient stability studies

### `optional/scripts/` - Automation Scripts
Shell and PowerShell batch processing templates:

- **`script.sh`** - Bash/Shell automation (Linux/macOS)
  - Parallel ACCC processing
  - Short circuit batch analysis
  - Dynamic simulation orchestration
  - Interactive menu for study selection

- **`script.ps1`** - PowerShell automation (Windows)
  - Same workflows as script.sh
  - Native Windows PowerShell functions
  - Progress bars and parallel execution

### `docs/` - PSS/E API Reference
Reference documentation (copied only if needed):

- `psspy.txt` - PSS/E Python API methods
- `pssarrays.txt` - Array input/output specifications
- `dyntools.txt` - Dynamic simulation tools documentation
- `pssras.txt` - PSS/E RAS (Remedial Action Scheme) functions
- `sliderPy.txt` - Slider diagram Python interface

### Other Files

- **`GEMINI.md`** - Workspace governance document
  - Describes standard workspace structure
  - Engineering standards and best practices
  - Core workflows (static, short circuit, dynamic)

## Setup Wizard Flow

When you run `pssetools setup`, the wizard will:

1. ✓ **Create** workspace folders: `lib/`, `log/`, `build/`, `results/`
2. ✓ **Copy essential files** automatically
3. ❓ **Ask** what analyses you'll run (ACCC, ASCC, Dynamic, or all)
4. ❓ **Ask** if you want example scripts and documentation
5. ✓ **Copy** only the files you selected

## Usage Examples

### For Static Contingency Analysis Only
```bash
$ pssetools setup
# Select: "1) ACCC (Contingency Analysis)"
# Answer "n" to examples and scripts
```

### For Dynamic Simulation Study
```bash
$ pssetools setup
# Select: "3) Dynamic Simulation"
# Answer "y" to include example scripts
# Answer "y" to include documentation (if first time)
```

### For Complete Power System Study
```bash
$ pssetools setup
# Select: "4) All of the above"
# Answer "y" to both examples and scripts
```

## Customization

After setup, you can:

1. **Edit `config.cfg`** to adjust ACCC/ASCC analysis parameters
2. **Edit `estudio.sub/mon/con`** to define your study area
3. **Copy additional scripts** from `optional/examples/` or `optional/scripts/` manually
4. **Reference `docs/`** when writing custom Python automation

## File Descriptions in Detail

### config.cfg
Main configuration file with sections:
- `[ACC]` - ACCC (AC Contingency Analysis) settings
- `[ASCC]` - ASCC (Short Circuit Analysis) settings
- `[ARRBOX]` - Array/report formatting
- `[DLL]` - Compiler paths for user model compilation

### estudio.* Files
Standard PSS/E file formats:
- `.sub` - Subsystem definition (text format)
- `.mon` - Monitor points definition
- `.con` - Contingency list
- `.idv` - Monitored channels/variables list

### Python Example Scripts

All Python scripts are **Python 2.7 compatible** (PSS/E 34 requirement).

**`convload.py`**:
```python
# Custom case conversion logic
# Modify load and generator models before dynamic simulation
```

**`dyn_1ph.py` and `dyn_3ph.py`**:
```python
# Dynamic event scripts
# Structure: fault -> measurement period -> clear -> recovery
```

## More Information

- Full documentation: `pssetools --help`
- Configuration guide: Edit `config.cfg` with comments
- Quick reference: See `GEMINI.md` in workspace root

