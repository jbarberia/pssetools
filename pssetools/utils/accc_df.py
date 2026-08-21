# coding: latin-1
import os
import pandas as pd


def accc_df(accfile, **kwargs):
    """Post-processes ACCC contingency analysis results.

    Extracts flow and voltage data from an .acc file and return dataframes.

    Args:
        accfile (str): Input ACCC results file (.acc).
        **kwargs: Additional keyword arguments.

    Returns:
        int: 0 on success.
    """
    from arrbox.accc_pp import CONTINGENCY_PP
    rate = "a"

    case = os.path.basename(accfile).replace(".acc", "")
    accobj = CONTINGENCY_PP(accfile)
    summary = accobj.summary()    
    flow_data = []
    volt_data = []

    for colabel in summary.colabel:
        solnobj  = accobj.solution(colabel=colabel)            
        n_interfaces = len(summary.melement) - len(solnobj.ampflow)
        
        flow_data.append(pd.DataFrame({
            "CASO": case,
            "CONVERGENCIA": solnobj["cnvcond"],
            "CONTINGENCIA": colabel,
            "ELEMENTO":     [x.strip() for x in summary.melement],
            "P [MW]":       solnobj.brnpflow,        
            "Q [MVAR]":     solnobj.brnqflow,
            "S [MVA]":      list(map(abs, solnobj.mvaflow)),
            "I [as MVA]":   solnobj.ampflow + [0] * n_interfaces,        
            "LIMITE [MVA]": summary.rating[rate],        
        }))
        
        volt_data.append(pd.DataFrame({
            "CASO": case,
            "CONVERGENCIA": solnobj["cnvcond"],
            "CONTINGENCIA": colabel,
            "ELEMENTO":     summary.mvbuslabel,
            "PU":        solnobj.volts,
        }))
        
                    
    df_flow = pd.concat(flow_data)
    df_volts = pd.concat(volt_data)
    
    return df_flow, df_volts
