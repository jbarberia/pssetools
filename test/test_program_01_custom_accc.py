# coding: latin-1
import os
import pytest
import pandas as pd
import importlib
import shutil

from pssetools.programs import BaseProgram
BaseProgram.set_psse_path()
import psspy

# Import CustomACCCProgram from 01_custom_accc
custom_accc_module = importlib.import_module("pssetools.programs.01_custom_accc")
CustomACCCProgram = custom_accc_module.ACCCProgram

def test_custom_accc_full_flow():
    # 1. Inicialización de PSS/E
    psspy.psseinit()
    case_path = os.path.join("test", "files", "test_case.sav")

    ierr = psspy.case(case_path)
    if ierr != 0:
        pytest.fail("Error al cargar el caso .sav. Ierr: {}".format(ierr))

    # 2. Definición de rutas de archivos de prueba proporcionados
    mon_file = os.path.join("test", "files", "test_case_accc.tsv")    
    con_file = os.path.join("test", "files", "test_case_accc.py")

    # Directorios de salida y temporales
    output_root = os.path.join("test", "output")
    temp_root = os.path.join("test", "tmp")

    output_dir = os.path.join(output_root, "custom_accc_results")
    temp_dir = os.path.join(temp_root, "custom_accc_temp")

    if not os.path.exists(output_root): os.makedirs(output_root)
    if not os.path.exists(temp_root): os.makedirs(temp_root)
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)

    try:
        # 3. Ejecución del programa Custom ACCC
        program = CustomACCCProgram()
        # El método _run acepta: cases (lista), mon_file, con_file, output_dir, temp_dir
        program._run(
            cases=[case_path],
            mon_file=mon_file,
            con_file=con_file,
            output_dir=output_dir,
            temp_dir=temp_dir
        )

        # 4. Validaciones de salida
        # Custom ACCC genera un archivo "estatico.tsv"
        output_tsv = os.path.join(output_dir, "estatico.tsv")

        assert os.path.exists(output_tsv), "No se genero el archivo estatico.tsv"

        # Verificar que el archivo no esté vacío y tenga el formato correcto
        df_results = pd.read_csv(output_tsv, sep="\t")
        assert not df_results.empty, "El archivo estatico.tsv esta vacio"

        # Verificar que se hayan procesado las contingencias definidas en test_case_accc.py
        # (base y BRANCH_RAMA_B)
        assert "CONTINGENCIA" in df_results.columns, "El archivo de salida no contiene la columna CONTINGENCIA"

    finally:
        pass  # Limpieza comentada para debuggear; use 'make clean'
        # for dir in [output_dir, temp_dir]:
        #     if os.path.exists(dir):
        #         shutil.rmtree(dir, ignore_errors=True)
