import argparse
from pssetools import dll


def main():
    parser = argparse.ArgumentParser(
        description="Compila y crea una DLL de modelos de usuario en PSS/E."
    )
    
    parser.add_argument(
        "-d", "--dll", 
        required=False, 
        default="usrdll.dll",
        help="Archivo DLL a crear."
    )
    
    parser.add_argument(
        "-s", "--sources",
        nargs="+",  # Acepta uno o más archivos separados por espacio
        required=True,
        help="Lista de archivos fuente, objetos y librerías (ej: mod1.f90 mod2.obj)."
    )
    
    parser.add_argument(
        "-c", "--config",
        required=False,
        help="Ruta al archivo de configuración (JSON o YAML).",
    )
    
    args = parser.parse_args()
    
    # Se desempaquetan los argumentos de argparse como un diccionario
    # vars(args) devolverá {'dll': ..., 'sources': [...], 'config': ...}
    dll(**vars(args))
    
    print("Proceso de DLL finalizado exitosamente.")


if __name__ == "__main__":
    main()
