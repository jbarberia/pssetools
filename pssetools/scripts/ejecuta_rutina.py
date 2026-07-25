import os
import argparse
from pssetools.utils import set_psse_path


def ejecuta_rutina(ifile, ofile, py, **kwargs):
    """Run scripts on one or more .sav cases.

    Executes specified Python scripts on the loaded case(s) before saving.

    Args:
        ifile (list or str): Input PSS/E case file(s) (.sav).
        ofile (list or str, optional): Output saved case file(s). If None, overwrites ifile.
        py (list or str): Python script or list of Python scripts to execute before saving.
        **kwargs: Additional keyword arguments.
        
    Returns:
        int or list: The PSS/E activity return code (ierr) or a list of return codes if 
                     multiple files were processed.
    """
    
    if not ofile:
        ofile = ifile

    if isinstance(py, str):
        py = [py]

    if isinstance(ifile, list):
        if len(ifile) != len(ofile):
            raise ValueError("La cantidad de archivos de entrada (ifile) y salida (ofile) no coincide.")
    
        ierr_list = []
        for inp, out in zip(ifile, ofile):
            ierr = ejecuta_rutina(inp, out, py, **kwargs)
            ierr_list.append(ierr)
        return
    
    set_psse_path()
    import psspy
    psspy.psseinit()
    psspy.case(ifile)

    locals_vars = {
        "psspy": psspy,
        "_i" : psspy.getdefaultint(),
        "_f" : psspy.getdefaultreal(),
        "_s" : psspy.getdefaultchar(),
    }
    
    for file in py:
        if file.endswith(".py"):
            with open(file) as f:
                code = f.read()
                exec(code, locals_vars)
    
    # crea ruta si no existe (y si dirname no está vacío)
    dirname = os.path.dirname(ofile)
    if dirname and not os.path.isdir(dirname):
        os.makedirs(dirname)
    ierr = psspy.save(ofile)
    return ierr



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Ejecuta rutinas (scripts Python) sobre uno o varios casos PSS/E."
    )
    
    parser.add_argument(
        "-i", "--ifile",
        nargs="+",
        required=True, 
        help="Ruta al archivo (o archivos) de caso PSS/E de entrada (.sav)."
    )
    
    parser.add_argument(
        "-o", "--ofile", 
        nargs="+",
        required=False, 
        help="Ruta al archivo (o archivos) de caso PSS/E de salida."
    )
    
    parser.add_argument(
        "-p", "--py", 
        nargs="+", 
        required=True, 
        help="Ruta al script o lista de scripts Python a ejecutar (separados por espacio)."
    )    
    args = parser.parse_args()

    ierr = ejecuta_rutina(
        ifile=args.ifile,
        ofile=args.ofile,
        py=args.py
    )

