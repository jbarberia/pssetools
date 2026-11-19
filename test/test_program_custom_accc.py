# coding: latin-1
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import pandas as pd
import pytest

from pssetools.programs import BaseProgram

BaseProgram.set_psse_path()
import psspy

from pssetools.programs.custom_accc import CustomACCCProgram
from pssetools.programs.extractor import ExtractorProgram


def test_custom_accc_and_extractor_flow():
    # 1. Inicializacion de PSS/E
    psspy.psseinit()
    case_path = os.path.join("test", "files", "test_case.sav")
    ierr = psspy.case(case_path)
    if ierr != 0:
        pytest.fail("Error al cargar el caso .sav. Ierr: {}".format(ierr))

    # 2. Definicion de rutas de archivos de prueba
    con_file = os.path.join("test", "files", "test_case_accc.py")
    mon_file = os.path.join("test", "files", "test_case_accc.tsv")

    # Directorios de salida y temporales
    output_root = os.path.join("test", "output")
    temp_root = os.path.join("test", "tmp")
    output_dir = os.path.join(output_root, "custom_accc_results")
    temp_dir = os.path.join(temp_root, "custom_accc_temp")

    for d in (output_root, temp_root, output_dir, temp_dir):
        if not os.path.exists(d):
            os.makedirs(d)

    try:
        # 3. Ejecucion de Custom ACCC (solo genera casos .sav)
        program_accc = CustomACCCProgram()
        program_accc._run(
            cases=[case_path],
            con_file=con_file,
            output_dir=output_dir,
            temp_dir=temp_dir,
        )

        # 4. Validar que se generaron los .sav esperados segun test_case_accc.py
        case_subfolder = os.path.join(output_dir, "test_case")
        sav_base = os.path.join(case_subfolder, "test_case_base.sav")
        sav_branch = os.path.join(case_subfolder, "test_case_BRANCH_RAMA_B.sav")

        assert os.path.exists(sav_base), "No se genero el caso base: {}".format(sav_base)
        assert os.path.exists(sav_branch), "No se genero el caso de contingencia: {}".format(sav_branch)

        # 5. Ejecucion del Extractor sobre los .sav generados
        generated_cases = [sav_base, sav_branch]
        program_extractor = ExtractorProgram()
        program_extractor._run(
            cases=generated_cases,
            mon_file=mon_file,
            output_name="estatico.xlsx",
            output_dir=output_dir,
            temp_dir=temp_dir,
        )

        # 6. Validar que el reporte Excel fue generado y contiene datos
        output_xlsx = os.path.join(output_dir, "estatico.xlsx")
        assert os.path.exists(output_xlsx), "No se genero el archivo estatico.xlsx"

        df_results = pd.read_excel(output_xlsx)
        assert not df_results.empty, "El archivo estatico.xlsx esta vacio"
        assert "CASO" in df_results.columns, "Falta la columna CASO en el Excel de salida"
        assert "ELEMENTO" in df_results.columns, "Falta la columna ELEMENTO en el Excel de salida"

    finally:
        pass
