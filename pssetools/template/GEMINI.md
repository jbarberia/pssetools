# PSS/E Workspace Mandates

This workspace is managed using `pssetools`. You are acting as a senior power systems engineer automating PSS/E workflows.

## Workspace Structure
- `*.sav`: PSS/E case files (Static).
- `*.dyr`: Dynamic data files.
- `*.py`: Support scripts (e.g., `convload.py` for case conversion, `dyn_*.py` for simulation events).
- `estudio.sub/mon/con`: PSS/E subsystem, monitor, and contingency definitions.
- `build/`: Temporary files (.dfx, .acc, .cnv, .snp).
- `log/`: Activity logs and progress output (.pdv).
- `results/`: Final reports and simulation output (.out).
- `lib/`: User DLLs and libraries.

## Documentation
- `docs/`: Contains PSS/E API documentation (e.g., `psspy.txt`, `pssarrays.txt`, `dyntools.txt`). Refer to these files when building custom automation scripts.

## Core Workflows

### 1. Static Analysis (ACCC)
- **Goal:** Run contingency analysis and extract results.
- **Workflow:** 
    1. Build DFX: `pssetools dfx --sav [CASE].sav --sub estudio.sub --mon estudio.mon --con estudio.con --dfx build/[CASE].dfx`
    2. Run ACC: `pssetools acc --sav [CASE].sav --dfx build/[CASE].dfx --acc build/[CASE].acc`
    3. Post-process: `pssetools acc-pp --acc build/[CASE].acc --frp build/[CASE].frp --vrp build/[CASE].vrp`

### 2. Short Circuit (ASCC)
- **Goal:** Calculate fault levels at specified buses.
- **Workflow:** `pssetools ascc --sav [CASE].sav --sub estudio.sub --report build/[CASE].scf`

### 3. Dynamic Simulation
- **Goal:** Run time-domain simulations with user models.
- **Workflow:**
    1. **Convert Case:** `pssetools cnv --sav [CASE].sav --cnv build/[CASE].cnv --py convload.py`
    2. **Build Snapshot:** `pssetools snp --sav [CASE].sav --snp build/snapshot.snp --dyr [DATA].dyr --cc build/cc.flx --ct build/ct.flx`
    3. **Compile DLL (if needed):** `pssetools dll --sources build/cc.flx build/ct.flx lib/*.lib --dll lib/usrdll.dll`
    4. **Run Simulation:** `pssetools dyn --cnv build/[CASE].cnv --snp build/snapshot.snp --out results/[NAME].out --dll lib/*.dll --py dyn_event.py`

## Engineering Standards
- **Python Compatibility:** All scripts must be compatible with Python 2.7 as they interact with PSS/E 34.
- **Pathing:** Use relative paths or the `build/`, `log/`, `results/` structure defined in `script.sh`.
- **Validation:** When modifying `dyn_*.py` scripts, ensure `psspy.run` calls are sequenced correctly (fault, clear, recovery).
- **Configuration:** Preferences for ACCC and ASCC should be modified in `config.cfg`.


## Automation
The `script.sh` file provides a high-level wrapper. Prefer using the CLI `pssetools` directly for surgical operations or debugging, and `script.sh` for batch processing.


## pssetools runner
The python script shuld import psse34 before psspy and output the relevant information with the psspy.report function


