# coding: latin-1
"""
Imprime SLD
-----------

Imprime el SLD que esta actualmente abierto en la GUI del PSSE.
Tras la impresión, utiliza un subproceso de Python 3 para recortar 
los bordes y eliminar errores de paginación del PDF.
"""
import os
import shutil
import time
import subprocess
from pssetools.programs import BaseProgram

class SLDPrinter(BaseProgram):
    
    def get_parameters(self):    
        return [
            {
                "name": "python_3_path",
                "label": "Python 3 EXE (Para PyMuPDF):",
                "type": "file",
                "default": "C:/Python314/python.exe", # Ajustar a donde tengas instalado PyMuPDF
                "editable": True,
            },
            {
                "name": "cases",
                "label": "Saved cases (.sav):",
                 "type": "multi_file",
                 "default": ""
            },
        ]

    def run(self, parsed_params):        
        self.main(**parsed_params)
            

    def main(self, cases, python_3_path, **kwargs):        
        psspy = self.psspy
        psspy.psseinit()

        # impresion       
        print_output = "C:/Users/User/Documents/ms_print.pdf"
        output_dir = os.path.dirname(print_output)

        if os.path.isfile(print_output):
            os.remove(print_output)

        pdfs_generados = []
        for case in cases:
            ierr = psspy.case(case)
            if ierr != 0:
                continue
            sav_base, _ = os.path.splitext(os.path.basename(case))

            psspy.refreshdiagfile()
            psspy.printdiagfile(r"""Microsoft Print to PDF""",1,2)

            while self.is_file_in_use(print_output):
                time.sleep(0.1)

            output = os.path.join(output_dir, sav_base + ".pdf")
            shutil.move(print_output, output)

            pdfs_generados.append(output)

        # ajuste
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.abspath(os.path.join(base_dir, "..", "utils", "pdf_fixer.py"))
        
        if pdfs_generados:
            cmd = [python_3_path, script_path, "--pdfs"] + pdfs_generados

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_data, stderr_data = process.communicate()
            
            out_str = stdout_data.decode("utf-8", errors="replace") if stdout_data else ""
            err_str = stderr_data.decode("utf-8", errors="replace") if stderr_data else ""

            if out_str:
                print(out_str)
            if process.returncode != 0 or err_str:
                print("--- ERRORES AL AJUSTAR PDFS ---")
                print(err_str)
        except Exception as e:
            print("Error al invocar subproceso de ajuste: {}".format(e))




    @staticmethod
    def is_file_in_use(filename):
        try:
            shutil.move(filename, filename)
        except:
            return True
        else:
            return False
