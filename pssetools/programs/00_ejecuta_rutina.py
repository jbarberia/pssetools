# coding: latin-1
"""
Ejecuta rutina
--------------

Corre diferentes pythons sobre los casos.
Se debe aceptar la opción sobrescribir para guardar el caso de forma permanente.

En caso de querer guardarlo en otro lugar se recomienda al final del python poner:

import os
case, snap = psspy.sfiles()
path, ext = os.path.splitext(case)
psspy.save(path + "modificado" + ext)
"""
import os
from pssetools.programs import BaseProgram

class EjecutaRutina(BaseProgram):
    
    def get_parameters(self):    
        return [
            {"name": "cases",     "label": "Saved cases (.sav):", "type": "multi_file", "default": ""},
            {"name": "py_files",  "label": "Python files (.py):", "type": "multi_file", "default": ""},            
            {"name": "overwrite", "label": "Overwrite files:",    "type": "bool",       "default": False}
        ]

    def run(self, parsed_params):        
        self.main(**parsed_params)
            

    def main(self, cases, py_files, overwrite=False, **kwargs):        
        psspy = self.psspy
        psspy.psseinit()

        locals_vars = {
            "psspy": psspy,
            "_i" : psspy.getdefaultint(),
            "_f" : psspy.getdefaultreal(),
            "_s" : psspy.getdefaultchar(),
        }

        for case in cases:
            ierr = psspy.case(case)
            if ierr != 0:
                continue

            for file in py_files:
                if file.endswith(".py"):
                    with open(file) as f:
                        code = f.read()
                        exec(code, locals_vars)

            if overwrite:
                psspy.save(case)
            


