# coding: latin-1
"""
Equivalente de cortocircuito
----------------------------

Realiza un equivalente de cortocircuito 


Por ejemplo para seccionar el NOA usar como límite:

8000 2620
LII 5016 8011 1
LII 6006 8004 1

siendo 8000 una barra interna a la isla y 2620 una barra externa a la isla para 
poder verificar si se desmembra correctamente el sistema.
"""
import os
import re
from pssetools.programs import BaseProgram

class Equivalente(BaseProgram):
    
    def get_parameters(self):
        """Returns the parameter definitions and characteristics for ACCC."""
        return [
            {
                "name": "infile",
                "label": "Input File (.sav):",
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
        self.main(**parsed_params)

            
    def main(self, infile, ofile, limit_file, output_dir=".", temp_dir=".", **kwargs):        
        psspy = self.psspy
        psspy.psseinit()
        import pssarrays # type: ignore

        _i = psspy.getdefaultint()
        _f = psspy.getdefaultreal()

        # lee fronteras
        bus_1, bus_2, fronteras = self.get_fronteras(limit_file)
        barras_frontera = self.obtener_barras_frontera(fronteras)

        # extracto del caso
        psspy.case(infile)
        isla_1 = self.obtener_isla(bus_1, fronteras)
        if not self.check_island(bus_1, bus_2):
            return

        # correr corto afuera de los limites del sistema
        barras_dentro = list(set([b for b in barras_frontera if b in isla_1]))
        arcos_a_mantener = [a[1:] for a in fronteras]
        sc_data = {}

        for ibus in barras_dentro:
            psspy.case(infile)
            psspy.bus_chng_4(ibus, 0, intgar=3)
            ierr = psspy.inibrn(ibus, single=2)

            # abre vinculos
            while ierr == 0:
                ierr, jbus, kbus, ckt = psspy.nxtbrn3(ibus)
                ckt = ckt.strip()
                if ierr != 0: break

                if kbus == 0:                    
                    frontera = any([
                        [ibus, jbus, ckt] in arcos_a_mantener,
                        [jbus, ibus, ckt] in arcos_a_mantener,
                    ])
                    if not frontera:
                        self.abrir_elemento("LII", [ibus, jbus, ckt])
                        self.abrir_elemento("SYS", [ibus, jbus, ckt])

                else:
                    frontera = any([
                        [ibus, jbus, kbus, ckt] in arcos_a_mantener,
                        [ibus, kbus, jbus, ckt] in arcos_a_mantener,
                        [jbus, ibus, kbus, ckt] in arcos_a_mantener,
                        [jbus, kbus, ibus, ckt] in arcos_a_mantener,
                        [kbus, ibus, jbus, ckt] in arcos_a_mantener,
                        [kbus, jbus, ibus, ckt] in arcos_a_mantener,
                    ])
                    if not frontera:
                        self.abrir_elemento("T3", [ibus, jbus, kbus, ckt])


            # pone generadores como slacks para evitar desconexiones de tree
            psspy.progress_output(6)
            ierr, (machnum,) = psspy.amachint(-1, string="NUMBER")
            ierr, (machid,) = psspy.amachchar(-1, string="ID")
            for bus in machnum:
                psspy.bus_chng_4(bus,0,intgar=3)

            # elimina inconsistencias de barras aisladas            
            ierr, buses = psspy.tree(1, 0)
            while buses != 0:
                ierr, buses = psspy.tree(2, 1)
            psspy.progress_output(1)

            # elimina el varistor en los bancos de capacitores
            ierr, (id,) = psspy.abrnchar(string=["ID"])
            ierr, (fr, to, mov) = psspy.abrnint (string=["FROMNUMBER", "TONUMBER", "MOVTYPE"])
            mov_lines = [(f,t,i) for f,t,i,m in zip(fr, to, id, mov) if m != 0]
            for i, j, ckt in mov_lines:
                psspy.seq_branch_data_3(i, j, ckt, intgar1=0, realar8=0.0)

            # calcula corto
            psspy.bsys(0,0,[0.0,0.0],0,[],1,[ibus],0,[],0,[])
            psspy.short_circuit_warning(0)
            psspy.short_circuit_units(0)
            psspy.short_circuit_z_units(0)
            psspy.short_circuit_coordinates(0)
            psspy.short_circuit_z_coordinates(0)
            
            rlst = pssarrays.ascc_currents(
                0, 0,
                flt3ph=1, fltlg=1, fltllg=0, fltll=0,
                linout=0, linend=0, voltop=0, genxop=0,
                tpunty=0, dcload=0, zcorec=1, lnchrg=0,
                shntop=0, loadop=0, machpq=0, volts=1.0,
                relfile="", fcdfile="", scfile="nooutput",
                rptop=-1, rptlvl=0
            )
            
            sc_data[ibus] = {
                "z0": rlst["thevzpu"][0]["z0"],
                "z1": rlst["thevzpu"][0]["z1"],
                "z2": rlst["thevzpu"][0]["z2"],
            }

        
        # Abre las fronteras del caso
        psspy.case(infile)
        psspy.short_circuit_warning(0)
        for frontera in fronteras:
            tipo = frontera[0]
            identificador = frontera[1:]
            self.abrir_elemento(tipo, identificador)
       
        # Pone los equivalentes
        psspy.bsys(1,0,[0.0,0.0],0,[],len(barras_dentro),barras_dentro,0,[],0,[])
        psspy.bgen(1,0,1)
        for ibus in barras_dentro:
            psspy.seq_machine_data_4(
                ibus,"99",
                realar1=sc_data[ibus]["z1"].real,
                realar2=sc_data[ibus]["z1"].imag,
                realar3=sc_data[ibus]["z2"].real,
                realar4=sc_data[ibus]["z2"].imag,
                realar5=sc_data[ibus]["z0"].real,
                realar6=sc_data[ibus]["z0"].imag
            )
               
        # elimina todas las otras barras
        ierr, (all_bus,) = psspy.abusint(-1, 2, "NUMBER")
        barras_a_eliminar = [b for b in all_bus if b not in isla_1]
        psspy.bsys(1,0,[0.0, 525.],0,[],len(barras_a_eliminar),barras_a_eliminar,0,[],0,[])
        psspy.extr(1,0,[0,0])

        # generador slack sobre el generador mas grande
        ierr, (parray,) = psspy.agenbusreal(-1, 1, "PGEN")
        ierr, (busnum,) = psspy.agenbusint(-1, 1, "NUMBER")

        max_gen = (0, None)
        for p, b in zip(parray, busnum):
            if p > max_gen[0]:
                max_gen = (p, b)
        psspy.bus_chng_4(max_gen[1],0,intgar=3)
        
        psspy.fnsl()
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Equivalente de cortocircuito\n"
            "----------------------------\n"
            "Realiza un equivalente de cortocircuito.\n\n"
            "El archivo de limites define las fronteras del sistema. Ejemplo:\n\n"
            "  8000 2620\n"
            "  LII 5016 8011 1\n"
            "  LII 6006 8004 1\n\n"
            "siendo 8000 una barra interna a la isla y 2620 una barra externa."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-i", "--infile",
        required=True,
        help="Ruta al caso de entrada (.sav)."
    )

    parser.add_argument(
        "-f", "--ofile",
        required=True,
        help="Ruta del caso de salida (.sav)."
    )

    parser.add_argument(
        "-l", "--limit-file",
        required=True,
        dest="limit_file",
        help="Ruta al archivo de limites (.txt)."
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

    program = Equivalente()
    program.main(
        infile=args.infile,
        ofile=args.ofile,
        limit_file=args.limit_file,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
