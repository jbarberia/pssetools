import os
import pandas as pd
from .parse_sub import parse_sub


def ascc(sav, subfile, subsystem_name="CORTOCIRCUITO", **kwargs):
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
    import psspy # type: ignore
    import pssarrays # type: ignore
    psspy.psseinit()
    
    ierr = psspy.case(sav)
    basename, _ = os.path.splitext(os.path.basename(sav))

    # arma subsistema
    if subfile.endswith(".sub"):
        subsystem = parse_sub(subfile)
        if not subsystem_name:
            raise ValueError("No hay subsistema {} en archivo {}".format(subsystem_name, subfile))

        buses = subsystem.get(subsystem_name)
        if not buses:
            raise ValueError("No hay subsistema {} en archivo {}".format(subsystem_name, subfile))

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
    
    rlst = pssarrays.ascc_currents(
        0, 0,
        flt3ph=1, fltlg=1, fltllg=1, fltll=1,
        linout=0, linend=0, voltop=0, genxop=0,
        tpunty=0, dcload=0, zcorec=1, lnchrg=0,
        shntop=0, loadop=0, machpq=0, volts=1.0,
        relfile="", fcdfile="", scfile="nooutput",
        rptop=-1, rptlvl=0
    )

    # arma al reporte
    buses = rlst["fltbus"]

    df = pd.DataFrame()
    df["CASO"] = [basename] * len(buses)
    df["NUMBER"] = buses
    df["NAME"] = [psspy.notona(bus)[-1][:12].strip() for bus in buses]
    df["KV"] = [psspy.busdat(bus, "BASE")[-1] for bus in buses]
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

