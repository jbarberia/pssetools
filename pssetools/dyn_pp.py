from __future__ import print_function
from . import get_config
from . import pss_activity
import os
import pandas as pd


@pss_activity
def run(out, ofile, config, **kwargs):
    """Post-process dynamic channel outputs.

    Exports channels from a PSS/E dynamic output file to a tab-separated file
    or an Excel workbook depending on the output extension.

    Args:
        out (str): Input dynamic channel output file (.out).
        ofile (str): Output file path (.tsv or .xlsx).
        config (str|dict): Configuration dictionary or path to configuration file.
        **kwargs: Additional keyword arguments.

    Returns:
        int: 0 on success.
    """
    import dyntools

    config = get_config(config)
    obj = dyntools.CHNF(out)

    title, channels, data = obj.get_data()
    df = pd.DataFrame.from_dict(data).rename(channels, axis=1)

    if ofile.endswith(".xlsx"):
        df.to_excel(ofile, index=False)
    else:
        df.to_csv(ofile, sep="\t", index=False)

    return 0
