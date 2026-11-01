# coding: latin-1
"""
Fusionador de casos
-------------------

El archivo de límites debe especificarse con el mapstring correspondiente al
elemento usado.

Por ejemplo para seccionar el NOA usar como límite:

8000 2620
LII 5016 8011 1
LII 6006 8004 1

case_1 contiene la isla con la barra 8000
case_2 contiene la isla con la barra 2620


"""

from __future__ import absolute_import, division, print_function, unicode_literals
import os
from pssetools.programs import BaseProgram
from pssetools.utils.topology import (
    parse_boundaries,
    get_island_buses,
    get_boundary_buses,
    verify_island_isolation,
)


class FusionadorDeCaso(BaseProgram):
    order = 60

    def get_parameters(self):
        """Returns the parameter definitions and characteristics for ACCC."""
        return [
            {
                "name": "case_1",
                "label": "Working Case 1 (.sav):",
                "type": "file",
                "default": "",
            },
            {
                "name": "case_2",
                "label": "Working Case 2 (.sav):",
                "type": "file",
                "default": "",
            },
            {
                "name": "ofile",
                "label": "Output File (.sav):",
                "type": "file",
                "default": "",
            },
            {
                "name": "limit_file",
                "label": "Limites (.txt):",
                "type": "file",
                "default": "",
            },            
        ]


    def run(self, parsed_params):
        self._run(**parsed_params)


    def _run(self, case_1, case_2, ofile, limit_file, output_dir=".", temp_dir="."):
                
        psspy = self.psspy
        psspy.psseinit()
        _i = psspy.getdefaultint()
        _f = psspy.getdefaultreal()
        _s = psspy.getdefaultchar()

        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # lee fronteras
        bus_1, bus_2, fronteras = parse_boundaries(limit_file)

        # extracto del case_1
        psspy.case(case_1)
        isla_1 = get_island_buses(psspy, bus_1, fronteras)
        if not verify_island_isolation(psspy, bus_1, bus_2):
            return

        psspy.case(case_1)
        psspy.bsys(0, 0, [0.0, 525.0], 0, [], len(isla_1), isla_1, 0, [], 0, [])
        raw_path = os.path.join(temp_dir, "isla_1.raw")
        seq_path = os.path.join(temp_dir, "isla_1.seq")
        psspy.rawd_2(0, 0, [1, 1, 1, 0, 0, 0, 1], 0, raw_path)
        psspy.rwsq_2(0, 0, [1, 1, 1, 0, 1], 0, seq_path)

        # barras a eliminar del case_2
        psspy.case(case_2)
        isla_1 = get_island_buses(psspy, bus_1, fronteras)
        if not verify_island_isolation(psspy, bus_1, bus_2):
            return
        
        barras_frontera = get_boundary_buses(psspy, fronteras)
        barras_a_eliminar = [bus for bus in isla_1 if bus not in barras_frontera]

        script = os.path.join(temp_dir, "elimina_isla.py")
        psspy.startrecording(1, script)
        psspy.bsys(1, 0, [0.0, 525.0], 0, [], len(barras_a_eliminar), barras_a_eliminar, 0, [], 0, [])
        psspy.extr(1, 0, [0, 0])
        ierr = psspy.stoprecording()

        # corta el case_2 y le pega la parte del subsistema del case_1
        psspy.case(case_2)
        locals_vars = {
            "psspy": psspy,
            "_i" : psspy.getdefaultint(),
            "_f" : psspy.getdefaultreal(),
            "_s" : psspy.getdefaultchar(),
        }
        with open(script) as code:
            exec(code.read(), locals_vars)

        psspy.read(0, raw_path)
        psspy.resqversion("34", seq_path)
        psspy.save(ofile)
        print("Caso fusionado exitosamente en: {}".format(ofile))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Fusionador de casos\n"
            "-------------------\n"
            "Fusiona dos casos PSS/E a partir de un archivo de limites.\n\n"
            "El archivo de limites debe especificarse con el mapstring correspondiente al\n"
            "elemento usado. Por ejemplo para seccionar el NOA:\n\n"
            "  8000 2620\n"
            "  LII 5016 8011 1\n"
            "  LII 6006 8004 1\n\n"
            "case_1 contiene la isla con la barra 8000\n"
            "case_2 contiene la isla con la barra 2620"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--case-1",
        required=True,
        dest="case_1",
        help="Ruta al caso 1 (.sav)."
    )

    parser.add_argument(
        "--case-2",
        required=True,
        dest="case_2",
        help="Ruta al caso 2 (.sav)."
    )

    parser.add_argument(
        "-f", "--ofile",
        required=True,
        help="Ruta del archivo de salida (.sav)."
    )

    parser.add_argument(
        "-l", "--limit-file",
        required=True,
        dest="limit_file",
        help="Ruta al archivo de limites (.txt)."
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

    program = FusionadorDeCaso()
    program._run(
        case_1=args.case_1,
        case_2=args.case_2,
        ofile=args.ofile,
        limit_file=args.limit_file,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
