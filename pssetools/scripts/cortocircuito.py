import os
import argparse
import pssetools
from pssetools.utils import set_psse_path


def cortocircuito(case, config=None, folder=None):
    set_psse_path()
    import psspy
    psspy.psseinit()
    
    config = pssetools.get_config(config)
    folder = folder or "."

    if not os.path.isdir(folder):
        os.makedirs(folder)

    psspy.case(case)

    func = pssetools.ascc
    kwargs = pssetools.get_kwargs(func, config)
    kwargs["sav"] = case
    kwargs["config"] = config
    df = func(**kwargs)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ejecuta análisis de cortocircuito en casos PSS/E."
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

    folder = args.folder or "."
    for c in args.case:
        cortocircuito(c, args.config, folder)

