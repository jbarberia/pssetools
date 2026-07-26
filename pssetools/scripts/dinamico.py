


import os
import argparse
import pssetools


def dinamico(cnv, snp, out, dll, py, config=None, folder=None):
    folder = folder or "."
    
    # redirige todo a folder
    out = os.path.basename(out)
    out = os.path.join(folder, out)
    
    # corre la simulacion
    pssetools.dyn(cnv, snp, out, dll, py, config)
    
    # exporta los datos a un csv o algo procesable
    base_name, _ = os.path.splitext(out)
    outfile = base_name + ".tsv"
    pssetools.dyn_pp(out, outfile, config)

    return 0

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ejecuta una simulación dinámica de PSS/E y exporta los resultados a CSV."
    )
    
    parser.add_argument(
        "-c", "--cnv", 
        required=True, 
        help="Ruta al archivo convertido de PSS/E (.cnv)."
    )
    
    parser.add_argument(
        "-s", "--snp", 
        required=True, 
        help="Ruta al archivo Snapshot (.snp)."
    )
    
    parser.add_argument(
        "-o", "--out", 
        required=True, 
        help="Nombre/Ruta del archivo de salida de la simulación (.out)."
    )
    
    parser.add_argument(
        "-d", "--dll", 
        nargs="+", 
        required=True, 
        help="Lista de librerías DLL requeridas (separadas por espacio)."
    )
    
    parser.add_argument(
        "-p", "--py", 
        nargs="+", 
        required=True, 
        help="Scripts en Python de simulación a ejecutar (separados por espacio)."
    )
    
    parser.add_argument(
        "-k", "--config", 
        required=False, 
        default=None,
        help="Archivo o diccionario de configuración (opcional)."
    )
    
    parser.add_argument(
        "-f", "--folder", 
        required=False, 
        default=None,
        help="Carpeta de destino donde se depositarán los resultados."
    )
    
    args = parser.parse_args()
    dinamico(
        cnv=args.cnv,
        snp=args.snp,
        out=args.out,
        dll=args.dll,
        py=args.py,
        config=args.config,
        folder=args.folder
    )
