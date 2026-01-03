from . import argument_parser
from . import get_config
from . import psse34
from . import psspy
import os
import shutil

def run(sav, acc, dfx, zipfile, config, **kwargs):
    config = get_config(config)
    tmp_zipfile = os.path.join(os.path.expanduser("~"), os.path.basename(zipfile))

    # abro el caso y corro acc
    psspy.case(sav)
    function = getattr(psspy, config["ACC"]["ACTIVITY"].lower())    
    ierr = function(
            dfxfile=dfx,
            accfile=acc,
            zipfile=tmp_zipfile,
            **config["ACC"]
        )

    # el zip lo llevo a la carpeta de destino
    if os.path.isfile(tmp_zipfile):    
        shutil.move(tmp_zipfile, zipfile)


if __name__ == "__main__":
    args_specs = {
        "sav": {"type": str},
        "dfx": {"type": str}, 
        "acc": {"type": str}, 
        "zipfile": {"type": str},         
        "config": {"type": str},         
    }    
    args = argument_parser(args_specs)
    run(**args)
    
    