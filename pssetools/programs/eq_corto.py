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
from pssetools.utils.topology import (
    parse_boundaries,
    get_island_buses,
    get_boundary_buses,
    set_element_status,
    verify_island_isolation,
)

class Equivalente(BaseProgram):
    order = 61
    
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
        import pssarrays  # type: ignore

        _i = psspy.getdefaultint()
        _f = psspy.getdefaultreal()

        # 1. Leer fronteras
        psspy.case(infile)
        bus_1, bus_2, fronteras = parse_boundaries(limit_file)
        barras_frontera = get_boundary_buses(psspy, fronteras)

        # 2. Extraer caso y validar aislamiento
        isla_1 = get_island_buses(psspy, bus_1, fronteras)
        if not verify_island_isolation(psspy, bus_1, bus_2):
            return

        # 3. Correr corto afuera de los limites del sistema
        barras_dentro = list(set(isla_1).intersection(set(barras_frontera)))
        arcos_a_mantener = [a[1:] for a in fronteras]
        sc_data = {}

        for ibus in barras_dentro:
            psspy.case(infile)
            psspy.bus_chng_4(ibus, 0, intgar=3)
            ierr = psspy.inibrn(ibus, single=2)

            # Abre vinculos no pertenecientes a la frontera
            while ierr == 0:
                ierr, jbus, kbus, ckt = psspy.nxtbrn3(ibus)
                ckt = ckt.strip()
                if ierr != 0:
                    break

                if kbus == 0:
                    es_frontera = any([
                        [ibus, jbus, ckt] in arcos_a_mantener,
                        [jbus, ibus, ckt] in arcos_a_mantener,
                    ])
                    if not es_frontera:
                        set_element_status(psspy, "LII", [ibus, jbus, ckt], status=0)
                        set_element_status(psspy, "SYS", [ibus, jbus, ckt], status=0)
                else:
                    es_frontera = any([
                        [ibus, jbus, kbus, ckt] in arcos_a_mantener,
                        [ibus, kbus, jbus, ckt] in arcos_a_mantener,
                        [jbus, ibus, kbus, ckt] in arcos_a_mantener,
                        [jbus, kbus, ibus, ckt] in arcos_a_mantener,
                        [kbus, ibus, jbus, ckt] in arcos_a_mantener,
                        [kbus, jbus, ibus, ckt] in arcos_a_mantener,
                    ])
                    if not es_frontera:
                        set_element_status(psspy, "T3", [ibus, jbus, kbus, ckt], status=0)

            # Pone generadores como slacks para evitar desconexiones de tree
            psspy.progress_output(6)
            ierr, (machnum,) = psspy.amachint(-1, string="NUMBER")
            if ierr == 0 and machnum:
                for bus in machnum:
                    psspy.bus_chng_4(bus, 0, intgar=3)

            # Elimina inconsistencias de barras aisladas
            ierr, buses = psspy.tree(1, 0)
            while buses != 0:
                ierr, buses = psspy.tree(2, 1)
            psspy.progress_output(1)

            # Elimina el varistor en los bancos de capacitores
            ierr, (id_list,) = psspy.abrnchar(string=["ID"])
            ierr, (fr, to, mov) = psspy.abrnint(string=["FROMNUMBER", "TONUMBER", "MOVTYPE"])
            mov_lines = [(f, t, i) for f, t, i, m in zip(fr, to, id_list, mov) if m != 0]
            for i, j, ckt in mov_lines:
                psspy.seq_branch_data_3(i, j, ckt, intgar1=0, realar8=0.0)

            # Calcula cortocircuito
            psspy.bsys(0, 0, [0.0, 0.0], 0, [], 1, [ibus], 0, [], 0, [])
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

        # 4. Abre las fronteras del caso
        psspy.case(infile)
        psspy.short_circuit_warning(0)
        for frontera in fronteras:
            set_element_status(psspy, frontera[0], frontera[1:], status=0)

        # 5. Coloca generadores equivalentes
        psspy.bsys(1, 0, [0.0, 0.0], 0, [], len(barras_dentro), barras_dentro, 0, [], 0, [])
        psspy.bgen(1, 0, 1)
        import pdb; pdb.set_trace()
        for ibus in barras_dentro:
            psspy.seq_machine_data_4(
                ibus, "99",
                realar1=sc_data[ibus]["z1"].real,
                realar2=sc_data[ibus]["z1"].imag,
                realar3=sc_data[ibus]["z2"].real,
                realar4=sc_data[ibus]["z2"].imag,
                realar5=sc_data[ibus]["z0"].real,
                realar6=sc_data[ibus]["z0"].imag
            )

        # 6. Elimina las demas barras externas
        ierr, (all_bus,) = psspy.abusint(-1, 2, "NUMBER")
        barras_a_eliminar = [b for b in all_bus if b not in isla_1]
        psspy.bsys(1, 0, [0.0, 525.0], 0, [], len(barras_a_eliminar), barras_a_eliminar, 0, [], 0, [])
        psspy.extr(1, 0, [0, 0])

        # 7. Asigna slack al generador mas grande
        ierr, (parray,) = psspy.agenbusreal(-1, 1, "PGEN")
        ierr, (busnum,) = psspy.agenbusint(-1, 1, "NUMBER")

        max_gen = (0, None)
        for p, b in zip(parray, busnum):
            if p > max_gen[0]:
                max_gen = (p, b)
        if max_gen[1] is not None:
            psspy.bus_chng_4(max_gen[1], 0, intgar=3)

        psspy.fnsl()
        psspy.save(ofile)
        print("Equivalente de cortocircuito guardado en: {}".format(ofile))
        

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
