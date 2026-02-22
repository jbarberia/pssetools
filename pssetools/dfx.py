from __future__ import print_function
from . import psspy
from . import pss_activity


@pss_activity
def run(sav, sub, mon, con, dfx, **kwargs):
    ierr = psspy.dfax_2([1,1,0], sub, mon, con, dfx)
    return ierr