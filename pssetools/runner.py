from . import psse34
from . import psspy
from . import argument_parser
import os


def run(sav, script, report, **kwargs):
    psspy.case(sav)    
    ierr = psspy.t_report_output(2, report, [2, 0])

    with open(script) as f:
        code = f.read()
        exec(code)


if __name__ == "__main__":    
    args_specs = {                                
        "sav": {"type": str},
        "script": {"type": str},
        "report": {"type": str},
    }    
    args = argument_parser(args_specs)
    run(**args)
