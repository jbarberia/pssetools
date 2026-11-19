# coding: latin-1
"""
ACCC Custom
-----------
Corre un AC Contingency Calculation modificado, bypaseando PSS/E
y generando los casos .sav resultantes post-contingencia.
"""
import os
import inspect
from pssetools.programs import BaseProgram


class CustomACCCProgram(BaseProgram):
    order = 21

    def get_parameters(self):
        return [
            {
                "name": "cases",
                "label": "Working Case (.sav):",
                "type": "multi_file",
                "default": "",
            },
            {
                "name": "con_file",
                "label": "Contingency (.con/.py):",
                "type": "file",
                "default": "contingencias.py",
            },
        ]

    def run(self, parsed_params):
        self._run(**parsed_params)

    def _run(self, cases, con_file, output_dir=".", temp_dir="."):
        psspy = self.psspy
        psspy.psseinit()
        _f = psspy.getdefaultreal()

        ruta_contingencias = os.path.abspath(con_file)
        nombre_modulo = os.path.splitext(os.path.basename(ruta_contingencias))[0]

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(nombre_modulo, ruta_contingencias)
            contingencies = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(contingencies)
        except (ImportError, AttributeError):
            import imp
            contingencies = imp.load_source(nombre_modulo, ruta_contingencias)

        LISTA_CONTINGENCIAS = {
            nombre: func 
            for nombre, func in inspect.getmembers(contingencies, inspect.isfunction)
            if getattr(func, '__module__', '') == nombre_modulo and not nombre.startswith('_')
        }

        for case in cases:
            for nombre_ctg, funcion_ctg in LISTA_CONTINGENCIAS.items():
                ierr = psspy.case(case)
                if ierr != 0: 
                    continue
                
                funcion_ctg()
                ierr = psspy.runlastsolution()
                if ierr == 1:
                    self._disconnect_island()
                    ierr = psspy.runlastsolution()                
                if ierr != 0: 
                    continue
                
                name = os.path.splitext(os.path.basename(case))[0]
                ofile = os.path.join(output_dir, name, "{}_{}.sav".format(name, nombre_ctg))
                
                folder_path = os.path.dirname(ofile)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                
                psspy.save(ofile)
        
        print("ACCC Custom finalizado. Casos guardados en subcarpetas de: {}".format(output_dir))

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
            "ACCC Custom\n"
            "-----------\n"
            "Aplica rutinas de contingencia en Python sobre casos .sav y guarda los resultados."
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

    program = CustomACCCProgram()
    program._run(
        cases=args.cases,
        mon_file=args.mon_file,        
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
