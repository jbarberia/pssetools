


import os
import pandas as pd


def otdf(case, sub_file, mon_file, con_file, temp_dir="."):
    import psspy
    import arrbox.dfax_pp
    psspy.psseinit()

    ierr = psspy.case(case)
    if ierr != 0:
        return
    
    base, _ = os.path.splitext(os.path.basename(case))
    dfx_file = os.path.join(temp_dir, base + ".dfx")
    ierr = psspy.dfax_2([1, 0, 1], sub_file, mon_file, con_file, dfx_file)

    dfxobj = arrbox.dfax_pp.DFAX_PP(dfx_file)    
    smryobj = dfxobj.summary()
    otdfobj = dfxobj.otdf_factors()

    otdf = pd.DataFrame(
        data=otdfobj.factor,
        index=otdfobj.colabel,
        columns=otdfobj.melement,
    )
    otdf = otdf.T
    otdf = otdf[[c for c in otdf.columns if c]]
    otdf.index.name = "ELEMENTO"
    otdf.index = otdf.index.str.strip()
    otdf = otdf.reset_index()
    otdf.insert(0, "CASO", base)

    return otdf
