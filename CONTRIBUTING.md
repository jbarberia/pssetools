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

1. **Create a new module:** in `pssetools/` (e.g., `pssetools/opf.py`).
2. **Use the `@pss_activity` decorator:** 
   The `pssetools.pss_activity` decorator handles common tasks:
   - Automatically loads the `.sav` or `.cnv` case before the function runs.
   - Catches exceptions and ensures PSS/E output is redirected back to the screen if it was captured.
   - Verifies the return code of the activity and raises an exception on failure (if the return value is a non-zero integer).

   ```python
   from pssetools import pss_activity
   import psspy

   @pss_activity
   def run(sav, output_file, **kwargs):
       ierr = psspy.my_psse_activity(output_file)
       return ierr
   ```

3. **Register in CLI:** Add the command to the parser in `pssetools/cli.py`.
4. **Update Config:** Add default configuration parameters to `pssetools/config.cfg` if the activity requires specific settings.

## Configuration Handling
Always use `pssetools.get_config()` to retrieve settings. This ensures user-provided configuration files (via `--config`) are correctly merged with system defaults.

## Reporting Issues
Please use the GitHub Issue tracker to report bugs or request new features.
