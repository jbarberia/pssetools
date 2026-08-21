# coding: latin-1
"""
Genera un snapshot
------------------

En idv se pasa el response file con los canales a sumar.
En py se pasa un python con las opciones tipicas a usar.

psspy.setnetfrq() # ya incluida
psspy.set_relang(1,2610,"1")

"""

import os
from pssegui.programs import BaseProgram
from pssegui.utils.snp import create_snapshot


class Snapshot(BaseProgram):
    
    def get_parameters(self):
        "Returns the parameter definitions"
        return [
            {
                "name": "case",
                "label": "Working Case (.sav):",
                "type": "file",
                "default": "",
                "editable": False,
            },
            {
                "name": "dyr_files",
                "label": "Dyre files (.dyr):",
                "type": "multi_file",
                "default": "",
            },
            {
                "name": "conec",
                "label": "CONEC (.flx):",
                "type": "file",
                "default": "",
                "editable": True,
            },
            {
                "name": "conet",
                "label": "CONET (.flx):",
                "type": "file",
                "default": "",
                "editable": True,
            },
            {
                "name": "idv",
                "label": "Canales (.idv):",
                "type": "file",
                "default": "",
                "editable": True,
            },
            {
                "name": "py",
                "label": "Configuración (.py):",
                "type": "file",
                "default": "",
                "editable": True,
            },
            {
                "name": "snapshot",
                "label": "Snapshot (.snp):",
                "type": "file",
                "default": "",
                "editable": False,
            },
        ]

    def run(self, parsed_params):
        self.run_snapshot(**parsed_params)

    def run_snapshot(self, case, dyr_files, conec, conet, idv, py, snapshot, output_dir=".", temp_dir="."):
        psspy = self.psspy
        psspy.psseinit()

        ierr = create_snapshot(
            sav=case,
            snp=snapshot,
            dyr=dyr_files,
            cc=conec,
            ct=conet,
        )

        if idv and os.path.exists(idv):
            psspy.runrspnsfile(idv)

        locals_vars = {
            "psspy": psspy,
            "_i" : psspy.getdefaultint(),
            "_f" : psspy.getdefaultreal(),
            "_s" : psspy.getdefaultchar(),
        }
        if py and os.path.exists(py):
             with open(py) as f:
                code = f.read()
                exec(code, locals_vars)

        # configuracion tipica
        _i = psspy.getdefaultint()
        _f = psspy.getdefaultreal()
        _s = psspy.getdefaultchar()
        psspy.dynamics_solution_param_2([250,_i,_i,_i,_i,_i,_i,_i],[ 0.25,_f, 0.002,_f,_f,_f,_f,_f])
        psspy.set_netfrq(1)

        ierr = psspy.snap(sfile=snapshot)
