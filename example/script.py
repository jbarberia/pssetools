import os
import pandas as pd
from glob import glob
import pssetools
from pssetools.scripts.estatico import estatico
from pssetools.scripts.cortocircuito import cortocircuito
from pssetools.scripts.ejecuta_rutina import ejecuta_rutina
cases  = glob("*.sav")
config = "config.jsonc"


# estatico
folder = "estatico"
results = [estatico(case, config, folder) for case in cases]
dff, dfv = zip(*results)
with pd.ExcelWriter("resultados.xlsx", engine="openpyxl") as writter:
    pd.concat(dff).to_excel(writter, "flujos", index=False)
    pd.concat(dfv).to_excel(writter, "tensiones", index=False)


# cortocircuito
folder = "cortocircuito"
ccdf = [cortocircuito(case, config, folder) for case in cases]
with pd.ExcelWriter("resultados.xlsx", engine="openpyxl", mode="a") as writter:
    pd.concat(ccdf).to_excel(writter, "cortocircuito", index=False)


# prepara dinamico
folder = "dinamico"
for case in cases:
    ofile = os.path.join(folder, os.path.basename(case).replace(".sav", ".cnv"))
    ejecuta_rutina(case, ofile, "convload.py")


# genera snapshot
dyr = glob("*.dyr")
pssetools.snp(
    sav=cases[0],
    dyr=dyr,
    snp="{}/snapshot.snp".format(folder),
    cc="{}/conec.flx".format(folder),
    ct="{}/conet.flx".format(folder),
    idv="estudio.idv",
    config=config,
)

# compila - copiar y pegar para generar otros dll
os.system(
    "C:/Python314/python.exe -m pssetools.scripts.compila" +
    " --dll lib/dsurs.dll" +
    " --sources " + " ".join(glob("{}/*.flx".format(folder)) + glob("*/*.lib")) +
    " --config " + config
)

# simulaciones dinamicas
args = {
    "dll": glob("*/*.dll"),
    "snp": "{}/snapshot.snp".format(folder),
}


pssetools.dyn(cnv="dinamico/FC01.cnv", out="dinamico/FC01/D01.out", py="flat.py", **args)
pssetools.dyn(cnv="dinamico/FC02.cnv", out="dinamico/FC02/D02.out", py="flat.py", **args)
pssetools.dyn(cnv="dinamico/FC11.cnv", out="dinamico/FC11/D03.out", py="flat.py", **args)
pssetools.dyn(cnv="dinamico/FC12.cnv", out="dinamico/FC12/D04.out", py="flat.py", **args)




