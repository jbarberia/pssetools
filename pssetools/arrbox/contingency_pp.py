from .. import psse34
from .. import argument_parser
from .. import get_config

import os
import pandas as pd
from arrbox.accc_pp import CONTINGENCY_PP


def run(acc, frp, vrp, config, **kwargs):
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
        sep="\t"
    )
    
    df_volts = pd.concat(volt_data)
    df_volts.to_csv(
        vrp,
        float_format=config["ARRBOX"]["NUMFMT_VOLT"],
        index=False,
        sep="\t"
    )
        
        
    
    
    




if __name__ == "__main__":
    args_specs = {
        "acc": {"type": str},     
        "frp": {"type": str},     
        "vrp": {"type": str},     
        "config": {"type": str},     
    }    
    args = argument_parser(args_specs)
    run(**args)
