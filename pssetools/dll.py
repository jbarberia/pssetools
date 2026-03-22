# coding: latin-1
from __future__ import print_function
import os
import sys
import subprocess

from . import psse34
from . import get_config


def run(dll, sources, config, **kwargs):
    """Compiles and creates a PSS/E user model DLL.

    Uses PSSE's environment manager and compiler tools to compile source
    files (.flx, .f, .for, .f90) and link them with object/library files
    to generate a .dll for user models.

    Args:
        dll (str): Output path for the generated DLL.
        sources (list): List of source, object, and library files.
        config (str|dict): Configuration dictionary or path to configuration file.
        **kwargs: Additional keyword arguments.

    Returns:
        int: The result of the DLL creation process (0 on success).

    Raises:
        Exception: If DLL creation fails.
    """

    # configuracion del PATH
    subprocess.call(r"C:\Program Files (x86)\PTI\PSSE34\SET_PSSE_PATH.BAT")
    import psse_env_manager

    config = get_config(config)
    os.environ['PATH']    = config["DLL"]["PATH"].replace("\n", ";")
    os.environ['LIB']     = config["DLL"]["LIB"].replace("\n", ";")
    os.environ['INCLUDE'] = config["DLL"]["INCLUDE"].replace("\n", ";")
    
    # remueve archivos viejos
    if os.path.isfile(dll): os.remove(dll)

    # src files
    src_lst = []
    for ext in ['.flx','.f','.for','.f90']:       #include conec & conet files
        for f in sources:
            if f.endswith(ext):
                src_lst.append(f)

    # obj files
    objlibfiles = []
    for ext in ['.obj', '.lib']:
        for f in sources:
            if f.endswith(ext):
                objlibfiles.append(f)

    psse_vrsn = 34
    ivfversion = 18
    addopstr = psse_env_manager.ivf_compiler_options_add(ivfversion, "/Qdiag-disable:10448")
    addopstr = psse_env_manager.ivf_compiler_options_add(ivfversion, "/Qm32")
    
    ierr = psse_env_manager.create_dll(psse_vrsn, src_lst, modsources=[], 
        objlibfiles=objlibfiles, dllname=os.path.basename(dll), workdir=os.path.dirname(dll),
        showprg=True, useivfvrsn=ivfversion, shortname='DSUSR', description='User Model',
        majorversion=1, minorversion=0, buildversion=0, companyname='', mypathlib=False,
        keep=False, keepf=False)
    
    if ierr != 0:
        raise Exception("Error creating DLL: {}".format(ierr))
    
    # retiro .lib
    lib_file = dll.replace(".dll", ".lib")
    if os.path.exists(lib_file):
        os.remove(lib_file)
    return ierr
