from __future__ import print_function
from . import psspy
from . import pss_activity
import sys
import os

def export_initial_conditions_suspect(filename):
    """Extracts 'INITIAL CONDITIONS SUSPECT' from a progress output file.

    Parses the input file for a specific pattern of suspected initial conditions
    and overwrites the file with only that information if found.

    Args:
        filename (str): The path to the progress output file to parse.
    """
    import re
    
    with open(filename) as f:
        content = f.read()        
    
    pattern = r"INITIAL CONDITIONS SUSPECT:\n(.*)\n^"
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    if match:
        initial_conditions = match.group(1)        
        with open(filename, "w") as f:
            f.write(initial_conditions)
   
@pss_activity
def run(out, cnv, snp, dll, py, no_debug=False, **kwargs):    
    """Executes a dynamic simulation.

    Loads a converted case (.cnv), applies snapshot (.snp) and user-defined 
    libraries (.dll), and runs the simulation defined in a Python script (.py).
    Intermediate results are saved as .cnv and .snp at T=0 and end of simulation.

    Args:
        out (str): Path for the simulation output file (.out).
        cnv (str): Input converted case file (.cnv).
        snp (str): Input snapshot file (.snp).
        dll (list): List of user DLLs to add to the simulation.
        py (str): Path to the Python simulation script.
        no_debug (bool, optional): If True, suppresses debug output on initialization failure. Defaults to False.
        **kwargs: Additional keyword arguments.

    Returns:
        int: 0 on success.

    Raises:
        Exception: If loading snapshot or initialization fails.
    """
    debug = not no_debug
    dirname = os.path.dirname(out)
    basename = os.path.basename(out).split(".")[0]
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

    # abro snp con las librerias (cnv ya fue abierto por pss_activity)
    ierr = psspy.rstr(snp)
    if ierr != 0:
        raise Exception("Error loading snapshot {}: {}".format(snp, ierr))

    for library in dll:
        psspy.addmodellibrary(library)
        
    # manda una copia del progress
    t_device = os.path.join(dirname, basename + ".pdv")
    ierr = psspy.t_progress_output(2, t_device, [2, 0])
    
    # inicializa
    ierr = psspy.strt_2([1, 1], out) 
    if psspy.okstrt() != 0 and debug:        
        raise Exception("Error en la inicializacion - {} {}".format(cnv, snp))
        
    psspy.save(os.path.join(dirname, basename + "_T0.cnv"))
    psspy.snap(sfile=os.path.join(dirname, basename + "_T0.snp"))
    sys.stdout.write("{} incializado en T=0\n".format(basename))

    # corre simulacion
    with open(py) as f:
        code = f.read()
        exec(code)
    
    # flujo postfalla
    ierr, time = psspy.dsrval("TIME")
    psspy.save(os.path.join(dirname, basename + "_T{:.0f}.cnv".format(time)))
    psspy.snap(sfile=os.path.join(dirname, basename + "_T{:.0f}.snp".format(time)))
    
    psspy.progress("\n FIN SIMULACION\n")
    sys.stdout.write("{} finalizado en T={:.0f}\n".format(basename, time))
    return 0
