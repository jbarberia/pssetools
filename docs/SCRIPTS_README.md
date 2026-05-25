# Simulation Runner Scripts

This folder contains interactive scripts to run PSS/E simulations with easy-to-use menus.

## Available Scripts

### Windows Batch Script
**File:** `run_simulations.bat`

**Usage:**
```cmd
run_simulations.bat
```

**Features:**
- ✅ Interactive menu to select configuration files
- ✅ Choose execution mode (validate, dry-run, normal, interactive)
- ✅ Auto-detects available .yml config files
- ✅ Color-coded output
- ✅ Error handling and validation

**Requirements:**
- Python 3.x installed and in PATH
- pssetools installed (`pip install -e .`)

**Example:**
```
C:\project> run_simulations.bat

================================================================================
                   PSS/E SIMULATION RUNNER - Interactive Menu
================================================================================

[*] Available configurations:

  [1] ACCC Parallel (2 workers)
  [2] Full Parallel Mixed Studies (4 workers)
  [3] Default (config.yaml)
  [4] ACCC Sequential
  [5] Dynamic Sequential
  [0] Exit

Select configuration (0-5): 1

[OK] Selected: config_accc_parallel.yml

[*] Execution Mode:
  [1] Validate only (check configuration without running)
  [2] Dry run (show commands but don't execute)
  [3] Normal execution
  [4] Interactive (ask for each)

Select mode (1-4) [3]: 3
Mode: Normal execution

[*] Running simulation...
```

---

### PowerShell Script
**File:** `run_simulations.ps1`

**Usage (Interactive Mode):**
```powershell
.\run_simulations.ps1
```

**Usage (Command Line Mode):**
```powershell
.\run_simulations.ps1 -Config config_accc_parallel.yml -DryRun
.\run_simulations.ps1 -Config config.yaml -Validate
.\run_simulations.ps1 -Config config.yaml -Interactive
```

**Available Options:**
- `-Config <file>` - Specify configuration file directly
- `-Validate` - Validate only (no execution)
- `-DryRun` - Show commands but don't execute
- `-Interactive` - Ask before each simulation
- `-Help` - Show help message

**Features:**
- ✅ Interactive menu or command-line arguments
- ✅ Auto-discover available configs
- ✅ Color-coded output
- ✅ Cross-platform (PowerShell 5.0+)
- ✅ Professional error messages

**Requirements:**
- PowerShell 5.0 or higher
- Python 3.x installed and in PATH
- pssetools installed (`pip install -e .`)

**Example - Interactive Mode:**
```powershell
PS C:\project> .\run_simulations.ps1

================================================================================
         PSS/E Simulation Runner - Interactive Menu
================================================================================

[*] Available configurations:

  [1] ACCC Parallel (2 workers)
  [2] Full Parallel Mixed Studies (4 workers)
  [3] Default (config.yaml)

Select configuration (0-3): 1

[OK] Selected: config_accc_parallel.yml

[*] Execution Mode:
  [1] Validate only
  [2] Dry run
  [3] Normal execution
  [4] Interactive

Select mode (1-4) [3]: 2
Mode: Dry run (no execution)
...
```

**Example - Command Line Mode:**
```powershell
# Validate before running
PS C:\project> .\run_simulations.ps1 -Config config_accc_parallel.yml -Validate

# Preview commands without executing
PS C:\project> .\run_simulations.ps1 -Config config.yaml -DryRun

# Run in interactive mode
PS C:\project> .\run_simulations.ps1 -Config config.yaml -Interactive

# Show help
PS C:\project> .\run_simulations.ps1 -Help
```

---

## Recommended Workflow

### Step 1: Validate Configuration
```bash
# Batch
run_simulations.bat
# Select config [1], mode [1] (Validate)

# PowerShell
.\run_simulations.ps1 -Config config_accc_parallel.yml -Validate
```

### Step 2: Preview Commands (Dry-Run)
```bash
# Batch
run_simulations.bat
# Select config [1], mode [2] (Dry run)

# PowerShell
.\run_simulations.ps1 -Config config_accc_parallel.yml -DryRun
```

### Step 3: Execute
```bash
# Batch
run_simulations.bat
# Select config [1], mode [3] (Normal)

# PowerShell
.\run_simulations.ps1 -Config config_accc_parallel.yml
```

---

## Configuration Files Location

The scripts look for `.yml` configuration files in the **current directory**. Common locations:

```
project/
├── config_accc_parallel.yml    ← Scripts find this
├── config.yaml                 ← Scripts find this
├── run_simulations.bat         ← Run from here
├── run_simulations.ps1         ← Run from here
└── simulations/
    ├── config_accc.yml         ← Won't be found (not in current dir)
```

**To use configs in subdirectories:**
1. Copy them to the project root, OR
2. Edit the script to add the subfolder path

---

## Troubleshooting

### Script won't run (Batch)
```
Error: 'run_simulations.bat' is not recognized as an internal or external command
```

**Solution:**
- Run from the directory containing `run_simulations.bat`
- Or use full path: `C:\project\run_simulations.bat`

### Script won't run (PowerShell)
```
cannot be loaded because running scripts is disabled on this system
```

**Solution - Enable script execution (one-time):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Configuration file not found
```
[ERROR] Configuration file not found: config.yml
```

**Solution:**
- Check file exists in current directory: `dir config*.yml`
- Edit script to add correct path
- Copy config file to project root

### Python not found
```
[ERROR] Python is not installed or not in PATH
```

**Solution:**
- Install Python 3.x: https://www.python.org/downloads/
- Add Python to PATH (select during installation)
- Verify: `python --version`

### pssetools not found
```
[ERROR] Failed to install pssetools
```

**Solution:**
- Install pssetools in development mode:
  ```bash
  cd C:\path\to\pssetools
  pip install -e .
  ```
- Verify: `python -m pssetools --help`

---

## Extending the Scripts

### Add a New Configuration

1. Create your config file (e.g., `config_custom.yml`)
2. Place in the same directory as the script
3. Run the script - it will auto-detect the new config

The script automatically discovers all `.yml` files in the current directory.

### Create a Shortcut (Windows)

1. Right-click `run_simulations.bat` → Create shortcut
2. Right-click shortcut → Properties
3. In "Start in", set to your project directory
4. Save and double-click to use

---

## Integration with CI/CD

### GitHub Actions / Azure Pipelines

```yaml
- name: Run PSS/E Simulations
  run: python -m pssetools sim-runner --config config_accc_parallel.yml --continue-on-error
```

### Local Development

For frequent testing, create a shortcut or alias:

```bash
# Bash
alias run_sims='python -m pssetools sim-runner --config config_accc_parallel.yml'
run_sims

# PowerShell
Set-Alias run_sims {.\run_simulations.ps1 -Config config_accc_parallel.yml}
run_sims
```

---

## More Information

- `docs/SIM_RUNNER_GUIDE.md` - Detailed configuration documentation
- `docs/PARAMETRIZATION_GUIDE.md` - Advanced config patterns
- `pssetools/template/optional/examples/PARALLELIZATION_GUIDE.md` - Parallel execution tips
