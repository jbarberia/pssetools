# coding: latin-1
"""
ACCC
----

Corre un AC Contingency Calculation modificado, bypaseando el PSS/E y 
generando un excel con los resultados de tensiones y flujos de carga.

"""

import os
import pandas as pd
from pssetools.utils.results import get_results_from_case
from pssetools.programs import BaseProgram


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
                "name": "mon_file",
                "label": "Monitored (.mon):",
                "type": "file",
                "default": "monitor.tsv",
            },
            {
                "name": "con_file",
                "label": "Contingency (.con):",
                "type": "file",
                "default": "contingencias.py",
            },
        ]


    def run(self, parsed_params):
        self._run(**parsed_params)


    def _run(self, cases, mon_file, con_file, output_dir=".", temp_dir="."):
        import inspect

        psspy = self.psspy
        psspy.psseinit()

        _i = psspy.getdefaultint()
        _f = psspy.getdefaultreal()
        _s = psspy.getdefaultchar()
        
        # cargar archivo de contingencias
        ruta_contingencias = os.path.abspath(con_file)
        nombre_modulo = os.path.splitext(os.path.basename(ruta_contingencias))[0]

        try: # (Python 3.4+)
            import importlib.util
            spec = importlib.util.spec_from_file_location(nombre_modulo, ruta_contingencias)
            contingencies = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(contingencies)
        except: # Método legacy (Python 2.7)
            import imp
            contingencies = imp.load_source(nombre_modulo, ruta_contingencias)

        LISTA_CONTINGENCIAS = {
            nombre: func 
            for nombre, func in inspect.getmembers(contingencies, inspect.isfunction)
            if func.__module__ == nombre_modulo
        }

        # corre flujos de carga
        dfs = []
        for case in cases:
            for nombre_ctg, funcion_ctg in LISTA_CONTINGENCIAS.items():    
                ierr = psspy.case(case)
                if ierr != 0: return
                assert psspy.solved() == 0
                
                funcion_ctg()
                self._disconnect_island()
                ierr = psspy.runlastsolution()
                assert ierr == 0

                name, _ = os.path.splitext(os.path.basename(case))
                ofile = os.path.join(output_dir, name, "{}_{}.sav".format(name, nombre_ctg))
                folder_path = os.path.dirname(ofile)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                psspy.save(ofile)

                df = get_results_from_case(mon_file)
                df["CASO"] = os.path.splitext(os.path.basename(case))[0]
                df["CONTINGENCIA"] = funcion_ctg.__doc__ if funcion_ctg.__doc__ else nombre_ctg
                dfs.append(df)

        pd.concat(dfs, axis=0).to_csv(os.path.join(output_dir, "estatico.tsv"), sep="\t", index=False)
        print("ACCC finalizado. Resultados guardados en: {}".format(os.path.join(output_dir, "estatico.tsv")))

    def _disconnect_island(self):
        psspy = self.psspy
        ierr, buses = psspy.tree(1, 0)
        while buses != 0:
            ierr, buses = psspy.tree(2, 1)
        return ierr







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
        mon_file=args.mon_file,
        con_file=args.con_file,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
