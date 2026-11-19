# coding: latin-1
from __future__ import absolute_import, division, print_function, unicode_literals

"""
Extractor de Resultados
-----------------------
Lee un archivo de monitoreo (.tsv) y extrae los datos de PSS/E
para un lote de casos (.sav), consolidandolos en un unico Excel.
Apto para casos de ACCC o casos post-falla de simulaciones dinamicas.
"""

import argparse
import os
import sys

import pandas as pd

from pssetools.programs import BaseProgram
from pssetools.utils.results import get_results_from_case


class ExtractorProgram(BaseProgram):
    order = 22

    def get_parameters(self):
        """Define los parametros para la interfaz grafica."""
        return [
            {
                "name": "cases",
                "label": "Saved Cases (.sav):",
                "type": "multi_file",
                "default": "",
            },
            {
                "name": "mon_file",
                "label": "Monitored Elements (.tsv):",
                "type": "file",
                "default": "monitor.tsv",
            },
            {
                "name": "output_name",
                "label": "Output Excel Name:",
                "type": "text",
                "default": "resultados.xlsx",
            },
        ]

    def run(self, parsed_params):
        """Punto de entrada invocado por la GUI."""
        self._run(**parsed_params)

    def _run(self, cases, mon_file, output_name="resultados.xlsx", output_dir=".", temp_dir="."):
        psspy = self.psspy
        psspy.psseinit()

        if not os.path.exists(mon_file):
            print("Error: El archivo de monitoreo '{}' no existe.".format(mon_file))
            return

        dfs = []
        for case in cases:
            if not os.path.exists(case):
                print("Advertencia: El caso no existe, omitiendo -> {}".format(case))
                continue

            ierr = psspy.case(case)
            if ierr != 0:
                print("Error al cargar el caso '{}': ierr={}".format(case, ierr))
                continue

            df = get_results_from_case(mon_file)
            if df is not None and not df.empty:
                df["CASO"] = os.path.splitext(os.path.basename(case))[0]
                dfs.append(df)

        if dfs:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            if not output_name.lower().endswith(".xlsx"):
                output_name = output_name + ".xlsx"

            ofile = os.path.join(output_dir, output_name)
            df_final = pd.concat(dfs, axis=0, ignore_index=True)

            # Reordenar columnas para que "CASO" quede al inicio
            cols = ["CASO"] + [c for c in df_final.columns if c != "CASO"]
            df_final = df_final[cols]

            df_final.to_excel(ofile, index=False)
            print("Extraccion finalizada con exito. Reporte guardado en:\n{}".format(ofile))
        else:
            print("No se pudieron extraer datos de los casos especificados.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Extractor de Resultados PSS/E\n"
            "-----------------------------\n"
            "Extrae magnitudes de red (.tsv) desde una lista de casos .sav y genera un reporte Excel."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-c", "--cases",
        nargs="+",
        required=True,
        help="Rutas a los casos guardados (.sav)."
    )
    parser.add_argument(
        "-m", "--mon-file",
        required=True,
        dest="mon_file",
        help="Ruta al archivo TSV de elementos monitoreados."
    )
    parser.add_argument(
        "--output-name",
        dest="output_name",
        default="extraccion_resultados.xlsx",
        help="Nombre del archivo Excel de salida (por defecto: extraccion_resultados.xlsx)."
    )
    parser.add_argument(
        "-o", "--output-dir",
        dest="output_dir",
        default=".",
        help="Carpeta de destino del reporte Excel (por defecto: directorio actual)."
    )
    parser.add_argument(
        "-t", "--temp-dir",
        dest="temp_dir",
        default=".",
        help="Carpeta de archivos temporales (por defecto: directorio actual)."
    )

    args = parser.parse_args()
    program = ExtractorProgram()
    program._run(
        cases=args.cases,
        mon_file=args.mon_file,
        output_name=args.output_name,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
