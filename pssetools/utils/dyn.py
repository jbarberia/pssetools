# coding: latin-1

import os
import sys
import argparse
import re

def export_initial_conditions_suspect(filename):
    """Extrae las condiciones iniciales sospechosas del archivo de progreso."""
    if not os.path.exists(filename):
        return

    with open(filename, "r") as f:
        content = f.read()        
    
    # Busca la sección de INITIAL CONDITIONS SUSPECT
    pattern = r"INITIAL CONDITIONS SUSPECT:\n(.*)\n^"
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    
    if match:
        initial_conditions = match.group(1)        
        with open(filename, "w") as f:
            f.write(initial_conditions)


def run_dynamic_simulation(cnv, snp, out, dlls, py_scripts, debug=False):    
    # Importaciones de PSS/E asumiendo que el entorno está configurado
    import psspy
    
    psspy.psseinit()

    dirname = os.path.dirname(out)
    basename = os.path.basename(out).split(".")[0]
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

    psspy.setThrowPsseExceptions(True)
    
    # 1. Cargar Caso Convertido y Snapshot
    if psspy.case(cnv) != 0:
        raise Exception("Fallo al cargar el caso convertido: {}".format(cnv))
    if psspy.rstr(snp) != 0:
        raise Exception("Fallo al cargar el snapshot: {}".format(snp))

    # 2. Cargar librerías de usuario
    for library in dlls:
        if library:
            psspy.addmodellibrary(library)
        
    # 3. Redirigir progreso a archivo .pdv
    t_device = os.path.join(dirname, basename + ".pdv")
    psspy.t_progress_output(2, t_device, [2, 0])
    
    # 4. Inicializar
    psspy.setThrowPsseExceptions(False)
    ierr = psspy.strt_2([1, 1], out) 
    
    if psspy.okstrt() != 0 and debug:        
        psspy.t_progress_output(6) # Liberar archivo antes de crashear
        raise Exception("Error en la inicialización - {} {}".format(cnv, snp))
        
    # 5. Guardar estado T=0
    psspy.save(os.path.join(dirname, basename + "_T0.cnv"))
    psspy.snap(sfile=os.path.join(dirname, basename + "_T0.snp"))
    print("{} inicializado en T=0".format(basename))

    # 6. Preparar entorno para scripts del usuario y ejecutar
    locals_vars = {
        "psspy": psspy,
        "_i" : psspy.getdefaultint(),
        "_f" : psspy.getdefaultreal(),
        "_s" : psspy.getdefaultchar(),
    }
    
    for script_file in py_scripts:
        if script_file and os.path.exists(script_file):
            print("Ejecutando script de eventos: {}".format(os.path.basename(script_file)))
            with open(script_file, "r") as f:
                code = f.read()
                exec(code, locals_vars)
    
    # 7. Guardar flujo y snapshot postfalla
    ierr, final_time = psspy.dsrval("TIME")
    psspy.save(os.path.join(dirname, basename + "_T{:.0f}.cnv".format(final_time)))
    psspy.snap(sfile=os.path.join(dirname, basename + "_T{:.0f}.snp".format(final_time)))
    
    psspy.progress("\n FIN SIMULACION\n")
    print("{} finalizado en T={:.0f}".format(basename, final_time))

    # 8. Liberar t-device y post-procesar el archivo sospechoso
    psspy.t_progress_output(6)
    export_initial_conditions_suspect(t_device)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Worker Dinámico PSS/E")
    parser.add_argument("--cnv", required=True, help="Caso convertido (.cnv)")
    parser.add_argument("--snp", required=True, help="Snapshot (.snp)")
    parser.add_argument("--out", required=True, help="Archivo de salida principal (.out)")
    parser.add_argument("--dlls", nargs="*", default=[], help="Librerías de modelos DLL")
    parser.add_argument("--py", nargs="*", default=[], help="Scripts de simulación (.py)")
    parser.add_argument("--debug", action="store_true", help="Detener en fallas de inicialización")

    args = parser.parse_args()
    
    try:
        sys.exit(run_dynamic_simulation(
            args.cnv, args.snp, args.out, args.dlls, args.py, args.debug
        ))
    except Exception as e:
        sys.stderr.write("Error en Simulación: {}\n".format(e))
        sys.exit(1)
