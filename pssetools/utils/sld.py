# coding: latin-1
from __future__ import absolute_import, division, print_function, unicode_literals
import re

def get_selected_map_strings():
    """Generador que obtiene los tokens del MapString para los componentes

    seleccionados en el diagrama unifilar (SLD) activo de PSS/E.
    """
    try:
        import sliderPy
    except ImportError:
        raise ImportError(
            "El modulo sliderPy no esta disponible.\n"
            "Esta funcion solo opera dentro de la interfaz grafica de PSS/E."
        )

    doc = sliderPy.GetActiveDocument()
    if not doc:
        return

    diagram = doc.GetDiagram()
    if not diagram:
        return

    for comp in diagram.GetComponents():
        if comp.IsSelected():
            tokens = re.findall(r"\S+", comp.GetMapString())
            if tokens:
                yield tokens

def get_bus_info(psspy, bus):
    """Devuelve (nombre, tension_base) de una barra dada."""
    name = str(bus)
    ierr, val = psspy.notona(bus)
    if ierr == 0 and val and val.strip():
        name = val.strip()
    kv = 0.0
    ierr, val = psspy.busdat(bus, "BASE")
    if ierr == 0:
        kv = val
    return name, kv

def branch_label(psspy, ibus, jbus, ckt):
    """Formato de etiqueta de linea/transformador de 2 devanados id PSS/E."""
    iname, ikv = get_bus_info(psspy, ibus)
    jname, jkv = get_bus_info(psspy, jbus)
    return "{:<9d}{:<12s}{:6.2f}   {:<9d}{:<12s}{:6.2f} {}".format(
        ibus, iname[:12], ikv, jbus, jname[:12], jkv, ckt
    )

def three_winding_label(psspy, bus, name, ckt, winding):
    """Formato de etiqueta de transformador de 3 devanados id PSS/E."""
    iname, ikv = get_bus_info(psspy, bus)
    return "{:<9d}{:<12s}{:6.2f} {:<6s} {:<17s}{:<6s}{}".format(
        bus, iname[:12], ikv, "3WNDTR", name[:17], "WND {}".format(winding), ckt
    )

def map_key(map_string):
    """Identificador unico e invariante para no duplicar elementos."""
    kind = map_string[0]
    if kind in ("LII", "TR", "SYS") and len(map_string) >= 3:
        ckt = map_string[3] if len(map_string) > 3 else ""
        return (kind, tuple(sorted(map_string[1:3])), ckt)
    if kind == "T3" and len(map_string) >= 4:
        ckt = map_string[4] if len(map_string) > 4 else ""
        return ("T3", tuple(sorted(map_string[1:4])), ckt)
    return tuple(map_string)
