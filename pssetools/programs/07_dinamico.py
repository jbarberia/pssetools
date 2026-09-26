# coding: latin-1
"""
Simulación Dinámica
-------------------
Ejecuta simulaciones dinámicas secuencialmente.



"""

import os
import shutil
import sys
import re
import time
from pssetools.programs import BaseProgram

class DynamicSimulationProgram(BaseProgram):
    
    def get_parameters(self):
        return [
            {
                "name": "cases",
                "label": "Cases (.sav):",
                "type": "multi_file",
                "default": "",
            },
            {
                "name": "convload",
                "label": "Convertidor de caso (.py):",
                "type": "file",
                "default": "",
            },
            {
                "name": "snapshot",
                "label": "Snapshot Base (.snp):",
                "type": "file",
                "default": "",
            },
            {
                "name": "dlls",
                "label": "User Models (.dll):",
                "type": "multi_file",
                "default": "",
            },
            {
                "name": "scripts",
                "label": "Scripts (.py):",
                "type": "multi_file",
                "default": "",
            },
            {
                "name": "debug",
                "label": "Stop on Suspect Initial Conditions:",
                "type": "bool",
                "default": False,
            },
            {
                "name": "overwrite",
                "label": "Overwrite simulation:",
                "type": "bool",
                "default": True,
            },
        ]

    def run(self, parsed_params):
        self.main(**parsed_params)


    def main(self, cases, snapshot, dlls, convload, scripts, debug=False, overwrite=True, output_dir=".", temp_dir="."):
        if not cases or not snapshot:
            print("ERROR: Debe proveer al menos un caso (.sav) y un snapshot (.snp).")
            return

        psspy = self.psspy
        psspy.psseinit()

        for idx, sav_file in enumerate(cases, 1):
            if not os.path.exists(sav_file):
                print("Advertencia: El caso no existe, omitiendo -> {}".format(sav_file))
                continue
            
            for script in scripts:
                try:                
                    self._run_single_simulation(psspy, sav_file, snapshot, dlls, convload, script, output_dir, debug, overwrite)
                except Exception as e:
                    print("Error durante la simulación de {}: {}".format(os.path.basename(sav_file), e))

                

    def _run_single_simulation(self, psspy, sav, snp, dlls, convload, script, output_dir, debug, overwrite):
        """Lógica central de simulación dinámica para un único caso."""

        t0 = time.time()
        
        sav_basename, _ = os.path.splitext(os.path.basename(sav))
        py_basename, _ = os.path.splitext(os.path.basename(script))
        basename = "{}_{}".format(sav_basename, py_basename)

        output_dir = os.path.join(output_dir, basename)
        if overwrite and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)

        os.makedirs(output_dir)
        out_file = os.path.join(output_dir, basename + ".outx")

        # Redirigir progreso a archivo .pdv temporal/permanente
        pdv_file = os.path.join(output_dir, basename + ".pdv")
        psspy.t_progress_output(2, pdv_file, [2, 0])
        
        # Cargar Caso Convertido y Snapshot
        ierr = psspy.case(sav)
        if ierr != 0:
            raise Exception("Fallo al cargar el caso convertido: {}".format(sav))
            
        ierr = psspy.rstr(snp)
        if ierr != 0:
            raise Exception("Fallo al cargar el snapshot: {}".format(snp))

        # Convertir caso
        locals_vars = {
            "psspy": psspy,
            "_i" : psspy.getdefaultint(),
            "_f" : psspy.getdefaultreal(),
            "_s" : psspy.getdefaultchar(),
        }        
        with open(convload) as f:
            code = f.read()
            exec(code, locals_vars)
        
        # Cargar librerías DLL de usuario
        for library in dlls:
            if library and os.path.exists(library):
                psspy.addmodellibrary(library)
          
        # 4. Inicializar Condiciones
        ierr = psspy.strt_2([1, 1], out_file) 
        
        if psspy.okstrt() != 0 and debug:
            psspy.t_progress_output(6) # Liberar archivo output
            initial_conditions = self._get_initial_conditions_suspect(pdv_file)
            psspy.beginreport()
            psspy.report(sav + "\n\n")
            psspy.report(initial_conditions)
            raise Exception("Falla en la inicialización (OKSTRT != 0)")
            
        # Guardar estado base T=0
        psspy.save(os.path.join(output_dir, basename + "_T0.cnv"))
        psspy.snap(sfile=os.path.join(output_dir, basename + "_T0.snp"))
        sys.stdout.write("{} inicializado en T=0\n".format(basename))

        # Ejecutar rutinas/eventos de usuario mediante exec()
        locals_vars = {
            "psspy": psspy,
            "_i" : psspy.getdefaultint(),
            "_f" : psspy.getdefaultreal(),
            "_s" : psspy.getdefaultchar(),
        }
        with open(script) as f:
            code = f.read()
            exec(code, locals_vars)
               
        # Obtener tiempo final y guardar estados post-falla
        ierr, final_time = psspy.dsrval("TIME")
        psspy.save(os.path.join(output_dir, basename + "_T{:.0f}.cnv".format(final_time)))
        psspy.snap(sfile=os.path.join(output_dir, basename + "_T{:.0f}.snp".format(final_time)))

        t1 = time.time()
        
        psspy.progress("\nFIN SIMULACION\n")
        psspy.progress("{} finalizado en T={:.0f}\n".format(basename, final_time))
        psspy.progress("Elapsed time {:.3f} s\n".format(t1 - t0))

        # Liberar salida y procesar condiciones sospechosas
        psspy.t_progress_output(6)
        

    @staticmethod
    def _get_initial_conditions_suspect(filename):
        """Filtra y guarda únicamente los 'INITIAL CONDITIONS SUSPECT' del reporte."""
        if not os.path.exists(filename):
            return

        with open(filename, "r") as f:
            content = f.read()        
        
        pattern = r"INITIAL CONDITIONS SUSPECT:\n(.*)\n^"
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        
        if match:
            initial_conditions = match.group(1)        
            return initial_conditions


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Simulacion Dinamica\n"
            "-------------------\n"
            "Ejecuta simulaciones dinamicas secuencialmente."
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
        "--convload",
        required=True,
        help="Ruta al script de conversion de caso (.py)."
    )

    parser.add_argument(
        "-s", "--snapshot",
        required=True,
        help="Ruta al snapshot base (.snp)."
    )

    parser.add_argument(
        "-d", "--dlls",
        nargs="+",
        required=False,
        default=[],
        help="Rutas a las librerias de usuario (.dll)."
    )

    parser.add_argument(
        "--scripts",
        nargs="+",
        required=True,
        help="Rutas a los scripts de eventos (.py)."
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Si se especifica, detiene la simulacion ante condiciones iniciales sospechosas."
    )

    parser.add_argument(
        "--no-overwrite",
        action="store_false",
        dest="overwrite",
        default=True,
        help="Si se especifica, no sobreescribe simulaciones existentes."
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

    program = DynamicSimulationProgram()
    program.main(
        cases=args.cases,
        snapshot=args.snapshot,
        dlls=args.dlls,
        convload=args.convload,
        scripts=args.scripts,
        debug=args.debug,
        overwrite=args.overwrite,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
