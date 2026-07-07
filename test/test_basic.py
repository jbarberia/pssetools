import psse34
import pssetools
from nose.tools import assert_raises


def test_config_00():
    ""
    config = pssetools.get_config()
    assert isinstance(config, dict)


def test_config_01():
    "lectura de configuracion"
    config = pssetools.get_config("test/files/config.jsonc")
    assert config["psspy.dfax_2"]["subfile"] == "savnw.sub" 


def test_kwargs_00():
    "kwargs por defecto"
    import psspy
    func = psspy.dfax_2
    args = pssetools.get_kwargs(func)
    assert isinstance(args, dict)
    assert args["subfile"] == "estudio.sub"



