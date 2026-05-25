# PSS/E Workspace Mandates

This workspace is managed using `pssetools`. You are acting as a senior power systems engineer automating PSS/E workflows.

**Created with:** `pssetools setup` wizard

## 📁 Workspace Structure

```
.
├── lib/              # User-compiled DLLs and shared libraries
├── log/              # Activity logs, progress files (.pdv, .log)
├── build/            # Temporary analysis files (.dfx, .acc, .cnv, .snp)
├── results/          # Final reports and simulation output (.out, .csv, .tsv)
├── *.sav             # PSS/E case files (Static steady-state)
├── *.dyr             # Dynamic data files
├── *.py              # Support scripts (convload, dyn_*, custom automation)
├── estudio.sub       # PSS/E subsystem definition
├── estudio.mon       # Monitor points (voltage checks)
├── estudio.con       # Contingency list
├── estudio.idv       # Channel definitions for dynamic simulations
├── config.cfg        # Main configuration file
├── script.sh         # Bash/Shell batch automation (optional)
├── script.ps1        # PowerShell batch automation (optional)
└── docs/             # PSS/E API reference (optional)
```

## 🔧 Configuration Files

### `config.cfg`
Main configuration with sections:
- **`[ACC]`** - ACCC (AC Contingency Analysis) settings
  - Control options (tap, area interchange, phase shift, etc.)
  - Solution method and dispatch mode
  - Corrective action parameters
- **`[ASCC]`** - ASCC (Short Circuit) settings
  - Fault types (3PH, LG, LL, LLG)
  - Voltage and impedance options
- **`[ARRBOX]`** - Array formatting for reports
- **`[DLL]`** - Compiler paths for user model compilation

### PSS/E Study Files (estudio.*)
Standard PSS/E file formats (text-based):
- **`estudio.sub`** - Defines study area (buses, branches, generators)
- **`estudio.mon`** - Specifies monitored buses for violations
- **`estudio.con`** - List of contingencies to analyze
- **`estudio.idv`** - Channels to record during dynamic simulations

## 🔄 Core Workflows

### 1️⃣ Static Contingency Analysis (ACCC)

**Goal:** Identify and analyze line/generator outages impacting the system.

**Workflow:**
```bash
# Step 1: Create DFX (transient stability program file)
pssetools dfx --sav CASE.sav --sub estudio.sub --mon estudio.mon --con estudio.con --dfx build/CASE.dfx

# Step 2: Run ACCC analysis (generates results)
pssetools acc --sav CASE.sav --dfx build/CASE.dfx --acc build/CASE.acc --zip build/CASE.zip

# Step 3: Extract results to CSV reports
pssetools acc-pp --acc build/CASE.acc --frp build/CASE.frp --vrp build/CASE.vrp

# Step 4: Extract contingency details
pssetools acc-unzip --zipfile build/CASE.zip --folder results/CASE
```

**Output:**
- `build/CASE.frp` - Flow violation report
- `build/CASE.vrp` - Voltage violation report
- `results/CASE/` - Detailed contingency results

---

### 2️⃣ Short Circuit Analysis (ASCC)

**Goal:** Calculate fault levels (3PH, LG, LL, LLG) at specified buses.

**Workflow:**
```bash
# Run short circuit analysis
pssetools ascc --sav CASE.sav --sub estudio.sub --report build/CASE.scf
```

**Output:**
- `build/CASE.scf` - Short circuit report (tab-separated)

---

### 3️⃣ Dynamic Simulation

**Goal:** Run time-domain transient stability studies with user models.

**Workflow:**
```bash
# Step 1: Convert case (apply custom loads/generators)
pssetools cnv --sav CASE.sav --cnv build/CASE.cnv --py convload.py

# Step 2: Create snapshot (build transient model)
pssetools snp --sav CASE.sav --snp build/snapshot.snp --dyr DATA.dyr --idv estudio.idv

# Step 3: Compile user DLL (if needed)
pssetools dll --sources build/cc.flx build/ct.flx lib/*.lib --dll lib/usrdll.dll

# Step 4: Run simulation with event script
pssetools dyn --cnv build/CASE.cnv --snp build/snapshot.snp --out results/CASE_event.out \
    --dll lib/*.dll --py dyn_event.py
```

**Output:**
- `build/CASE.cnv` - Converted case file
- `build/snapshot.snp` - Transient stability snapshot
- `results/CASE_event.out` - Simulation results
- `results/CASE_event.llt` - Event log (channel values)

---

## 🛠️ Automation Scripts (Optional)

### `script.sh` (Linux/macOS)
Batch processing with menu interface:
```bash
./script.sh estatico      # Run all ACCC analyses
./script.sh cortocircuito  # Run all ASCC analyses
./script.sh dinamico      # Run all dynamic simulations
./script.sh clean         # Clean all temporary files
```

### `script.ps1` (Windows PowerShell)
Native Windows automation:
```powershell
.\script.ps1
# Presents interactive menu for study selection
```

---

## 📋 Engineering Standards

### Python Compatibility
- **All scripts must support Python 2.7** (PSS/E 34 requirement)
- Avoid Python 3-only syntax (f-strings, type hints, async)

### File Paths
- Use relative paths: `build/`, `log/`, `results/`
- Avoid hardcoded absolute paths
- Use forward slashes in Python, backslashes only in PowerShell

### Dynamic Event Scripts (dyn_*.py)
Ensure proper sequence in `psspy.run()` calls:
1. **Apply fault** (short circuit on bus)
2. **Measure/record** system response
3. **Clear fault** (open breakers)
4. **Observe recovery** (damping, stability)

Example structure:
```python
psspy.run(0, END_TIME, NPR, 1, 0, 0)  # Run to fault application
psspy.run(fault_time, END_TIME, NPR, 0, 0, 0)  # Run to fault clear
psspy.run(END_TIME, END_TIME, NPR, 0, 0, 0)  # Run to end (recovery)
```

### Configuration Management
- Edit `config.cfg` carefully (TOLN, options, paths)
- Test with small case first
- Keep version control of successful configs

---

## 🧹 Maintenance

### Cleaning Temporary Files
```bash
# Clean all build artifacts
pssetools setup   # Creates fresh lib/, log/, build/, results/

# Or use scripts
./script.sh clean      # Bash
.\script.ps1           # PowerShell (select "6) limpia todo")
```

### Recommended Workflow
1. Keep `.sav`, `.dyr`, `*.py` scripts in version control
2. Ignore: `build/`, `log/`, `results/`, `lib/usrdll.dll`
3. Track: `config.cfg`, `estudio.*`, `convload.py`, `dyn_*.py`

---

## 📚 Documentation

- **PSS/E API Methods:** `docs/psspy.txt`
- **Array I/O Formats:** `docs/pssarrays.txt`
- **Dynamic Simulation:** `docs/dyntools.txt`
- **Remedial Actions:** `docs/pssras.txt`
- **Slider Diagram:** `docs/sliderPy.txt`

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Contingency Analysis | `pssetools acc --help` |
| Short Circuit | `pssetools ascc --help` |
| Dynamic Simulation | `pssetools dyn --help` |
| View all commands | `pssetools --help` |

---

## ⚡ Performance Tips

- **Parallel Execution:** Use `script.sh` or `script.ps1` for batch jobs
- **DLL Compilation:** Pre-compile and cache `lib/usrdll.dll`
- **Case Conversion:** Run once, reuse `.cnv` file
- **Monitor Selection:** Limit to relevant buses to reduce file size

---

## 🆘 Common Issues

**Issue:** DLL compilation fails  
→ Check `config.cfg` [DLL] paths for Intel oneAPI, MSVC, Windows Kits

**Issue:** ACCC convergence failure  
→ Verify `estudio.sub` includes all critical generators/loads  
→ Adjust `config.cfg` [ACC] solution options

**Issue:** Dynamic simulation crashes  
→ Verify `convload.py` applies valid load/generator models  
→ Check `dyn_*.py` event sequencing

---

Created with `pssetools setup` - Power Systems Engineering Automation Tool

