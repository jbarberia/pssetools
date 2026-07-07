import os
import commentjson
import warnings
import inspect

def get_config(filename=None):
    "obtener configuracion o devolver una por defecto"
    if filename == None:
        warnings.warn("Se utiliza configuracion por defecto", UserWarning)
        dirname = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(dirname, "config.jsonc") 
    
    if isinstance(filename, dict):
        return filename

    with open(filename) as f:
        config = commentjson.loads(f.read())
    return config


def get_kwargs(function, config=None):
    """
    obtiene kwargs para una funcion dada.
    si no la encuentra da un diccionario vacio
    """
    if not config:
        config = get_config(config)

    if isinstance(config, str):
        config = get_config(config)

    key = ".".join([
        function.__module__,
        function.__name__,
        ])

    kwargs = config.get(key, {})
    return kwargs




