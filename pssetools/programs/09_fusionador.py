# coding: latin-1
"""
Fusionador de casos
-------------------

El archivo de límites debe especificarse con el mapstring correspondiente al
elemento usado.

Por ejemplo para seccionar el NOA usar como límite:

8000 2620
LII 5016 8011 1
LII 6006 8004 1

case_1 contiene la isla con la barra 8000
case_2 contiene la isla con la barra 2620


"""

import os
import re
import pandas as pd

from pssetools.programs import BaseProgram


class FusionadorDeCaso(BaseProgram):

    def get_parameters(self):
        """Returns the parameter definitions and characteristics for ACCC."""
        return [
            {
                "name": "case_1",
                "label": "Working Case 1 (.sav):",
                "type": "file",
                "default": "",
            },
            {
                "name": "case_2",
                "label": "Working Case 2 (.sav):",
                "type": "file",
                "default": "",
            },
            {
                "name": "ofile",
                "label": "Output File (.sav):",
                "type": "file",
                "default": "",
            },
            {
                "name": "limit_file",
                "label": "Limites (.txt):",
                "type": "file",
                "default": "",
            },            
        ]


    def run(self, parsed_params):
        self._run(**parsed_params)


    def _run(self, case_1, case_2, ofile, limit_file, output_dir=".", temp_dir="."):
                
        psspy = self.psspy
        psspy.psseinit()
        _i = psspy.getdefaultint()
        _f = psspy.getdefaultreal()

        # lee fronteras
        bus_1, bus_2, fronteras = self.get_fronteras(limit_file)

        # extracto del case_1
        psspy.case(case_1)
        isla_1 = self.obtener_isla(bus_1, fronteras)
        if not self.check_island(bus_1, bus_2):
            return

        psspy.case(case_1)
        psspy.bsys(0,0,[0.0, 525.],0,[],len(isla_1),isla_1,0,[],0,[])
        psspy.rawd_2(0,0,[1,1,1,0,0,0,1],0,os.path.join(temp_dir, "isla_1.raw"))
        psspy.rwsq_2(0,0,[1,1,1,0,1],0,os.path.join(temp_dir, "isla_1.seq"))

        # barras a eliminar del case_2
        psspy.case(case_2)
        isla_1 = self.obtener_isla(bus_1, fronteras)
        if not self.check_island(bus_1, bus_2):
            return
        barras_frontera = self.obtener_barras_frontera(fronteras)
        barras_a_eliminar = [bus for bus in isla_1 if bus not in barras_frontera]

        script = os.path.join(temp_dir, "elimina_isla.py")
        ierr = psspy.startrecording(1, script)
        psspy.bsys(1,0,[0.0, 525.],0,[],len(barras_a_eliminar),barras_a_eliminar,0,[],0,[])
        psspy.extr(1,0,[0,0])
        ierr = psspy.stoprecording()

        # corta el case_2 y le pega la parte del subsistema del case_1
        psspy.case(case_2)

        locals_vars = {
            "psspy": psspy,
            "_i" : psspy.getdefaultint(),
            "_f" : psspy.getdefaultreal(),
            "_s" : psspy.getdefaultchar(),
        }
        with open(script) as f:
            code = f.read()
            exec(code, locals_vars)

        psspy.read(0,os.path.join(temp_dir, "isla_1.raw"))
        psspy.resqversion('34', os.path.join(temp_dir, "isla_1.seq"))
        psspy.save(ofile)


    def get_fronteras(self, ofile):
        with open(ofile) as f:
            file_content = f.read()

        # remueve comentarios
        file_content = re.sub("^#.*", "", file_content)

        # splitting by non-empty sequences of commas, spaces, or tabs
        parsed_data = []
        for line in file_content.strip().splitlines():
            row = [token for token in re.split(r'[\t, ]+', line.strip()) if token]
            if row:
                parsed_data.append(row)

        bus_1 = int(parsed_data[0][0])
        bus_2 = int(parsed_data[0][1])

        fronteras = []
        for identificador in parsed_data[1:]:

            if identificador[0] in ["LII", "SYS"]:
                fronteras.append([
                    identificador[0],       # ident
                    int(identificador[1]),  # ibus
                    int(identificador[2]),  # jbus
                    identificador[3],       # ckt
                ])

            if identificador[0] in ["T3"]:
                fronteras.append([
                    identificador[0],       # ident
                    int(identificador[1]),  # ibus
                    int(identificador[2]),  # jbus
                    int(identificador[3]),  # kbus
                    identificador[4],       # ckt
                ])

        return bus_1, bus_2, fronteras


    def abrir_elemento(self, tipo, identificador):
        psspy = self.psspy    
        if tipo == "T3":
            psspy.three_wnd_imped_chng_4(*identificador,intgar8=0)
        if tipo == "LII":
            psspy.branch_chng_3(*identificador,intgar1=0)
        if tipo == "SYS":
            psspy.system_swd_chng(*identificador,intgar1=0)


    def prender_barras(self):
        psspy = self.psspy
        psspy.progress_output(6)

        ierr, (buses,) = psspy.abusint(-1, flag=2, string="NUMBER")
        for bus in buses:
            psspy.recn(bus)

            ierr, ide = psspy.busint(bus, "TYPE")
            if ide == 3:
                psspy.bus_chng_4(30,0,intgar1=2)

        psspy.progress_output(1)


    def obtener_isla(self, bus, fronteras):
        # Extraigo islas, para eso es necesario tener todas las barras prendidas
        # asi el comando tree me lista todas las barras
        psspy = self.psspy
        self.prender_barras()

        for frontera in fronteras:
            tipo = frontera[0]
            identificador = frontera[1:]
            self.abrir_elemento(tipo, identificador)

        treeobj = psspy.treedat(100)
        for isla in treeobj["island_busnum"]:
            if bus in isla:
                return isla
        return []


    def obtener_barras_frontera(self, fronteras):
        psspy = self.psspy
        barras_frontera = []
        for frontera in fronteras:
            tipo = frontera[0]
            if tipo == "T3":
                ierr, _ = psspy.wndint(*frontera[1:5], string="STATUS")
                barras = frontera[1:4] if ierr == 0 else []            
            if tipo == "LII":
                ierr, _ = psspy.brnint(*frontera[1:4], string="STATUS")
                barras = frontera[1:3] if ierr == 0 else []            
            if tipo == "SYS":
                ierr, _ = psspy.brnint(*frontera[1:4], string="STATUS")            
                barras = frontera[1:3] if ierr == 0 else []
            barras_frontera.extend(barras)
        return barras_frontera


    def check_island(self, bus1, bus2):
        psspy = self.psspy   
        ierr, camino, rxvalue = psspy.rxpath(1, bus1, bus2, 100)
        savfilnam, _ = psspy.sfiles()

        if len(camino) > 0: # Hay puente entre isla TBA hacia el SADI
            print("-" * 120)
            print("Limites en lado {}".format(savfilnam))
            print("No se creo la isla de forma correcta verificar vinculo en el camino:")
            print("\nNumero\tNombre\t\t\tArea")
            area_prev = None
            for bus in camino:
                ierr, name = psspy.notona(bus)
                ierr, area = psspy.busint(bus, "AREA")
                indicador = "<----" if area_prev and area != area_prev else ""
                area_prev = area
                print("{}\t{}\t{}\t{}".format(bus, name, area, indicador))
            print("-" * 120)
            return False
        else:
            return True
