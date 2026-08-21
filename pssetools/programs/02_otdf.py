"""
OTDF
----

Calcula los factores de distribución y los tabula en otdf.xlsx

Nota: no calcula los shifts, que deben ser sacados del caso base.
Para esto se puede usar la actividad ACCC y su excel de resultados.

"""

import os
import pandas as pd

from pssegui.programs import BaseProgram
from pssegui.utils.otdf import otdf


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
            
            