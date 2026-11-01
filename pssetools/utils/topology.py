# coding: latin-1
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import re

def parse_boundaries(filepath):
    """
    Lee el archivo de fronteras/limites de particion de red.
    Retorna: (bus_1, bus_2, fronteras)
    Donde fronteras es una lista con formato:
      [['LII', ibus, jbus, ckt], ['SYS', ibus, jbus, ckt], ['T3', ibus, jbus, kbus, ckt]]
    """
    if not os.path.exists(filepath):
        raise IOError("El archivo de limites no existe: {}".format(filepath))

    with open(filepath, "r") as f:
        file_content = f.read()

    # Remover lineas de comentarios
    file_content = re.sub("^#.*", "", file_content)#, flags=re.MULTILINE)

    parsed_data = []
    for line in file_content.strip().splitlines():
        tokens = [tok for tok in re.split(r"[\t, ]+", line.strip()) if tok]
        if tokens:
            parsed_data.append(tokens)

    if not parsed_data:
        raise ValueError("El archivo de limites esta vacio o no tiene datos validos.")

    bus_1 = int(parsed_data[0][0])
    bus_2 = int(parsed_data[0][1])

    fronteras = []
    for ident in parsed_data[1:]:
        kind = ident[0].upper()
        if kind in ("LII", "SYS"):
            fronteras.append([
                kind,           # ident
                int(ident[1]),  # ibus
                int(ident[2]),  # jbus
                str(ident[3]),  # ckt
            ])
        elif kind == "T3":
            fronteras.append([
                kind,           # ident
                int(ident[1]),  # ibus
                int(ident[2]),  # jbus
                int(ident[3]),  # kbus
                str(ident[4]),  # ckt
            ])

    return bus_1, bus_2, fronteras

def set_element_status(psspy, tipo, ident, status=0):
    """
    Abre (status=0) o cierra un elemento de red en PSS/E.
    Soporta Transformadores 3W (T3), Lineas (LII) y Switches de sistema (SYS).
    """
    tipo = tipo.upper()
    if tipo == "T3":
        psspy.three_wnd_imped_chng_4(*ident, intgar8=status)
    elif tipo == "LII":
        psspy.branch_chng_3(*ident, intgar1=status)
    elif tipo == "SYS":
        psspy.system_swd_chng(*ident, intgar1=status)

def enable_all_buses(psspy):
    """
    Reconecta todas las barras desconectadas para garantizar
    que la exploracion topologica (tree/treedat) abarque la red completa.
    """
    psspy.progress_output(6)
    ierr, (buses,) = psspy.abusint(-1, flag=2, string="NUMBER")
    if ierr == 0 and buses:
        for bus in buses:
            psspy.recn(bus)
            ierr_type, ide = psspy.busint(bus, "TYPE")
            if ierr_type == 0 and ide == 3:
                psspy.bus_chng_4(bus, 0, intgar1=2)
    psspy.progress_output(1)

def get_island_buses(psspy, bus, fronteras):
    """
    Determina la lista de barras que pertenecen a la isla electrica que contiene a 'bus',
    tras abrir todos los elementos de frontera.
    """
    enable_all_buses(psspy)
    for frontera in fronteras:
        set_element_status(psspy, frontera[0], frontera[1:], status=0)

    treeobj = psspy.treedat(100)
    for isla in treeobj.get("island_busnum", []):
        if bus in isla:
            return isla
    return []

def get_boundary_buses(psspy, fronteras):
    """
    Devuelve las barras terminales activas pertenecientes a los elementos de frontera.
    """
    barras_frontera = []
    for frontera in fronteras:
        tipo = frontera[0].upper()
        if tipo == "T3":
            ierr, _ = psspy.wndint(frontera[1], frontera[2], frontera[3], frontera[4], string="STATUS")
            barras = frontera[1:4] if ierr == 0 else []
        elif tipo in ("LII", "SYS"):
            ierr, _ = psspy.brnint(frontera[1], frontera[2], frontera[3], string="STATUS")
            barras = frontera[1:3] if ierr == 0 else []
        else:
            barras = []
        barras_frontera.extend(barras)
    return list(set(barras_frontera))

def verify_island_isolation(psspy, bus1, bus2):
    """
    Comprueba que no exista camino electrico cerrado entre bus1 y bus2.
    Retorna True si estan aisladas (correcto), o False si hay vinculo no seccionado.
    """
    ierr, camino, rxvalue = psspy.rxpath(1, bus1, bus2, 100)
    savfilnam, _ = psspy.sfiles()

    if len(camino) > 0:
        print("-" * 120)
        print("Limites en caso: {}".format(savfilnam))
        print("No se creo la isla de forma correcta. Verificar vinculo en el camino:")
        print("\nNumero\tNombre\t\t\tArea")
        area_prev = None
        for b in camino:
            ierr_name, name = psspy.notona(b)
            ierr_area, area = psspy.busint(b, "AREA")
            indicador = "<----" if (area_prev and area != area_prev) else ""
            area_prev = area
            print("{}\t{}\t{}\t{}".format(b, (name or "").strip(), area, indicador))
        print("-" * 120)
        return False
    return True
