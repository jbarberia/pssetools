import os
import shutil
import pandas as pd
from pssetools import get_config
from pssetools.utils import set_psse_path
from pssetools.scripts.estatico import estatico
from pssetools.scripts.factores_de_distribucion import factores_de_distribucion

set_psse_path()

def test_estatico():
    filename = "test/files/savnw.sav"
    folder = "temp_folder"
    dff, dfv = estatico(
        filename,
        sub="test/files/savnw.sub",
        mon="test/files/savnw.mon",
        con="test/files/savnw.con",
        folder=folder,
    )

    assert isinstance(dff, pd.DataFrame)
    assert isinstance(dfv, pd.DataFrame)
    assert os.path.isdir(folder)
    shutil.rmtree(folder)


def test_otdf():
    filename = "test/files/savnw.sav"
    folder = "temp_folder"
    otdf = factores_de_distribucion(
        filename,
        sub="test/files/savnw.sub",
        mon="test/files/savnw.mon",
        con="test/files/savnw.con",
        folder=folder,
    )

    assert isinstance(otdf, pd.DataFrame)
    assert os.path.isdir(folder)
    shutil.rmtree(folder)


