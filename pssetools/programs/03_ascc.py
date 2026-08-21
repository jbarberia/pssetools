"""
ASCC (Automated Short Circuit Calculation)

Corre un cortocircuito con opciones tipicas y lo tabula en:

ascc.xlsx
"""

import os
import pandas as pd

from pssegui.programs import BaseProgram
from pssegui.utils.ascc import ascc

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
        