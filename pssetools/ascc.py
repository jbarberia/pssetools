import os
import sys
import pandas as pd
from .parse_sub import parse_sub
from .utils import get_config, get_kwargs, set_psse_path


def ascc(sav, subfile, config=None, **kwargs):
    """Runs ASCC short circuit analysis.

    Parses the subsystem from a .sub file, executes short circuit
    calculations, and generates a formatted report including
    three-phase and LG faults, and Thevenin impedances.

    Args:
        sav (str): Input PSS/E case file (.sav).
        sub (str): Input subsystem file (.sub) or (.sbsxml).
        config (str|dict): Configuration dictionary or path to configuration file.
        report (str): Output report file (.scf).
        **kwargs: Additional keyword arguments.

    Returns:
        pd.DataFrame: dataframe with results.
    """
    set_psse_path()
    import psspy
    import pssarrays
    psspy.psseinit()
    
    ierr = psspy.case(sav)

    config = get_config(config)
    basename = ".".join(os.path.basename(sav).split(".")[:-1])

    # arma subsistema
    if subfile.endswith(".sub"):
        subsystem = parse_sub(subfile)
        buses = subsystem.get("CORTOCIRCUITO")
        if not buses:
            raise ValueError("No hay subsistema CORTOCIRCUITO en archivo {}".format(subfile))

    elif subfile.endswith(".sbsxml"):
        psspy.bsysrcl(sid=0, sfile=subfile)
        ierr, (buses,) = psspy.abusint(sid=0, flag=1, string="NUMBER")

    else:
        raise ValueError("No se puede crear un subsistema.")
    
    psspy.bsys(0,0,[0.0,0.0],0,[],len(buses),buses,0,[],0,[])

    # corre cortocircuito
    psspy.short_circuit_warning(0)
    psspy.short_circuit_units(0)
    psspy.short_circuit_z_units(0)
    psspy.short_circuit_coordinates(0)
    psspy.short_circuit_z_coordinates(0)
    
    func = getattr(pssarrays, "ascc_currents")
    ascc_config = get_kwargs(func, config)
    rlst = func(0, 0, **ascc_config)

    # arma al reporte
    buses = rlst["fltbus"]

    df = pd.DataFrame()
    df["CASO"] = [basename] * len(buses)
    df["NUMBER"] = buses
    df["FLT3PH"] = [abs(    rlst["flt3ph"][i]["ia1"]) * psspy.sysmva() for i, bus in enumerate(buses)]
    df["FLTLG"]  = [abs(    rlst["fltlg"][i]["ia"])   * psspy.sysmva() for i, bus in enumerate(buses)]
    df["FLTLLG"] = [abs(3 * rlst["fltllg"][i]["ia0"]) * psspy.sysmva() for i, bus in enumerate(buses)]
    df["FLTLL"]  = [abs(    rlst["fltll"][i]["ib"])   * psspy.sysmva() for i, bus in enumerate(buses)]
    df["THEVZ1_R"] = [rlst["thevzpu"][i]["z1"].real for i, bus in enumerate(buses)]
    df["THEVZ1_X"] = [rlst["thevzpu"][i]["z1"].imag for i, bus in enumerate(buses)]
    df["THEVZ2_R"] = [rlst["thevzpu"][i]["z2"].real for i, bus in enumerate(buses)]
    df["THEVZ2_X"] = [rlst["thevzpu"][i]["z2"].imag for i, bus in enumerate(buses)]
    df["THEVZ0_R"] = [rlst["thevzpu"][i]["z0"].real for i, bus in enumerate(buses)]
    df["THEVZ0_X"] = [rlst["thevzpu"][i]["z0"].imag for i, bus in enumerate(buses)]
    
    assert ierr == 0
    return df

