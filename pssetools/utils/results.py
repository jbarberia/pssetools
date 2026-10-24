# coding: latin-1
import os
import pandas as pd
import psspy

def get_results_from_case(mon_file):
    """
    Lee un archivo de monitoreo TSV y extrae datos de PSS/E para cada elemento.
    """
    df_mon = pd.read_csv(mon_file, sep="\t", encoding="latin-1", header=0, skiprows=0, skipinitialspace=True, dtype=str)
    df_mon.columns = ["ELEMENTO", "ID1", "ID2", "ID3", "ID4", "DESCRIPCION"]

    all_data = []
    for _, row in df_mon.iterrows():        
        elem = row["ELEMENTO"]
        desc = row["DESCRIPCION"]
        
        # Mapeo de elementos a sus funciones de extracci�n
        if elem == "BU":
            res = get_bus_data(int(row["ID1"]))
        elif elem in ["LII", "TR", "SYS"]:
            res = get_branch_data(int(row["ID1"]), int(row["ID2"]), row["ID3"])
        elif elem == "T3":
            res = get_3w_transformer_data(int(row["ID1"]), int(row["ID2"]), int(row["ID3"]), row["ID4"])
        elif elem == "LO":
            res = get_load_data(int(row["ID1"]), row["ID2"])
        elif elem == "ME":
            res = get_machine_data(int(row["ID1"]), row["ID2"])
        else:
            continue

        # Formateamos los resultados para el DataFrame final
        for var, val in res.items():
            all_data.append({
                "ELEMENTO": elem,
                "ID1": row["ID1"],
                "ID2": row["ID2"],
                "ID3": row["ID3"],
                "ID4": row["ID4"],
                "VARIABLE": var,
                "VALOR": val,
                "DESCRIPCION": desc if var == "DESCRIPCION" else None
            })

    return pd.DataFrame(all_data)


def get_bus_data(bus_id, variables=["VM", "BASE"]):
    """Extrae datos de una barra."""
    results = {}
    for var in variables:
        ierr, val = psspy.busdat(bus_id, var)
        if ierr == 0:
            results[var] = val
    return results


def get_branch_data(ibus, jbus, ckt, variables=["MW", "MVAR", "MVA", "AMPS", "PCTRT1", "RATE1"]):
    """Extrae datos de una rama (línea o transformador 2 devueltos)."""
    results = {}
    
    # Flujo complejo (MW, MVAR, MVA)
    ierr, mva = psspy.brnflo(ibus, jbus, ckt)
    if ierr == 0:
        results["MW"] = mva.real
        results["MVAR"] = mva.imag
        results["MVA"] = abs(mva)
    
    # Otros datos mediante brnmsc y brndat
    for var in variables:
        if var in ["MW", "MVAR", "MVA"]: continue
        
        # Intentamos brnmsc primero, luego brndat
        ierr, val = psspy.brnmsc(ibus, jbus, ckt, var)
        if ierr != 0:
            ierr, val = psspy.brndat(ibus, jbus, ckt, var)
            
        if ierr == 0:
            results[var] = val
            
    return results


def get_3w_transformer_data(ibus, jbus, kbus, ckt, variables=["MW", "MVAR", "MVA", "AMPS", "PCTRT1", "RATEA"]):
    """Extrae datos de un transformador trifásico (3-winding)."""
    results = {}
    
    ierr, mva = psspy.wnddt2(ibus, jbus, kbus, ckt, "FLOW")
    if ierr == 0:
        results["MW"] = mva.real
        results["MVAR"] = mva.imag
        results["MVA"] = abs(mva)
        
    for var in variables:
        if var in ["MW", "MVAR", "MVA"]: continue
        ierr, val = psspy.wnddat(ibus, jbus, kbus, ckt, var)
        if ierr == 0:
            results[var] = val
            
    return results


def get_load_data(bus_id, load_id, variables=["PL", "QL"]):
    """Extrae datos de una carga."""
    results = {}
    ierr, mva = psspy.loddt2(bus_id, load_id, "ACT", "TOTAL")
    if ierr == 0:
        results["PL"] = mva.real
        results["QL"] = mva.imag
    return results


def get_machine_data(bus_id, mac_id, variables=["PG", "QG"]):
    """Extrae datos de una m�quina."""
    results = {}
    ierr, mva = psspy.macdt2(bus_id, mac_id, "PQ")
    if ierr == 0:
        results["PG"] = mva.real
        results["QG"] = mva.imag
    return results
