from __future__ import print_function
from . import psspy
from . import pss_activity

@pss_activity
def run(sav, script, report, **kwargs):
    ierr = psspy.t_report_output(2, report, [2, 0])

    with open(script) as f:
        code = f.read()
        exec(code)
    
    return ierr
