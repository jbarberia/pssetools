from . import psspy
from . import argument_parser


def run(sav, sub, mon, con, dfx, **kwargs):
    psspy.case(sav)
    ierr = psspy.dfax_2([1,1,0], sub, mon, con, dfx)
    assert ierr == 0
    

if __name__ == "__main__":    
    args_specs = {
        "sav": {"type": str},
        "sub": {"type": str}, 
        "mon": {"type": str}, 
        "con": {"type": str},
        "dfx": {"type": str},
    }    
    args = argument_parser(args_specs)
    run(**args)
    
    