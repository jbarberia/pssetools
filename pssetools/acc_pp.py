from __future__ import print_function
from . import get_config
from . import pss_activity
import os
import pandas as pd
from arrbox.accc_pp import CONTINGENCY_PP

@pss_activity
def run(acc, frp, vrp, config, **kwargs):
    """Post-processes ACCC contingency analysis results.

    Extracts flow and voltage data from an .acc file and saves them to
    tab-separated reports.

    Args:
        acc: Input ACCC results file (.acc).
        frp: Output flow report file (.frp).
        vrp: Output voltage report file (.vrp).
        config: Configuration dictionary or path to configuration file.
        **kwargs: Additional arguments.

    Returns:
        0 on success.
    """
    config = get_config(config)    
    rate = config["ARRBOX"]["RATING"]

    case = os.path.basename(acc).replace(".acc", "")
    accobj = CONTINGENCY_PP(acc)
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
            "ELEMENTO":     summary.melement,
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
    df_flow.to_csv(
        frp,
        float_format=config["ARRBOX"]["NUMFMT_FLOW"],
        index=False,
        sep="	"
    )
    
    df_volts = pd.concat(volt_data)
    df_volts.to_csv(
        vrp,
        float_format=config["ARRBOX"]["NUMFMT_VOLT"],
        index=False,
        sep="	"
    )
    
    return 0
