import os
import shutil
import pandas as pd
from pssetools import get_config
from pssetools.utils import set_psse_path
from pssetools.scripts.cortocircuito import cortocircuito

set_psse_path()

def test_ascc():
    config = get_config()
    filename = "test/files/savnw.sav"
    folder = "temp_folder"
    config["pssetools.ascc"]["subfile"] = "test/files/savnw.sub"
    config["pssetools.ascc"]["subsystem_name"] = "WEST"
    ascc = cortocircuito(filename, config, folder)
    
