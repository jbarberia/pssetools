# coding: latin-1
from __future__ import absolute_import, division, print_function, unicode_literals

import importlib
import os
import sys
from collections import OrderedDict

# Abstraccion para compatibilidad Python 2 y 3 (metaclases y tipos de cadena)
PY2 = sys.version_info[0] == 2
if PY2:
    text_type = unicode
else:
    text_type = str


class BaseProgram(object):
    """Clase base de nuevo estilo compatible con Python 2 y 3."""
    order = 9999

    def __init__(self, test_dir=None):
        self.set_psse_path()
        import psspy
        self.psspy = psspy

    @staticmethod
    def set_psse_path():
        """Detecta de forma dinamica la instalacion activa de PSS/E."""
        is_64_bits = sys.maxsize > 2**32
        
        # Secuencia ordenada de intentos de importacion segun arquitectura
        candidates = ["psse36", "psse3606", "psse35", "psse34"] if is_64_bits else ["psse34", "psse33"]
        
        psse_loaded = False
        for mod_name in candidates:
            try:
                importlib.import_module(mod_name)
                psse_loaded = True
                break
            except ImportError:
                continue

        if not psse_loaded:
            # Si no se encuentra como modulo registrado, verificar sys.path
            if "psspy" not in sys.modules:
                sys.stderr.write(
                    "[ADVERTENCIA] No se pudo inicializar el entorno PSS/E automaticamente. "
                    "Verifique que la sesion se ejecute en el entorno de Siemens PSS/E.\n"
                )

    def get_parameters(self):
        """Retorna las definiciones de parametros para la UI."""
        raise NotImplementedError("Subclases deben implementar get_parameters()")

    def run(self, parsed_params):
        """Punto de entrada de ejecucion."""
        raise NotImplementedError("Subclases deben implementar run()")


def discover_programs(test_dir=None):
    """Descubre recursivamente todos los programas que heredan de BaseProgram."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    programs_dir = current_dir if os.path.basename(current_dir) == "programs" else os.path.join(current_dir, "programs")
    pkg_root = os.path.dirname(programs_dir)
    project_root = os.path.dirname(pkg_root)

    if test_dir is None:
        test_dir = os.path.join(project_root, "test")

    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    programs_data = OrderedDict()
    program_instances = OrderedDict()
    errors = []

    discovered_files = []
    for root, dirs, files in os.walk(programs_dir):
        for fname in sorted(files):
            if fname.endswith(".py") and not fname.startswith("__"):
                rel_dir = os.path.relpath(root, programs_dir)
                discovered_files.append((rel_dir, fname))

    # Preservar configuracion de bytecode para Python 2/3
    old_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True

    try:
        for rel_dir, fname in discovered_files:
            module_name = fname[:-3]
            if rel_dir == ".":
                rel_key = fname
                full_module_path = "pssetools.programs." + module_name
            else:
                rel_key = os.path.join(rel_dir, fname).replace("\\", "/")
                sub_pkg = rel_dir.replace(os.sep, ".")
                full_module_path = "pssetools.programs." + sub_pkg + "." + module_name

            try:
                mod = importlib.import_module(full_module_path)
                doc = getattr(mod, "__doc__", None)
                doc_str = doc.strip() if doc else "No documentation provided."

                program_class = None
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    # Comprobacion de tipo segura en Py2 (type/ClassType) y Py3
                    if isinstance(attr, type) and issubclass(attr, BaseProgram) and attr is not BaseProgram:
                        program_class = attr
                        break

                if program_class:
                    instance = program_class(test_dir)
                    programs_data[rel_key] = {
                        "doc": doc_str,
                        "parameters": instance.get_parameters()
                    }
                    program_instances[rel_key] = instance
            except Exception as e:
                err_text = "{}: {}".format(rel_key, str(e))
                errors.append(err_text)
    finally:
        sys.dont_write_bytecode = old_bytecode
    
    
    
    sorted_items = sorted(
        program_instances.items(),
        key=lambda item: getattr(item[1], "order", 999)
    )
    ordered_programs_data = OrderedDict()
    ordered_program_instances = OrderedDict()

    for rel_key, instance in sorted_items:
        ordered_program_instances[rel_key] = instance
        ordered_programs_data[rel_key] = programs_data[rel_key]

    return ordered_programs_data, ordered_program_instances, errors    
