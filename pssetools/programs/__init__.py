# coding: latin-1
import os
import sys
import importlib
from collections import OrderedDict

class BaseProgram(object):
    """Base class for all PSS/E automation modules."""
    
    def __init__(self, test_dir=None):
        # incializa psse        
        self.set_psse_path()
        import psspy
        self.psspy = psspy

    @staticmethod
    def set_psse_path():
        is_64_bits = sys.maxsize > 2**32
        if is_64_bits:
            import psse3606
        else:
            import psse34

    def get_parameters(self):
        """Returns parameter definitions for the UI. Must be overridden by subclasses."""
        raise NotImplementedError

    def run(self, parsed_params):
        """Execution entry point called by the main application. Must be overridden."""
        raise NotImplementedError


def discover_programs(test_dir=None):
    """
    Dynamically discovers and loads all program classes recursively using OrderedDict.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Aseguramos la ruta a la carpeta 'programs'
    if os.path.basename(current_dir) == "programs":
        programs_dir = current_dir
        pkg_root = os.path.dirname(current_dir) # carpeta 'pssegui'
    else:
        programs_dir = os.path.join(current_dir, "programs")
        pkg_root = current_dir

    project_root = os.path.dirname(pkg_root)
    if test_dir is None:
        test_dir = os.path.join(project_root, "test")

    programs_data = OrderedDict()
    program_instances = OrderedDict()
    errors = []

    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Recolectar archivos Python dentro de 'programs'
    discovered_files = []
    for root, dirs, files in os.walk(programs_dir):
        dirs.sort()
        files.sort()
        for fname in files:
            if fname.endswith(".py") and not fname.startswith("__"):
                rel_dir = os.path.relpath(root, programs_dir)
                discovered_files.append((rel_dir, fname, root))

    discovered_files.sort(key=lambda x: (x[0], x[1]))

    # Evitar usar código cache (archivos .pyc)
    old_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True

    for rel_dir, fname, root in discovered_files:
        module_name = fname[:-3]
        
        if rel_dir == ".":
            rel_key = fname
            full_module_path = "pssegui.programs." + module_name
        else:
            rel_key = os.path.join(rel_dir, fname).replace("\\", "/")
            sub_pkg = rel_dir.replace(os.sep, ".")
            full_module_path = "pssegui.programs." + sub_pkg + "." + module_name

        try:
            # Importación segura
            mod = importlib.import_module(full_module_path)

            doc = getattr(mod, "__doc__", None)
            doc_str = doc.strip() if doc else "No documentation provided."

            program_class = None
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseProgram) and 
                    attr is not BaseProgram):
                    program_class = attr
                    break

            if program_class:
                instance = program_class(test_dir)
                params = instance.get_parameters()

                programs_data[rel_key] = {
                    "doc": doc_str,
                    "parameters": params
                }
                program_instances[rel_key] = instance

        except Exception as e:
            error_msg = "{}: {}".format(rel_key, str(e))
            print("Error loading program module '" + rel_key + "': " + str(e))
            errors.append(error_msg)

    # Restaurar el comportamiento de bytecode original
    sys.dont_write_bytecode = old_bytecode

    return programs_data, program_instances, errors
