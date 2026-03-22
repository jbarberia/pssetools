from __future__ import print_function
from . import psspy
from . import pss_activity


@pss_activity
def run(sav, sub, mon, con, dfx, **kwargs):
    """Calculates distribution factors for contingency analysis.

    Uses subsystems, monitored elements, and contingency definitions
    to generate a distribution factors file (.dfx).

    Args:
        sav (str): Input PSS/E case file (.sav).
        sub (str): Input subsystem file (.sub).
        mon (str): Input monitored elements file (.mon).
        con (str): Input contingency file (.con).
        dfx (str): Output distribution factors file (.dfx).
        **kwargs: Additional keyword arguments.

    Returns:
        int: The PSS/E activity return code.
    """
    ierr = psspy.dfax_2([1,1,0], sub, mon, con, dfx)
    return ierr