from . import psspy
from . import argument_parser


def run(sav, cnv, py, **kwargs):
    psspy.case(sav)
    for file in py:
        if file.endswith(".py"):
            with open(file) as f:
                code = f.read()
                exec(code)
    psspy.save(cnv)
        

if __name__ == "__main__":    
    args_specs = {
        "sav": {"type": str},
        "cnv": {"type": str}, 
        "py": {"nargs": "*", "type": str}
    }    
    args = argument_parser(args_specs)
    run(**args)
    
    