import pssetools
import dyntools
import pandas as pd
import os

def get_plot_data(outfiles):
    """ devuelve un DataFrame con los canales
    """
    if isinstance(outfiles, str):
        get_plot_data([outfiles])
        return

    df_dict = {}
    titles = []
    for i, outfile in enumerate(outfiles):
        obj = dyntools.CHNF(outfile)
        title, channels, data = obj.get_data()
        df_temp = pd.DataFrame.from_dict(data).rename(channels, axis=1)
        df_temp = df_temp.set_index("Time(s)")
        df_dict[os.path.basename(outfile)] = df_temp

    return df_dict

