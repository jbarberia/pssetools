import os
import argparse
import pssetools
import pandas as pd
from pssetools.utils import set_psse_path

def factores_de_distribucion(case, config=None, folder=None):
    """genera factores de distribucion para un caso dado

    Args:
        case (str): Ruta al archivo de caso PSS/E (.sav).
        config (str or dict, optional): Archivo de configuracion o diccionario con parametros.
        folder (str, optional): Ruta al directorio donde depositar los archivos generados.

    Returns:
        pd.DataFrame: Dataframe con los factores de distribucion
    """

    set_psse_path()
    import psspy
    import arrbox.dfax_pp
    psspy.psseinit()

    config = pssetools.get_config(config)
    folder = folder or "."
    base = os.path.basename(case).replace(".sav", "")

    if not os.path.isdir(folder):
        os.makedirs(folder)

    psspy.case(case)

    func = psspy.dfax_2
    dfax_kwargs = pssetools.get_kwargs(func, config)
    dfxfile = dfax_kwargs["dfxfile"] = "{}/{}.dfx".format(folder, base)
    ierr = func(**dfax_kwargs)

    dfxobj = arrbox.dfax_pp.DFAX_PP(dfxfile)    
    otdfobj = dfxobj.otdf_factors()

    otdf = pd.DataFrame(
        data=otdfobj.factor,
        index=otdfobj.colabel,
        columns=otdfobj.melement,
    )
    otdf = otdf.T
    otdf = otdf[[c for c in otdf.columns if c]]

    # TODO sumar power shifts

    return otdf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Genera factores de distribución (DFAX/OTDF) para casos PSS/E."
    )

    parser.add_argument(
        "-c", "--case",
        nargs="+", 
        required=True,
        help="Ruta al archivo (o archivos) .sav separados por espacio."
    )

    parser.add_argument(
        "-k", "--config",
        required=False,
        default=None,
        help="Ruta al archivo de configuración (o nombre del diccionario local)."
    )

    parser.add_argument(
        "-f", "--folder",
        required=False,
        default=None,
        help="Carpeta de destino donde se depositarán los resultados."
    )

    args = parser.parse_args()

    results = []
    folder = args.folder or "."
    for c in args.case:
        res = factores_de_distribucion(c, args.config, folder)
        results.append(res)

    excel_path = "{}/factores_de_distribucion.xlsx".format(folder)
    with pd.ExcelWriter(excel_path) as writer:
        pd.concat(results).to_excel(writer, "otdf")
