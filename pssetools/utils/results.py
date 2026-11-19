# coding: latin-1
import os
import pandas as pd
import psse34
import psspy


def _extract_bus(row):
    return get_bus_data(int(row[1]))


def _extract_branch(row):
    return get_branch_data(int(row[1]), int(row[2]), str(row[3]))


def _extract_3w(row):
    return get_3w_transformer_data(int(row[1]), int(row[2]), int(row[3]), str(row[4]))

def _extract_load(row):
    return get_load_data(int(row[1]), str(row[2]))


def _extract_machine(row):
    return get_machine_data(int(row[1]), str(row[2]))


DISPATCHER = {
    "BU": _extract_bus,
    "LII": _extract_branch,
    "TR": _extract_branch,
    "SYS": _extract_branch,
    "T3": _extract_3w,
    "LO": _extract_load,
    "ME": _extract_machine,
}

def get_results_from_case(mon_file):
    """
    Lee un archivo de monitoreo TSV y extrae datos de PSS/E para cada elemento.
    """
    if not os.path.exists(mon_file):
        return pd.DataFrame()

    df_mon = pd.read_csv(
        mon_file,
        sep=b"\t" if bytes is str else "\t",
        encoding="latin-1",
        header=0,
        skiprows=0,
        skipinitialspace=True,
        dtype=str,
    )
    expected_cols = ["ELEMENTO", "ID1", "ID2", "ID3", "ID4", "DESCRIPCION"]
    if len(df_mon.columns) >= len(expected_cols):
        df_mon = df_mon.iloc[:, :len(expected_cols)]
        df_mon.columns = expected_cols
    else:
        # Completar columnas faltantes si el TSV tuviese menos de 6
        for col in expected_cols[len(df_mon.columns):]:
            df_mon[col] = ""

    # Reemplazar NaN por cadenas vacías para evitar floats
    df_mon = df_mon.fillna("")

    all_data = []
    for row in df_mon.itertuples(index=False, name=None):
        elem = row[0]
        func = DISPATCHER.get(elem)
        if not func:
            continue

        try:
            res = func(row)
        except (ValueError, TypeError, IndexError):
            continue

        if not res:
            continue

        id1, id2, id3, id4, desc = row[1], row[2], row[3], row[4], row[5]
        for var, val in res.items():
            all_data.append({
                "ELEMENTO": elem,
                "ID1": id1,
                "ID2": id2,
                "ID3": id3,
                "ID4": id4,
                "VARIABLE": var,
                "VALOR": val,
                "DESCRIPCION": desc,
            })

    if not all_data:
        return pd.DataFrame(columns=[
            "ELEMENTO", "ID1", "ID2", "ID3", "ID4", "VARIABLE", "VALOR", "DESCRIPCION"
        ])

    return pd.DataFrame(all_data)



def get_bus_data(bus_id, variables=["PU", "BASE"]):
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
    if ierr == 0 or ierr == 3:
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


def get_3w_transformer_data(ibus, jbus, kbus, ckt, variables=["MW", "MVAR", "MVA", "AMPS", "PCTRT1", "RATE1"]):
    """Extrae datos de un transformador trifásico (3-winding)."""
    results = {}
    
    ierr, mva = psspy.wnddt2(ibus, jbus, kbus, ckt, "FLOW")
    if ierr == 0 or ierr == 7:
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
    """Extrae datos de una máquina."""
    results = {}
    ierr, mva = psspy.macdt2(bus_id, mac_id, "PQ")
    if ierr == 0:
        results["PG"] = mva.real
        results["QG"] = mva.imag
    return results
