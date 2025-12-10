from . import psse34
from . import psspy
from . import argument_parser
import sys
import os

def export_initial_conditions_suspect(filename):
    import re
    import io    
    
    with open(filename) as f:
        content = f.read()        
    
    pattern = r"INITIAL CONDITIONS SUSPECT:\n(.*)\n^"
    initial_conditions = re.search(pattern, content, re.DOTALL | re.MULTILINE).group(1)        
    data_io = u"{}".format(initial_conditions)
    
    with open(filename, "w") as f:
        f.write(data_io)
   
    
def run(out, cnv, snp, dll, py, no_debug=False, **kwargs):    
    debug = not no_debug
    dirname = os.path.dirname(out)
    basename = os.path.basename(out).split(".")[0]
    os.makedirs(os.path.dirname(out))

    # abro el caso y snp con las librerias
    ierr = psspy.case(cnv)
    ierr = psspy.rstr(snp)

    if ierr != 0:
        sys.stderr.write("No existe el archivo {}\n".format(snp))
        exit(1)

    for library in dll:
        psspy.addmodellibrary(library)
        
    # manda una copia del progress
    t_device = os.path.join(dirname, basename + ".pdv")
    ierr = psspy.t_progress_output(2, t_device, [2, 0])
    
    # inicializa
    ierr = psspy.strt_2([1, 1], out) 
    if psspy.okstrt() != 0 and debug:        
        sys.stderr.write("Error en la inicializacion - {} {}\n".format(cnv, snp))
        exit(1)    
    psspy.save(os.path.join(dirname, basename + "_T0.cnv"))
    psspy.snap(sfile=os.path.join(dirname, basename + "_T0.snp"))
    sys.stderr.write("{} incializado en T=0\n".format(basename))

    # corre simulacion
    with open(py) as f:
        code = f.read()
        exec(code)
    
    # flujo postfalla
    ierr, time = psspy.dsrval("TIME")
    psspy.save(os.path.join(dirname, basename + "_T{:.0f}.cnv".format(time)))
    psspy.snap(sfile=os.path.join(dirname, basename + "_T{:.0f}.snp".format(time)))
    
    psspy.progress("\n FIN SIMULACION\n")
    sys.stderr.write("{} finalizado en T={:.0f}\n".format(basename, time))


if __name__ == "__main__":    
    args_specs = {
        "cnv": {"type": str},        
        "out": {"type": str},                
        "snp": {"type": str},        
        "dll": {"nargs": "*", "type": str},
        "py": {"type": str},
        "no-debug": {"default": False, "action": "store_true"},        
    }    
    args = argument_parser(args_specs)
    run(**args)
