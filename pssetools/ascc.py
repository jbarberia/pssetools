from . import argument_parser
from . import get_config
from . import psse34
from . import psspy
from . import pssarrays
import os
import shutil


def run(sav, ascc, config, **kwargs):
    psspy.case(sav)


    # pssarrays.ascc_currents(sid)

    pass


if __name__ == "__main__":
    args_specs = {
        "sav": {"type": str},
        "ascc": {"type": str}, 
        "config": {"type": str},         
    }    
    args = argument_parser(args_specs)
    run(**args)
    