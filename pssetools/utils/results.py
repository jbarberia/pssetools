import os
import pandas as pd


def get_results_from_case(mon_file):
    "archivo de monitoreo como TSV"
    import psspy
    df = pd.read_csv(mon_file, sep="\t", encoding="latin-1", header=0, skiprows=0, skipinitialspace=True, dtype=str)
    df.columns = ["ELEMENTO", "ID1", "ID2", "ID3", "ID4", "DESCRIPCION"]

    data = []
    for i, row in df.iterrows():        
        if row["ELEMENTO"] == "BU":
            data.extend(get_bus_data(row))

        elif row["ELEMENTO"] in ["LII", "TR", "SYS"]:
            data.extend(get_branch_data(row))

        elif row["ELEMENTO"] in ["T3"]:
            data.extend(get_3w_transformer_data(row))

        elif row["ELEMENTO"] in ["LO"]:
            data.extend(get_load_data(row))
        
        elif row["ELEMENTO"] in ["ME"]:
            data.extend(get_machine_data(row))

    df = pd.DataFrame(data)
    return df
            

def get_bus_data(row):
    import psspy
    ierr, pu = psspy.busdat(int(row["ID1"]), "PU")
    ierr, base = psspy.busdat(int(row["ID1"]), "BASE")

    return [
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": None,
            "ID3": None,
            "ID4": None,            
            "VARIABLE": "VM",
            "VALOR": pu,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": None,
            "ID3": None,
            "ID4": None,
            "VARIABLE": "BASE",
            "VALOR": base,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": None,
            "ID3": None,
            "ID4": None,
            "VARIABLE": "DESCRIPCION",
            "VALOR": row["DESCRIPCION"],
        }        
    ]
    
    
def get_branch_data(row):
    import psspy
    ibus, jbus, ckt = int(row["ID1"]), int(row["ID2"]), row["ID3"]
    ierr, mva    = psspy.brnflo(ibus, jbus, ckt)
    if ierr != 0: 
        return []
    ierr, amps   = psspy.brnmsc(ibus, jbus, ckt, "AMPS")
    ierr, pctrta = psspy.brnmsc(ibus, jbus, ckt, "PCTRTA")
    ierr, rate1  = psspy.brndat(ibus, jbus, ckt, "RATE1")

    return [
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": None,
            "VARIABLE": "MVAr",
            "VALOR": mva.imag,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": None,
            "VARIABLE": "MW",
            "VALOR": mva.real,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": None,
            "VARIABLE": "MVA",
            "VALOR": abs(mva),
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": None,
            "VARIABLE": "AMPS",
            "VALOR": amps,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": None,
            "VARIABLE": "PCTRTA",
            "VALOR": pctrta,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": None,
            "VARIABLE": "RATE1",
            "VALOR": rate1,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": None,
            "VARIABLE": "DESCRIPCION",
            "VALOR": row["DESCRIPCION"],
        },
    ]


def get_3w_transformer_data(row):
    import psspy
    ibus, jbus, kbus, ckt = int(row["ID1"]), int(row["ID2"]), int(row["ID3"]), row["ID4"]    
    ierr, mva    = psspy.wnddt2(ibus, jbus, kbus, ckt, "FLOW")
    ierr, amps   = psspy.wnddat(ibus, jbus, kbus, ckt, "AMPS")
    ierr, pctrta = psspy.wnddat(ibus, jbus, kbus, ckt, "PCTRTA")
    ierr, rate1  = psspy.wnddat(ibus, jbus, kbus, ckt, "RATEA")

    return [
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": row["ID4"],
            "VARIABLE": "MVAr",
            "VALOR": mva.real,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": row["ID4"],
            "VARIABLE": "MW",
            "VALOR": mva.imag,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": row["ID4"],
            "VARIABLE": "MVA",
            "VALOR": abs(mva),
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": row["ID4"],
            "VARIABLE": "AMPS",
            "VALOR": amps,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": row["ID4"],
            "VARIABLE": "PCTRTA",
            "VALOR": pctrta,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": row["ID4"],
            "VARIABLE": "RATE1",
            "VALOR": rate1,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": row["ID3"],
            "ID4": row["ID4"],
            "VARIABLE": "DESCRIPCION",
            "VALOR": row["DESCRIPCION"],
        },
    ]

def get_load_data(row):
    import psspy
    ierr, mva = psspy.loddt2(int(row["ID1"]), row["ID2"], "ACT", "TOTAL")
    if ierr != 0: return []

    return [
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": None,
            "ID4": None,            
            "VARIABLE": "PL",
            "VALOR": mva.real,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": None,
            "ID4": None,            
            "VARIABLE": "QL",
            "VALOR": mva.imag,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": None,
            "ID4": None,
            "VARIABLE": "DESCRIPCION",
            "VALOR": row["DESCRIPCION"],
        }        
    ]


def get_machine_data(row):
    import psspy
    ierr, mva = psspy.macdt2(int(row["ID1"]), row["ID2"], "PQ")

    return [
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": None,
            "ID4": None,            
            "VARIABLE": "PG",
            "VALOR": mva.real,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": None,
            "ID4": None,            
            "VARIABLE": "QG",
            "VALOR": mva.imag,
        },
        {
            "ELEMENTO": row["ELEMENTO"],
            "ID1": row["ID1"],
            "ID2": row["ID2"],
            "ID3": None,
            "ID4": None,
            "VARIABLE": "DESCRIPCION",
            "VALOR": row["DESCRIPCION"],
        }        
    ]
