# coding: latin-1
"""
Genera un snapshot
------------------

En idv se pasa el response file con los canales a sumar.
En py se pasa un python con las opciones tipicas a usar.

psspy.setnetfrq() # ya incluida
psspy.set_relang(1,2610,"1")

"""

import os
from pssetools.programs import BaseProgram
from pssetools.utils.snp import create_snapshot


class Snapshot(BaseProgram):
    
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
                "name": "dyr_files",
                "label": "Dyre files (.dyr):",
                "type": "multi_file",
                "default": "",
            },
            {
                "name": "conec",
                "label": "CONEC (.flx):",
                "type": "file",
                "default": "",
                "editable": True,
            },
            {
                "name": "conet",
                "label": "CONET (.flx):",
                "type": "file",
                "default": "",
                "editable": True,
            },
            {
                "name": "idv",
                "label": "Canales (.idv):",
                "type": "file",
                "default": "",
                "editable": True,
            },
            {
                "name": "py",
                "label": "Configuración (.py):",
                "type": "file",
                "default": "",
                "editable": True,
            },
            {
                "name": "snapshot",
                "label": "Snapshot (.snp):",
                "type": "file",
                "default": "",
                "editable": False,
            },
        ]

    def run(self, parsed_params):
        self.run_snapshot(**parsed_params)

    def run_snapshot(self, case, dyr_files, conec, conet, idv, py, snapshot, output_dir=".", temp_dir="."):
        psspy = self.psspy
        psspy.psseinit()

        ierr = create_snapshot(
            sav=case,
            snp=snapshot,
            dyr=dyr_files,
            cc=conec,
            ct=conet,
        )

        if idv and os.path.exists(idv):
            psspy.runrspnsfile(idv)

        locals_vars = {
            "psspy": psspy,
            "_i" : psspy.getdefaultint(),
            "_f" : psspy.getdefaultreal(),
            "_s" : psspy.getdefaultchar(),
        }
        if py and os.path.exists(py):
             with open(py) as f:
                code = f.read()
                exec(code, locals_vars)

        # configuracion tipica
        _i = psspy.getdefaultint()
        _f = psspy.getdefaultreal()
        _s = psspy.getdefaultchar()
        psspy.dynamics_solution_param_2([250,_i,_i,_i,_i,_i,_i,_i],[ 0.25,_f, 0.002,_f,_f,_f,_f,_f])
        psspy.set_netfrq(1)

        ierr = psspy.snap(sfile=snapshot)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Genera un snapshot\n"
            "------------------\n"
            "En idv se pasa el response file con los canales a sumar.\n"
            "En py se pasa un python con las opciones tipicas a usar."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-c", "--case",
        required=True,
        help="Ruta al caso de trabajo (.sav)."
    )

    parser.add_argument(
        "-d", "--dyr-files",
        nargs="+",
        required=True,
        dest="dyr_files",
        help="Rutas a los archivos de datos dinamicos (.dyr)."
    )

    parser.add_argument(
        "--conec",
        required=False,
        default="",
        help="Ruta al archivo CONEC (.flx)."
    )

    parser.add_argument(
        "--conet",
        required=False,
        default="",
        help="Ruta al archivo CONET (.flx)."
    )

    parser.add_argument(
        "--idv",
        required=False,
        default="",
        help="Ruta al archivo de canales (.idv)."
    )

    parser.add_argument(
        "--py",
        required=False,
        default="",
        help="Ruta al archivo de configuracion (.py)."
    )

    parser.add_argument(
        "-s", "--snapshot",
        required=True,
        help="Ruta de salida del snapshot (.snp)."
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

    program = Snapshot()
    program.run_snapshot(
        case=args.case,
        dyr_files=args.dyr_files,
        conec=args.conec,
        conet=args.conet,
        idv=args.idv,
        py=args.py,
        snapshot=args.snapshot,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
