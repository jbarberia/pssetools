from __future__ import print_function
from . import psspy
from . import pss_activity

@pss_activity
def run(sav, script, report, **kwargs):
    """Executes a custom Python script and redirects PSS/E report output.

    Args:
        sav (str): Input PSS/E case file (.sav).
        script (str): Path to the Python script to execute.
        report (str): Path to the output report file.
        **kwargs: Additional keyword arguments.

    Returns:
        int: The PSS/E activity return code.
    """
    ierr = psspy.t_report_output(2, report, [2, 0])

    with open(script) as f:
        code = f.read()
        exec(code)
    
    return ierr
