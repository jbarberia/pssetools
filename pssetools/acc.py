from __future__ import print_function
from . import get_config
from . import psspy
from . import pss_activity
import os
import shutil

@pss_activity
def run(sav, acc, dfx, zipfile=None, config=None, **kwargs):
    """Runs ACCC contingency analysis.

    Executes the contingency analysis activity specified in the configuration,
    loads the distribution factors, and generates results in .acc and .zip formats.

    Args:
        sav: Input PSS/E case file (.sav).
        acc: Output ACCC results file (.acc).
        dfx: Input distribution factors file (.dfx).
        zipfile: Optional output path for the zip report.
        config: Optional path to a configuration file.
        **kwargs: Additional arguments.

    Returns:
        The PSS/E activity return code.
    """
    config = get_config(config)
    
    if zipfile is None:
        zipfile = acc.replace(".acc", ".zip")
    
    tmp_zipfile = os.path.join(os.path.expanduser("~"), os.path.basename(zipfile))

    # corro acc
    function = getattr(psspy, config["ACC"]["ACTIVITY"].lower())    
    ierr = function(
            dfxfile=dfx,
            accfile=acc,
            zipfile=tmp_zipfile,
            **config["ACC"]
        )

    # el zip lo llevo a la carpeta de destino
    if os.path.isfile(tmp_zipfile):    
        if os.path.exists(zipfile):
            os.remove(zipfile)
        shutil.move(tmp_zipfile, zipfile)
    
    return ierr