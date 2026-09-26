# coding: latin-1
"""
Utilidad para inicializar el caso
---------------------------------

1. Convierte el caso.
2. Incializa la base de estudios.
3. Captura las condiciones sospechosas.
4. Genera un reporte para eso.
5. Abre el caso original.
6. Genera un subsistema con las condiciones sospechosas.

"""

import os
import re
import sys
import psse34
import psspy
from pssetools.programs import BaseProgram


class DynStrtDebug(BaseProgram):
    """Base class for all PSS/E automation modules."""

    def get_parameters(self):
        "Returns the parameter definitions"
        return [
            {
                "name": "case",
                "label": "Working Case (.sav):",
                "type": "file",
                "default": "",
                "editable": False,
            },
            {
                "name": "snap",
                "label": "Snapshot (.snp):",
                "type": "file",
                "default": "",
                "editable": False,
            },
            {
                "name": "py",
                "label": "Convload (.py):",
                "type": "file",
                "default": "",
                "editable": True,
            },
            {
                "name": "dll_files",
                "label": "DLL Files (.dll):",
                "type": "multi_file",
                "default": "",
            },
            {
                "name": "drop_library",
                "label": "Quitar dll luego de inicialización:",
                "type": "bool",
                "default": False,
            },
        ]


    def run(self, parsed_params):
        self.run_strt_debug(**parsed_params)


    def run_strt_debug(self, case, snap, py, dll_files, drop_library, **kwargs):
        outpur_dir = kwargs.get("output_dir", ".")
        temp_dir = kwargs.get("temp_dir", ".")

        psspy.psseinit()
        _i = psspy.getdefaultint()
        _f = psspy.getdefaultreal()
        _s = psspy.getdefaultchar()

        ierr = psspy.case(case)
        if ierr != 0:
            raise ValueError("Error al cargar el caso")

        ierr = psspy.rstr(snap)
        if ierr != 0:
            raise ValueError("Error al cargar el snapshot")

        for library in dll_files:
            psspy.addmodellibrary(library)

        locals_vars = {
            "psspy": psspy,
            "_i" : psspy.getdefaultint(),
            "_f" : psspy.getdefaultreal(),
            "_s" : psspy.getdefaultchar(),
        }
        if py.endswith(".py"):
            with open(py) as f:
                code = f.read()
                exec(code, locals_vars)

        t_device = os.path.join(temp_dir, "incializacion.pdv")
        psspy.clearprogressoutput()
        ierr = psspy.t_progress_output(2, t_device, [0, 0])

        ierr = psspy.strt_2([1, 1], "") 

        ierr = psspy.t_progress_output(6)

        with open(t_device, "r") as f:
            psspy.beginreport()
            psspy.report(f.read())

        psspy.case(case)

        if drop_library:
            for library in dll_files:
                print(library)
                psspy.dropmodellibrary(os.path.abspath(library))

        if not psspy.okstrt() == 0:            
            report = self._get_initial_conditions_suspect(t_device)        
            psspy.beginreport()
            psspy.report(report)

            buses = self._get_buses_with_suspect_models(report)        
            psspy.bsys(0,0,[_f,_f],0,[],len(buses),buses,0,[],0,[])
            
        psspy.refreshgui()
        psspy.refreshdiagfile()
        


    def _get_initial_conditions_suspect(self, filename):
        """Extracts 'INITIAL CONDITIONS SUSPECT' from a progress output file.

        Parses the input file for a specific pattern of suspected initial conditions
        and overwrites the file with only that information if found.

        Args:
            filename (str): The path to the progress output file to parse.
        """

        
        with open(filename) as f:
            content = f.read()        
        
        pattern = r"INITIAL CONDITIONS SUSPECT:\n(.*)\n^"
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            initial_conditions = match.group(1)        
            return initial_conditions

        return "INITIAL CONDITIONS CHECK O.K."

    def _get_buses_with_suspect_models(self, report):
        pattern = r"K..\s*?([0-9]{1,6})\s.*?"
        match = re.findall(pattern, report)
        return [int(m) for m in match]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Utilidad para inicializar el caso\n"
            "---------------------------------\n"
            "1. Convierte el caso.\n"
            "2. Inicializa la base de estudios.\n"
            "3. Captura las condiciones sospechosas.\n"
            "4. Genera un reporte para eso.\n"
            "5. Abre el caso original.\n"
            "6. Genera un subsistema con las condiciones sospechosas."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-c", "--case",
        required=True,
        help="Ruta al caso de trabajo (.sav)."
    )

    parser.add_argument(
        "-s", "--snap",
        required=True,
        help="Ruta al snapshot (.snp)."
    )

    parser.add_argument(
        "--py",
        required=False,
        default="",
        help="Ruta al archivo de conversion de carga (convload) (.py)."
    )

    parser.add_argument(
        "-d", "--dll-files",
        nargs="+",
        required=False,
        default=[],
        dest="dll_files",
        help="Rutas a las librerias de usuario (.dll)."
    )

    parser.add_argument(
        "--drop-library",
        action="store_true",
        default=False,
        dest="drop_library",
        help="Si se especifica, quita las dll luego de la inicializacion."
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

    program = DynStrtDebug()
    program.run_strt_debug(
        case=args.case,
        snap=args.snap,
        py=args.py,
        dll_files=args.dll_files,
        drop_library=args.drop_library,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
