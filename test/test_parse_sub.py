# coding: latin-1
import os
import pytest

from pssetools.utils.parse_sub import parse_sub
from pssetools.programs import BaseProgram

BaseProgram.set_psse_path()
import psspy

def test_parse_sub_logic():
    psspy.psseinit()

    case_path = os.path.join("test", "files", "test_case.sav")
    ierr = psspy.case(case_path)
    if ierr != 0:
        pytest.fail("Error al cargar el caso .sav en PSS/E. Ierr: {}".format(ierr))

    test_file = os.path.join("test", "files", "test_case.sub")
    result = parse_sub(test_file)
    
    # Validaciones
    assert isinstance(result, dict), "El resultado debe ser un diccionario"
    assert "SYSTEM1" in result, "No se encontro el subsistema SYSTEM1"
    assert "SYSTEM2" in result, "No se encontro el subsistema SYSTEM2"
    assert result["SYSTEM1"] == [1, 2, 3], "Buses del subsistema SYSTEM1 incorrectos"


