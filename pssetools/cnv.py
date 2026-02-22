from __future__ import print_function
from . import psspy
from . import pss_activity


@pss_activity
def run(sav, cnv, py, **kwargs):
    """Converts a .sav case to a snapshot/dynamic (.cnv) case.

    Executes specified Python scripts on the loaded case before saving
    it as a converted file.

    Args:
        sav: Input PSS/E case file (.sav).
        cnv: Output converted case file (.cnv).
        py: List of Python scripts to execute before saving.
        **kwargs: Additional arguments.

    Returns:
        The PSS/E activity return code.
    """
    for file in py:
        if file.endswith(".py"):
            with open(file) as f:
                code = f.read()
                exec(code)
    ierr = psspy.save(cnv)
    return ierr