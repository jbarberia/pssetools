from __future__ import print_function
from . import get_config
from . import psspy
from . import pssarrays
from . import pss_activity
from .parse_sub import parse_sub
import os
import sys


@pss_activity
def run(sav, sub, config, report, **kwargs):
    config = get_config(config)

    # arma subsistema
    basename = ".".join(os.path.basename(sav).split(".")[:-1])
    subsystem = parse_sub(sub)
    buses = subsystem.get("CORTOCIRCUITO")
    if not buses:
        raise ValueError("No hay subsistema CORTOCIRCUITO en archivo {}".format(sub))
    
    psspy.bsys(0,0,[0.0,0.0],0,[],len(buses),buses,0,[],0,[])

    # corre cortocircuito
    psspy.short_circuit_warning(0)
    psspy.short_circuit_units(0)
    psspy.short_circuit_z_units(0)
    psspy.short_circuit_coordinates(0)
    psspy.short_circuit_z_coordinates(0)
    ascc_config = {k.lower(): v for (k, v) in config["ASCC"].items()}
    rlst = pssarrays.ascc_currents(0, 0, **ascc_config)

    # arma al reporte
    buses = rlst["fltbus"]
    flt3ph = {bus: abs(    rlst["flt3ph"][i]["ia1"]) * psspy.sysmva() for i, bus in enumerate(buses)}
    fltlg  = {bus: abs(    rlst["fltlg"][i]["ia"])   * psspy.sysmva() for i, bus in enumerate(buses)}
    fltllg = {bus: abs(3 * rlst["fltllg"][i]["ia0"]) * psspy.sysmva() for i, bus in enumerate(buses)}
    fltll  = {bus: abs(    rlst["fltll"][i]["ib"])   * psspy.sysmva() for i, bus in enumerate(buses)}
    thevz1_r = {bus: rlst["thevzpu"][i]["z1"].real for i, bus in enumerate(buses)}
    thevz1_x = {bus: rlst["thevzpu"][i]["z1"].imag for i, bus in enumerate(buses)}
    thevz2_r = {bus: rlst["thevzpu"][i]["z2"].real for i, bus in enumerate(buses)}
    thevz2_x = {bus: rlst["thevzpu"][i]["z2"].imag for i, bus in enumerate(buses)}
    thevz0_r = {bus: rlst["thevzpu"][i]["z0"].real for i, bus in enumerate(buses)}
    thevz0_x = {bus: rlst["thevzpu"][i]["z0"].imag for i, bus in enumerate(buses)}

    ierr = psspy.t_progress_output(2, report, [0, 0])
    header = [
        "CASO",
        "BUS",
        "NAME",
        "KV",
        "THREE PHASE FAULT",
        "LG FAULT",
        "LLG FAULT",
        "LL FAULT",
        "R1",
        "X1",
        "R2",
        "X2",
        "R0",
        "X0",
    ]
    psspy.progress(" " + "\t".join(header) + "\n")

    for bus in buses:
        ierr, name = psspy.notona(bus)
        ierr, base = psspy.busdat(bus, "BASE")
        
        line = []
        line.append("{}".format(basename))
        line.append("{:.0f}".format(bus))
        line.append("{}".format(name[:12].strip()))
        line.append("{:.1f}".format(base))
        line.append("{:.0f}".format(flt3ph[bus]))
        line.append("{:.0f}".format(fltlg[bus]))
        line.append("{:.0f}".format(fltllg[bus]))
        line.append("{:.0f}".format(fltll[bus]))
        line.append("{:.4f}".format(thevz1_r[bus]))
        line.append("{:.4f}".format(thevz1_x[bus]))
        line.append("{:.4f}".format(thevz2_r[bus]))
        line.append("{:.4f}".format(thevz2_x[bus]))
        line.append("{:.4f}".format(thevz0_r[bus]))
        line.append("{:.4f}".format(thevz0_x[bus]))

        psspy.progress(" " + "\t".join(line) + "\n")
    
    return 0
