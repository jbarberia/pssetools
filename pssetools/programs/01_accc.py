# coding: latin-1
"""
ACCC
----

Corre un AC Contingency Calculation y genera dos excel:
- uno para lineas monitoreadas (accc_flow.xlsx)
- uno para tensiones monitoreadas (accc_volt.xlsx)

"""

import os
import pandas as pd

from pssetools.programs import BaseProgram
from pssetools.utils.accc_df import accc_df
from pssetools.utils.accc_unzip import accc_unzip


class ACCCProgram(BaseProgram):

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
                
        psspy = self.psspy
        psspy.psseinit()
        _f = psspy.getdefaultreal()

        flow_table = []
        volt_table = []

        for case in cases:
            base, _ = os.path.splitext(os.path.basename(case))
            tmp_zipfile = os.path.join(os.path.expanduser("~"), base + ".zip")

            ierr = psspy.case(case)
            if ierr != 0:
                continue

            dfx_file = os.path.join(temp_dir, base + ".dfx")
            ierr = psspy.dfax_2([1, 0, 1], sub_file, mon_file, con_file, dfx_file)

            acc_file = os.path.join(temp_dir, base + ".acc")
            ierr = psspy.accc_with_dsp_3(
                tol=_f,
                optacc=[
                    0,  # tap adj (0: disable, 1:stepping, 2:direct)
                    0,  # area interchange
                    0,  # phase shift
                    0,  # dc tap adjustment
                    0,  # sw shunt adj (0:disable, 1:enable, 2:only continuous)
                    1,  # (0: fdns, 1:fnsl)
                    1,  # divergent solution
                    0,  # induction motors
                    0,  # induction motors convergence flag
                    0,  # dispatch mode
                    1,  # write zip archive
                ],
                dfxfile=dfx_file,
                accfile=acc_file,
                zipfile=tmp_zipfile,
            )

            accc_unzip(tmp_zipfile, os.path.join(output_dir, base))
            df_flow, df_volt = accc_df(acc_file)
            flow_table.append(df_flow)
            volt_table.append(df_volt)

        if flow_table:
            pd.concat(flow_table).to_excel(os.path.join(output_dir, "accc_flow.xlsx"), index=False)
            pd.concat(volt_table).to_excel(os.path.join(output_dir, "accc_volt.xlsx"), index=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "ACCC\n"
            "----\n"
            "Corre un AC Contingency Calculation y genera dos excel:\n"
            "  - accc_flow.xlsx  (lineas monitoreadas)\n"
            "  - accc_volt.xlsx  (tensiones monitoreadas)"
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

    program = ACCCProgram()
    program._run(
        cases=args.cases,
        sub_file=args.sub_file,
        mon_file=args.mon_file,
        con_file=args.con_file,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
