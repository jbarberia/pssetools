## coding: latin-1
import os
import sys
import argparse


def compilacion(dll, sources, psse_vrsn=34, ivfversion="latest"):
    """Compiles and creates a PSS/E user model DLL.

    Uses PSSE"s environment manager and compiler tools to compile source
    files (.flx, .f, .for, .f90) and link them with object/library files
    to generate a .dll for user models.

    Args:
        dll (str): Output path for the generated DLL.
        sources (list): List of source, object, and library files.
        psse_vrsn
        ivfversion
        
    Returns:
        int: The result of the DLL creation process (0 on success).

    Raises:
        Exception: If DLL creation fails.
    """

    try:
        import psse_env_manager
    except ImportError:
        sys.stderr.write("ERROR: psse_env_manager no instalado.\n")
        sys.stderr.write("Verifique que está usando el intérprete Python correcto de PSS/E (64-bits).\n")
        return

    # configuracion del entorno
    psse_env_manager.set_local_env(psse_vrsn, useivfvrsn=ivfversion, showprg=True)

    # remueve archivos viejos
    if os.path.isfile(dll):
        os.remove(dll)

    # src files
    # src files
    src_lst = []
    for ext in ['.flx', '.f', '.for', '.f90']:  # include conec & conet files
        for f in sources:
            if f.lower().endswith(ext):
                src_lst.append(f)

    # obj files
    objlibfiles = []
    for ext in ['.obj', '.lib']:
        for f in sources:
            if f.lower().endswith(ext):
                objlibfiles.append(f)

    addopstr = psse_env_manager.ivf_compiler_options_add(ivfversion, "/Qdiag-disable:10448")
    addopstr = psse_env_manager.ivf_compiler_options_remove(ivfversion, "/Qauto")
    # addopstr = psse_env_manager.ivf_compiler_options_add(ivfversion, "/Qm32")

    ierr = psse_env_manager.create_dll(
        psse_vrsn,
        src_lst,
        modsources=[],
        objlibfiles=objlibfiles,
        dllname=os.path.basename(dll),
        workdir=os.path.dirname(dll),
        showprg=True,
        useivfvrsn=ivfversion,
        shortname="DSUSR",
        description="User Model",
        majorversion=1,
        minorversion=0,
        buildversion=0,
        companyname="",
        mypathlib=False,
        keep=False,
        keepf=False,
    )

    if ierr != 0:
        raise Exception("Error creating DLL: {}".format(ierr))

    # retiro .lib
    lib_file = dll.replace(".dll", ".lib")
    if os.path.exists(lib_file):
        os.remove(lib_file)

    return ierr


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PSS/E DLL Compiler Backend")
    parser.add_argument("--dll", required=True, help="Ruta de salida para el archivo .dll")
    parser.add_argument("--sources", nargs='+', required=True, help="Lista de archivos fuente (.f, .flx, .obj)")
    
    args = parser.parse_args()    
    sys.exit(compilacion(args.dll, args.sources))
