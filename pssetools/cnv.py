from __future__ import print_function
from . import psspy
from . import pss_activity


@pss_activity
def run(sav, cnv, py, **kwargs):
    for file in py:
        if file.endswith(".py"):
            with open(file) as f:
                code = f.read()
                exec(code)
    ierr = psspy.save(cnv)
    return ierr