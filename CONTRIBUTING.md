# Contributing to pssetools

Thank you for your interest in improving **pssetools**! We welcome contributions to add new PSS/E activities, improve the CLI, or enhance the GUI.

## Developer Setup
1. **Clone and install:**
   ```bash
   git clone https://github.com/User/pssetools.git
   cd pssetools
   python setup.py develop
   ```
2. **Standard:** Use Python 2.7 (compatible with PSS/E 34).
3. **Docstrings:** All new functions must follow the **Google Style**.

## Adding a New Activity
To add a new PSS/E activity (e.g., OPF, GIC):
1. Create a new module in `pssetools/` (e.g., `pssetools/opf.py`).
2. Implement a `run` function decorated with `@pss_activity`.
3. Add the command to the CLI parser in `pssetools/cli.py`.
4. Add default configuration parameters to `pssetools/config.cfg` if needed.

## Reporting Issues
Please use the GitHub Issue tracker to report bugs or request new features.
