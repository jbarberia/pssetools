from __future__ import print_function
from . import psspy
from . import pss_activity


@pss_activity
def run(sav, sub, mon, con, dfx, **kwargs):
    """Calculates distribution factors for contingency analysis.

    Uses subsystems, monitored elements, and contingency definitions
    to generate a distribution factors file (.dfx).

    Args:
        sav: Input PSS/E case file (.sav).
        sub: Input subsystem file (.sub).
        mon: Input monitored elements file (.mon).
        con: Input contingency file (.con).
        dfx: Output distribution factors file (.dfx).
        **kwargs: Additional arguments.

    Returns:
        The PSS/E activity return code.
    """
    ierr = psspy.dfax_2([1,1,0], sub, mon, con, dfx)
    return ierr