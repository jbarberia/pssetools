import os
import argparse
import pssetools
import pandas as pd
from pssetools.utils import set_psse_path


def estatico(case, config, folder):
    """
    Corre la rutina ACCC, tabula los resultados y desempaca los zip en una carpeta.
    
    Args:
        case (str): Ruta al archivo de caso PSS/E (.sav).
        config (str or dict): Archivo de configuracion o diccionario con parametros.
        folder (str): Ruta al directorio donde depositar los archivos generados.

    Returns:
        tuple: (dff, dfv) donde:
            - dff (pd.DataFrame): DataFrame con los resultados de flujos.
            - dfv (pd.DataFrame): DataFrame con los resultados de tensiones.
    """
    set_psse_path()
    import psspy
    psspy.psseinit()

    config = pssetools.get_config(config)
    base = os.path.basename(case).replace(".sav", "")
    tmp_zipfile = os.path.join(os.path.expanduser("~"), base + ".zip")
    
    if not os.path.isdir(folder):
        os.makedirs(folder)

    psspy.case(case)
    
    func = psspy.dfax_2
    dfax_kwargs = pssetools.get_kwargs(func, config)
    dfax_kwargs["dfxfile"] = "{}/{}.dfx".format(folder, base)
    ierr = func(**dfax_kwargs)

    func = psspy.accc_with_dsp_3
    accc_kwargs = pssetools.get_kwargs(func, config)
    accc_kwargs["dfxfile"] = dfax_kwargs["dfxfile"]
    accc_kwargs["accfile"] = "{}/{}.acc".format(folder, base)
    accc_kwargs["zipfile"] = tmp_zipfile     
    ierr = func(**accc_kwargs)

    func = pssetools.accc_unzip
    accc_unzip_kwargs = pssetools.get_kwargs(func, config)
    accc_unzip_kwargs["zipfile"] = tmp_zipfile
    accc_unzip_kwargs["folder"] = os.path.join(folder, base)
    func(**accc_unzip_kwargs)
    os.remove(tmp_zipfile)

    func = pssetools.accc_df
    accc_df_kwargs = pssetools.get_kwargs(func, config)
    accc_df_kwargs["accfile"] = accc_kwargs["accfile"]
    dff, dfv = func(**accc_df_kwargs)

    return dff, dfv

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Corre rutina ACCC estático, tabula resultados y extrae los ZIPs."
    )
    
    parser.add_argument(
        "-c", "--case", 
        nargs="+", 
        required=True, 
        help="Ruta al archivo (o archivos) .sav separados por espacio."
    )
    
    parser.add_argument(
        "-k", "--config", 
        required=True, 
        help="Ruta al archivo de configuración (o nombre del diccionario local)."
    )
    
    parser.add_argument(
        "-f", "--folder", 
        required=True, 
        help="Carpeta de destino donde se depositarán los resultados."
    )
    
    args = parser.parse_args()

    results = []
    for c in args.case:
        res = estatico(c, args.config, args.folder)
        results.append(res)
        
    dff_list, dfv_list = zip(*results)
    excel_path = "{}/resultados.xlsx".format(args.folder)
    with pd.ExcelWriter(excel_path) as writer:
        pd.concat(list(dff_list)).to_excel(writer, "flujos", index=False)
        pd.concat(list(dfv_list)).to_excel(writer, "tensiones", index=False)
        
