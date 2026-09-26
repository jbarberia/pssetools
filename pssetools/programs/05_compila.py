# coding: latin-1
"""
Compila
-------

Genera la compilación por medio del PSSE Env Manager.

Debido a que puede estar instalada una versión más moderna del mismo, ejecuta 
la compilacion como un subproceso.


"""

import os
import subprocess
from pssetools.programs import BaseProgram


class CompilaProgram(BaseProgram):
    
    def get_parameters(self):
        "Returns the parameter definitions"
        return [
            {
                "name": "python_exe",
                "label": "Python EXE:",
                "type": "file",
                "default": "C:/Python314/python.exe", # Ajusta este default al de tu empresa
                "editable": False,
            },
            {
                "name": "sources",
                "label": "Source Files (.for, .flx, .lib):",
                "type": "multi_file",
                "default": "",
                "editable": True,
            },
            {
                "name": "dll",
                "label": "Output (.dll):",
                "type": "file",
                "default": "",
                "editable": False,
            },                        
        ]

    def run(self, parsed_params):
        self.compilacion(**parsed_params)

    def compilacion(self, python_exe, sources, dll, temp_dir=".", output_dir="."):

        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.abspath(os.path.join(base_dir, "..", "utils", "dll.py"))

        # comando cli
        cmd = [python_exe, script_path, "--dll", str(dll), "--sources"] + list(sources)

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_data, stderr_data = process.communicate()
            
            out_str = stdout_data.decode("utf-8", errors="replace") if stdout_data else ""
            err_str = stderr_data.decode("utf-8", errors="replace") if stderr_data else ""

            if out_str:
                print(out_str)
            
            if process.returncode != 0:
                print("--- ERRORES DEL COMPILADOR ---")
                print(err_str)
                print("El proceso terminó con código: {}".format(process.returncode))

        except Exception as e:
            print("Error al intentar lanzar el subproceso: {}".format(e))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Compila\n"
            "-------\n"
            "Genera la compilacion por medio del PSSE Env Manager.\n"
            "Ejecuta la compilacion como un subproceso para compatibilidad con versiones modernas."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--python-exe",
        dest="python_exe",
        default="C:/Python314/python.exe",
        help="Ruta al ejecutable de Python (por defecto: C:/Python314/python.exe)."
    )

    parser.add_argument(
        "-s", "--sources",
        nargs="+",
        required=True,
        help="Archivos fuente a compilar (.for, .flx, .lib)."
    )

    parser.add_argument(
        "-d", "--dll",
        required=True,
        help="Ruta de salida de la libreria compilada (.dll)."
    )

    parser.add_argument(
        "-o", "--output-dir",
        dest="output_dir",
        default=".",
        help="Carpeta de destino de los resultados (por defecto: directorio actual)."
    )

    parser.add_argument(
        "-t", "--temp-dir",
        dest="temp_dir",
        default=".",
        help="Carpeta de archivos temporales (por defecto: directorio actual)."
    )

    args = parser.parse_args()

    program = CompilaProgram()
    program.compilacion(
        python_exe=args.python_exe,
        sources=args.sources,
        dll=args.dll,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
