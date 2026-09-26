"""
ASCC (Automated Short Circuit Calculation)

Corre un cortocircuito con opciones tipicas y lo tabula en:

ascc.xlsx
"""

import os
import pandas as pd

from pssetools.programs import BaseProgram
from pssetools.utils.ascc import ascc

class ASCCProgram(BaseProgram):

    def get_parameters(self):
        """Returns the parameter definitions and characteristics for ASCC."""
        return [
            {
                "name": "cases",
                "label": "Working Case (.sav):",
                "type": "multi_file",
                "default": "",
                "editable": True,
            },
            {
                "name": "sub_file",
                "label": "Subsystem (.sbsxml):",
                "type": "file",
                "default": "",
                "editable": True,
            },
        ]

    def run(self, parsed_params):
        """Execution entry point called by main application."""
        self.run_ascc(**parsed_params)

    def run_ascc(self, cases, sub_file, output_dir=".", temp_dir="."):
        psspy = self.psspy
        psspy.psseinit()

        ascc_list = []

        for case in cases:
            try:
                df_result = ascc(case, sub_file)
                if df_result is not None and not df_result.empty:
                        ascc_list.append(df_result)

            except Exception as e:
                print("Error processing {}: {}".format(os.path.basename(case), e))

        if ascc_list:
            ofile = os.path.join(output_dir, "ascc.xlsx")
            pd.concat(ascc_list).to_excel(ofile, index=False)
            print("\nASCC Report successfully saved to: {}".format(ofile))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "ASCC (Automated Short Circuit Calculation)\n"
            "------------------------------------------\n"
            "Corre un cortocircuito con opciones tipicas y lo tabula en ascc.xlsx"
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
        help="Ruta al archivo de subsistema (.sbsxml)."
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

    program = ASCCProgram()
    program.run_ascc(
        cases=args.cases,
        sub_file=args.sub_file,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )