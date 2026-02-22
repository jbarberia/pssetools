from __future__ import print_function
from . import get_config
from . import psspy
from . import pss_activity
import os
import shutil

@pss_activity
def run(sav, acc, dfx, zipfile=None, config=None, **kwargs):
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