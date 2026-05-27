# PSS/E Workspace Mandates (LLM Guide)

You are acting as a senior power systems engineer. This workspace is automated using `pssetools` and a `Makefile`.

## 📁 Workspace Structure

- `src/`: **Source Files.** Contains `.sav`, `.dyr`, `config.cfg`, and study files (`estudio.sub`, `.mon`, `.con`, `.idv`).
- `build/`: **Intermediate Artifacts.** Files like `.dfx`, `.acc`, `.cnv`, `.snp`. (Auto-generated).
- `results/`: **Output Reports.** Final reports (`.frp`, `.vrp`, `.scf`, `.out`).
- `log/`: **Execution Logs.** Detailed logs for every command run via Makefile.
- `Makefile`: **Orchestration.** Use this as the primary entry point for studies.

## 🚀 Automation (Makefile Targets)

Instead of running raw `pssetools` commands, prefer using `make`:

| Target | Description | Output Location |
|:-------|:------------|:----------------|
| `make estatico` | AC Contingency Analysis (ACCC) | `results/*.frp`, `results/*.vrp` |
| `make cortocircuito` | Short Circuit Analysis (ASCC) | `results/*.scf` |
| `make dinamico` | Transient Stability Simulations | `results/dyn_*/` |
| `make dll` | Compiles user models into DLL | `src/dsurs.dll` |
| `make clean` | Wipes build, results, and logs | - |

## 🛠️ Raw Command Reference

If you need granular control, use the `pssetools` CLI:

### 1. Static Analysis (ACCC)
```bash
# 1. Create DFX
pssetools dfx src/CASE.sav src/estudio.sub src/estudio.mon src/estudio.con --dfx build/CASE.dfx
# 2. Run ACC
pssetools acc src/CASE.sav --dfx build/CASE.dfx --acc build/CASE.acc --zipfile results/CASE.zip
# 3. Process Reports
pssetools acc-pp --acc build/CASE.acc --frp results/CASE.frp --vrp results/CASE.vrp
```

### 2. Short Circuit (ASCC)
```bash
pssetools ascc src/CASE.sav src/estudio.sub --report results/CASE.scf --config src/config.cfg
```

### 3. Dynamic Simulation
```bash
# 1. Convert Case
pssetools cnv src/CASE.sav --cnv build/CASE.cnv --py src/convload.py
# 2. Create Snapshot
pssetools snp src/CASE.sav --snp build/CASE.snp --idv src/estudio.idv --dyr src/*.dyr
# 3. Run Simulation
pssetools dyn --cnv build/CASE.cnv --snp build/CASE.snp --out results/CASE.out --py src/EVENT.py
```

## 📋 Engineering Standards for LLMs

1. **Python 2.7 Compatibility:** PSS/E 34 requires Python 2.7. Do NOT use f-strings, type hints, or `pathlib`.
2. **Path Handling:** Always use forward slashes `/` in Python scripts for cross-platform compatibility.
3. **Configuration:** Check `src/config.cfg` before running studies to ensure solution parameters (TOLN, etc.) are correct.
4. **Log Review:** If a `make` command fails, always check the corresponding log in `log/*.log` before attempting a fix.
5. **Batch Processing:** The Makefile automatically processes ALL `.sav` files in `src/`. To run a specific case, you can use `make build/CASE.acc`.

## 📚 API Reference (Internal Docs)
- `docs/psspy.txt`: Full PSS/E API documentation.
- `docs/dyntools.txt`: Tools for dynamic simulation results.
- `docs/pssarrays.txt`: Low-level data access.
