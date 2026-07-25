import os
import sys
import pssetools
from pssetools.utils import set_psse_path


def cortocircuito(sav, config, folder):
    set_psse_path()
    import psspy
    
    config = pssetools.get_config(config)

    if not os.path.isdir(folder):
        os.makedirs(folder)

    func = pssetools.ascc
    kwargs = pssetools.get_kwargs(func, config)
    
    kwargs["sav"] = sav
    kwargs["config"] = config
    df = func(**kwargs)
    return df


if __name__ == "__main__":
    sav = sys.argv[1]
    config = sys.argv[2]
    folder = sys.argv[3]
    scdf = cortocircuito(sav, config, folder)


