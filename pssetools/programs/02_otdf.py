"""
OTDF
----

Calcula los factores de distribución y los tabula en otdf.xlsx

Nota: no calcula los shifts, que deben ser sacados del caso base.
Para esto se puede usar la actividad ACCC y su excel de resultados.

"""

import os
import pandas as pd

from pssetools.programs import BaseProgram
from pssetools.utils.otdf import otdf


class OTDFProgram(BaseProgram):

    def get_parameters(self):
        """Returns the parameter definitions and characteristics for ACCC."""
        return [
            {
                "name": "cases",
                "label": "Working Case (.sav):",
                "type": "multi_file",
                "default": "",
            },
            {
                "name": "sub_file",
                "label": "Subsystem (.sub):",
                "type": "file",
                "default": "estudio.sub",
            },
            {
                "name": "mon_file",
                "label": "Monitored (.mon):",
                "type": "file",
                "default": "estudio.mon",
            },
            {
                "name": "con_file",
                "label": "Contingency (.con):",
                "type": "file",
                "default": "estudio.con",
            },
        ]


    def run(self, parsed_params):
        self._run(**parsed_params)


    def _run(self, cases, sub_file, mon_file, con_file, output_dir=".", temp_dir="."):        
        
        otdf_table = []
        for case in cases:
            df = otdf(case, sub_file, mon_file, con_file, temp_dir)
            if not df.empty:
                otdf_table.append(df)

        if otdf_table:
            pd.concat(otdf_table).to_excel(os.path.join(output_dir, "otdf.xlsx"), index=False)
            

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "OTDF\n"
            "----\n"
            "Calcula los factores de distribucion y los tabula en otdf.xlsx\n\n"
            "Nota: no calcula los shifts, que deben ser sacados del caso base.\n"
            "Para esto se puede usar la actividad ACCC y su excel de resultados."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-c", "--cases",
        nargs="+",
        required=True,
        help="Rutas a los casos de trabajo (.sav)."
    )

    parser.add_argument(
        "-s", "--sub-file",
        required=True,
        dest="sub_file",
        default="estudio.sub",
        help="Ruta al archivo de subsistema (.sub)."
    )

    parser.add_argument(
        "-m", "--mon-file",
        required=True,
        dest="mon_file",
        default="estudio.mon",
        help="Ruta al archivo de monitoreados (.mon)."
    )

    parser.add_argument(
        "-n", "--con-file",
        required=True,
        dest="con_file",
        default="estudio.con",
        help="Ruta al archivo de contingencias (.con)."
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

    program = OTDFProgram()
    program._run(
        cases=args.cases,
        sub_file=args.sub_file,
        mon_file=args.mon_file,
        con_file=args.con_file,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
            