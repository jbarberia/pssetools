import os
import shutil
import pandas as pd
from pssetools import get_config
from pssetools.utils import set_psse_path
from pssetools.scripts.estatico import estatico
from pssetools.scripts.factores_de_distribucion import factores_de_distribucion

set_psse_path()

def test_estatico():
    config = get_config()
    config["psspy.dfax_2"]["subfile"] = "test/files/savnw.sub"
    config["psspy.dfax_2"]["monfile"] = "test/files/savnw.mon"
    config["psspy.dfax_2"]["confile"] = "test/files/savnw.con"
    
    filename = "test/files/savnw.sav"
    folder = "temp_folder"
    dff, dfv = estatico(filename, config, folder)

    assert isinstance(dff, pd.DataFrame)
    assert isinstance(dfv, pd.DataFrame)
    assert os.path.isdir(folder)
    shutil.rmtree(folder)


def test_otdf():
    config = get_config()
    config["psspy.dfax_2"]["subfile"] = "test/files/savnw.sub"
    config["psspy.dfax_2"]["monfile"] = "test/files/savnw.mon"
    config["psspy.dfax_2"]["confile"] = "test/files/savnw.con"

    filename = "test/files/savnw.sav"
    folder = "temp_folder"
    otdf = factores_de_distribucion(filename, config, folder)

    assert isinstance(otdf, pd.DataFrame)
    assert os.path.isdir(folder)
    shutil.rmtree(folder)

