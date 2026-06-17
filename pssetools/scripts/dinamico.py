from .. import psspy

_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()

def correr_por(segundos=None, ciclos=None):
    ierr, time = psspy.dsrval("TIME")
    if segundos:
        psspy.run(0, time + segundos, 0, 1, 0)

    if ciclos:
        ierr, freq = psspy.base_frequency()
        psspy.run(0, time + ciclos/freq, 0, 1, 0)

    ierr, time = psspy.dsrval("TIME")
    return time


def correr_hasta(segundos=None, ciclos=None):
    ierr, time = psspy.dsrval("TIME")
    if segundos:
        psspy.run(0, segundos, 0, 1, 0)

    if ciclos:
        ierr, freq = psspy.base_frequency()
        psspy.run(0, ciclos/freq, 0, 1, 0)

    ierr, time = psspy.dsrval("TIME")
    return time


def falla_monofasica(ibus, jbus, ckt, zf=0.0+0.0j, location=0.5):
    options = [
        3, # in-line fault.
        _i, # include a path to ground (not used)
        1, # line-to-ground fault
        _i, # breaker at bus IBUS is open (not used)
        0, # dc line and FACTS device option (block and ignore)
        1, # transformer impedance correction option (apply to zero sequence)
        0, # fault analysis generator reactance option (use subtransient reactance)
    ]
    values = [
        location, # fault location as fraction of line from bus
        zf.real, # Rl-g
        zf.imag, # Xl-g
        _f, # Rl-l (not used)
        _f, # Xl-l (not used)
    ]
    ierr = psspy.dist_spcb_fault_2(ibus, jbus, ckt, options, values)
    if ierr > 0:
        ierr, string = psspy.apierrstr("dist_spcb_fault_2", ierr)
        psspy.report(string + "\n")


def falla_trifasica(ibus, jbus, ckt, zf=0.0+0.0j, location=0.5):
    options = [
        3, # in-line fault.
        _i, # path to ground code (not used)
        3, # three phase fault.
        _i, # breaker at bus IBUS is open (not used)
        0, # dc line and FACTS device option (block and ignore)
        1, # transformer impedance correction option (apply to zero sequence)
        0, # fault analysis generator reactance option (use subtransient reactance)
    ]
    values = [
        location, # fault location as fraction of line from bus
        zf.real, # Rl-g
        zf.imag, # Xl-g
        _f, # Rl-l (not used)
        _f, # Xl-l (not used)
    ]
    ierr = psspy.dist_spcb_fault_2(ibus, jbus, ckt, options, values)
    if ierr > 0:
        ierr, string = psspy.apierrstr("dist_spcb_fault_2", ierr)
        psspy.report(string + "\n")
    

def apertura_fase_fallada(ibus, jbus, ckt):
    options = [
        1, # one phase open.
        0, # no path to ground.
        _i, # type of in-line fault code (not used)
        _i, # breaker at bus IBUS is open (not used)
        0, # dc line and FACTS device option (block and ignore)
        1, # transformer impedance correction option (apply to zero sequence)
        0, # fault analysis generator reactance option (use subtransient reactance)
    ]
    values = [
        _f, # fault location as fraction of line from bus (not used)
        _f, # Rl-g (not used)
        _f, # Xl-g (not used)
        _f, # Rl-l (not used)
        _f, # Xl-l (not used)

    ]
    ierr = psspy.dist_spcb_fault_2(ibus, jbus, ckt, options, values)
    if ierr > 0:
        ierr, string = psspy.apierrstr("dist_spcb_fault_2", ierr)
        psspy.report(string + "\n")


def aplica_dag(machine_list, mw_value=9999):
    """Aplica la desconexion de maquinas segun una orden de merito dada

    Args:
        machine_list (list): listado de maquinas
        mw_value (float): volumen a daguear
    """ 
    
    selected_machines = []
    cumulative_to_shed = mw_value

    # selecciona maquinas
    for ibus, id in machine_list:
        ierr, active_power = psspy.macdat(ibus, id, "P")
        ierr, in_service = psspy.macint(ibus, id, "STATUS")
        if ierr > 0:
            ierr, string = psspy.apierrstr("dist_spcb_fault_2", ierr)
            psspy.report(string + "({}, {})\n".format(ibus, id))
        elif in_service and cumulative_to_shed > 0:
            selected_machines.append((ibus, id))
            cumulative_to_shed -= active_power

    # aplica la desconexion
    for ibus, id in selected_machines:
        ierr = psspy.dist_machine_trip(ibus, id)

    return cumulative_to_shed




