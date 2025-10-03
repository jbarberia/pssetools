from . import psse34
from . import psspy
from . import argument_parser
import os

SPLIT_CHAR = "-"

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
   
    
def run(outx, chan, snp, dll, no_debug=False, keep_post_fault_case=False, **kwargs):
    debug = not no_debug
    
    # del outx obtengo el cnv y psa
    baseout = os.path.basename(outx).replace(".outx", "")
    sav, aut = baseout.split(SPLIT_CHAR)
    build_folder = os.path.dirname(snp)
    
    # abro el caso y snp con las librerias
    psspy.case(os.path.join(build_folder, sav + ".cnv"))
    psspy.rstr(snp)
    for library in dll:
        psspy.addmodellibrary(library)
        
    # instancio canales
    psspy.runrspnsfile(chan)
    
    # inicializa
    if debug:
        t_device = sav + "_initial_conditions_suspect.txt"
        ierr = psspy.t_progress_output(2, t_device)
        ierr = psspy.strt_2([1, 1], outx) 
        ierr = psspy.t_progress_output(6, "")
    
        if psspy.okstrt() != 0:
            export_initial_conditions_suspect(t_device)
            exit(1)
        else:
            os.remove(t_device)
    else:
        ierr = psspy.strt_2([1, 1], outx) 
    
    # corre simulacion
    if os.path.isfile(aut + ".psa"):
        psspy.psas(aut + ".psa", "simulacion.idv")
        psspy.runrspnsfile("simulacion.idv")
        os.remove("simulacion.idv")
    
    if os.path.isfile(aut + ".py"):
        execfile(aut + ".py")
    
    # guarda el caso post falla
    if keep_post_fault_case:
        psspy.save(outx.replace(".outx", "-postfault.cnv"))


if __name__ == "__main__":    
    args_specs = {        
        "outx": {"type": str},                
        "chan": {"type": str},
        "snp": {"type": str},
        "dll": {"nargs": "*", "type": str},
        "no-debug": {"default": False, "action": "store_true"},
        "keep_post_fault_case": {"default": False, "action": "store_true"},
    }    
    args = argument_parser(args_specs)
    run(**args)