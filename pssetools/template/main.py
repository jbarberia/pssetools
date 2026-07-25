import os
from os.path import basename, dirname, isdir, isfile
from glob import glob
import shutil
import subprocess
import psse3606
import psspy
from pssetools import dfx, acc, acc_pp, acc_unzip
from pssetools import cnv, dyn, snp, dll
psspy.psseinit()
_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()

cases = glob("src/*.sav")
dlls = glob("lib/*.dll") + glob("*.dll")
sub_file = "src/estudio.sub"
mon_file = "src/estudio.mon"
con_file = "src/estudio.con"
idv_file = "src/estudio.idv"
dyr_file = ["src/gyr_26_v34_1.dyr"]
convload = ["src/convload.py"]
config   = "src/config.cfg"
snapshot = "build/snapshot.snp"
build_dir = "build"
results_dir = "results"

# CLEAN
files_to_remove = ["src/usrdll.dll"]
files_to_remove += glob(build_dir + "/*")
files_to_remove += glob(results_dir + "/*")
files_to_remove += glob(log_dir + "/*")
for path in files_to_remove:
    if path.endswith(".dll"):
        psspy.dropmodellibrary(path)
    if isdir(path):
        shutil.rmtree(path)
    if isfile(path):
        os.remove(path)
psspy.pssehalt_2()
psspy.psseinit()

# ESTATICO
def estatico(case):
    case_basename = basename(case).replace(".sav", "")
    args = {
        "sav": case,
        "sub": sub_file,
        "mon": mon_file,
        "con": con_file,
        "dfx": os.path.join(build_dir, case_basename + ".dfx"),
        "zip": os.path.join(build_dir, case_basename + ".zip"),
        "acc": os.path.join(build_dir, case_basename + ".acc"),
        "frp": os.path.join(build_dir, case_basename + ".frp"),
        "vrp": os.path.join(build_dir, case_basename + ".vrp"),
        "folder": os.path.join(results_dir, case_basename),
        "config": config,
    }
    ierr1 = dfx.run(**args)
    ierr2 = acc.run(**args)
    ierr3 = acc_unzip.run(**args)
    ierr4 = acc_pp.run(**args)
    return [ierr1, ierr2, ierr3, ierr4]
map(estatico, cases)

# CNV
def convertir(case):
    case_basename = basename(case).replace(".sav", "")
    cnv = os.path.join(build_dir, "{}.cnv".format(case_basename))
    args = {
        "sav": case,
        "cnv": cnv,
        "py": convload,
    }
    ierr = cnv.run(**args)
    return ierr
map(convertir, glob("src/*.sav"))

# SNAPSHOT
snp.run(
    sav=cases[0],
    snp=snapshot,
    dyr=dyr_file,
    cc=os.path.join(build_dir, "cc.flx"),
    ct=os.path.join(build_dir, "ct.flx"),
    idv=idv_file,
)

# COMPILA
os.system("bash compila.sh")

# DINAMICO
def dinamico(case, script):
    case_basename = basename(case).replace(".cnv", "")
    script_basename = basename(script).replace(".py", "")
    ofile = os.path.join(
        results_dir,
        "{}_{}".format(case_basename, script_basename),
    )
    args = {
        "out": ofile + ".outx",
        "cnv": case,
        "snp": snapshot,
        "dll": dlls,
        "py": script,
        "no_debug": False,
    }
    ierr = dyn.run(**args)
    return ofile + "outx"

out = dinamico("build/FC01_BASE_CASE.cnv", "src/D01.py")


