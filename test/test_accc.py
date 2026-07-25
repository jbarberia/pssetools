import os
import pandas as pd
from pssetools import get_config
from pssetools.utils import set_psse_path
from pssetools.scripts.estatico import estatico

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
    os.removedirs(folder)    


    # TODO sumar otdf en algun lado
    # import arrbox.dfax_pp
    # dfxfile = config["psspy.dfax_2"]["dfxfile"]
    # dfxobj = arrbox.dfax_pp.DFAX_PP(dfxfile)
    # smryobj = dfxobj.summary()
    # otdfobj = dfxobj.otdf_factors()
