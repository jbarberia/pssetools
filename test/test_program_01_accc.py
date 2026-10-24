# coding: latin-1
import os
import pytest
import sys
import pandas as pd


from pssetools.programs import BaseProgram
BaseProgram.set_psse_path()
import psspy
import importlib
accc_module = importlib.import_module("pssetools.programs.01_accc")
ACCCProgram = accc_module.ACCCProgram

def test_accc_full_flow():
    # 1. Inicialización de PSS/E
    psspy.psseinit()
    case_path = os.path.join("test", "files", "test_case.sav")
    
    ierr = psspy.case(case_path)
    if ierr != 0:
        pytest.fail("Error al cargar el caso .sav. Ierr: {}".format(ierr))

    # 2. Definición de rutas de archivos de prueba existentes
    sub_file = os.path.join("test", "files", "test_case.sub")
    mon_file = os.path.join("test", "files", "test_case.mon")
    con_file = os.path.join("test", "files", "test_case.con")

    # Directorios de salida y temporales
    output_root = os.path.join("test", "output")
    temp_root = os.path.join("test", "tmp")

    output_dir = os.path.join(output_root, "accc_results")
    temp_dir = os.path.join(temp_root, "accc_temp")

    if not os.path.exists(output_root): os.makedirs(output_root)
    if not os.path.exists(temp_root): os.makedirs(temp_root)
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)

    try:
        # 3. Ejecución del programa ACCC utilizando los archivos de test/files
        program = ACCCProgram()
        # Simulamos los parametros que pasaria la GUI
        program._run(
            cases=[case_path],
            sub_file=sub_file,
            mon_file=mon_file,
            con_file=con_file,
            output_dir=output_dir,
            temp_dir=temp_dir
        )

        # 4. Validaciones de salida
        flow_excel = os.path.join(output_dir, "accc_flow.xlsx")
        volt_excel = os.path.join(output_dir, "accc_volt.xlsx")

        assert os.path.exists(flow_excel), "No se genero el archivo accc_flow.xlsx"
        assert os.path.exists(volt_excel), "No se genero el archivo accc_volt.xlsx"

        # Verificar que los excels no esten vacios                
        df_flow = pd.read_excel(flow_excel)
        assert not df_flow.empty, "El archivo accc_flow.xlsx esta vacio"

        df_volt = pd.read_excel(volt_excel)
        assert not df_volt.empty, "El archivo accc_volt.xlsx esta vacio"

    finally:
        pass  # Limpieza opcional comentada para debuggear; use 'make clean'
        # import shutil
        # for dir in [output_dir, temp_dir]:
        #     if os.path.exists(dir):
        #         shutil.rmtree(dir, ignore_errors=True)
        
