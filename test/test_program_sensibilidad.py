# coding: latin-1
import os
import pytest
import pandas as pd

from pssetools.programs import BaseProgram
BaseProgram.set_psse_path()
import psspy

from pssetools.programs.sensibilidad import SensitivityProgram


def test_sensitivity_full_flow():
    # 1. Rutas de archivos de prueba
    case_path = os.path.join("test", "files", "test_case.sav")
    sub_file = os.path.join("test", "files", "test_case.sub")
    mon_file = os.path.join("test", "files", "test_case.mon")
    con_file = os.path.join("test", "files", "test_case.con")
    elements_file = os.path.join("test", "files", "test_case_accc.tsv")

    # Directorios de salida y temporales
    output_root = os.path.join("test", "output")
    temp_root = os.path.join("test", "tmp")

    output_dir = os.path.join(output_root, "sensibilidad_results")
    temp_dir = os.path.join(temp_root, "sensibilidad_temp")

    if not os.path.exists(output_root): os.makedirs(output_root)
    if not os.path.exists(temp_root): os.makedirs(temp_root)
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)

    try:
        # 2. Ejecucion del programa SensitivityProgram a traves de run()
        program = SensitivityProgram()

        parsed_params = {
            "cases": [case_path],
            "sub_file": sub_file,
            "mon_file": mon_file,
            "con_file": con_file,
            "elements_file": elements_file,
            "source_subsystem": "SYSTEM1",
            "target_subsystem": "SYSTEM2",
            "ac_network": True,
            "output_dir": output_dir,
            "temp_dir": temp_dir,
        }

        program.run(parsed_params)

        # 3. Validaciones de salida
        report_txt = os.path.join(temp_dir, "sensitivity_report.txt")
        report_xlsx = os.path.join(output_dir, "sensitivity_report.xlsx")

        assert os.path.exists(report_txt), "No se genero el archivo sensitivity_report.txt"
        assert os.path.exists(report_xlsx), "No se genero el archivo sensitivity_report.xlsx"

        # Verificar que el excel tenga las 4 hojas esperadas
        expected_sheets = ["BUS NAME", "LOAD BUS", "TAP TRANSFORMERS", "SWITCHED SHUNTS"]
        xl = pd.ExcelFile(report_xlsx)
        for sheet in expected_sheets:
            assert sheet in xl.sheet_names, "Falta la hoja '{}' en el excel".format(sheet)

        df_bus = pd.read_excel(report_xlsx, sheet_name="BUS NAME")
        assert not df_bus.empty, "La hoja BUS NAME esta vacia"
        assert "ELEMENTO" in df_bus.columns, "Falta la columna ELEMENTO en BUS NAME"
        assert "CASO" in df_bus.columns, "Falta la columna CASO en BUS NAME"
        assert "MW_SENS" in df_bus.columns, "Falta la columna MW_SENS en BUS NAME"

    finally:
        pass



