# coding: latin-1
import os
import pytest
import pandas as pd
import importlib

from pssetools.programs import BaseProgram
BaseProgram.set_psse_path()
import psspy

# Import ASCCProgram dynamically to avoid issues with numeric module names
ascc_module = importlib.import_module("pssetools.programs.03_ascc")
ASCCProgram = ascc_module.ASCCProgram

def test_ascc_full_flow():
    # 1. Inicialización de PSS/E
    psspy.psseinit()
    case_path = os.path.join("test", "files", "test_case.sav")

    ierr = psspy.case(case_path)
    if ierr != 0:
        pytest.fail("Error al cargar el caso .sav. Ierr: {}".format(ierr))

    # 2. Definición de rutas de archivos de prueba
    sub_file = os.path.join("test", "files", "test_case.sbsxml")
    
    # Directorios de salida y temporales
    output_root = os.path.join("test", "output")
    temp_root = os.path.join("test", "tmp")

    output_dir = os.path.join(output_root, "ascc_results")
    temp_dir = os.path.join(temp_root, "ascc_temp")

    if not os.path.exists(output_root): os.makedirs(output_root)
    if not os.path.exists(temp_root): os.makedirs(temp_root)
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)

    try:
        # 3. Ejecución del programa ASCC utilizando los archivos de test/files
        program = ASCCProgram()
        # El método run_ascc acepta: cases (lista), sub_file, output_dir, temp_dir
        program.run_ascc(
            cases=[case_path],
            sub_file=sub_file,
            output_dir=output_dir,
            temp_dir=temp_dir
        )

        # 4. Validaciones de salida
        ascc_excel = os.path.join(output_dir, "ascc.xlsx")
        assert os.path.exists(ascc_excel), "No se genero el archivo ascc.xlsx"

        # Verificar que el excel no este vacio
        df_ascc = pd.read_excel(ascc_excel)
        assert not df_ascc.empty, "El archivo ascc.xlsx esta vacio"

    finally:
        pass  # Limpieza comentada para debuggear; use 'make clean'
        # import shutil
        # for dir in [output_dir, temp_dir]:
        #     if os.path.exists(dir):
        #         shutil.rmtree(dir, ignore_errors=True)
