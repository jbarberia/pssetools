import os
import sys
import psse34
import psspy
import argparse
import configparser
from ast import literal_eval


def is_in_psse_gui():
    return os.path.basename(sys.executable).lower() == "psse34.exe"


def argument_parser(args_specs):
    "crea un parser automatico para cada extension"
    parser = argparse.ArgumentParser()
    for arg, specs in args_specs.items():
        parser.add_argument("--{}".format(arg), **specs)
    
    parser.add_argument("files", nargs="*")
    args = parser.parse_args().__dict__
    
    # en caso de disponerlos sin especificar los asigna automaticamente
    for f in args["files"]:
        for arg in args_specs:
            if f.endswith(arg) and args[arg] is None:
                args[arg] = f   
    return args
    
    
def converter(in_str):
    try:
        out = literal_eval(in_str)
    except Exception:
        out = in_str
    return out


def config_parser(filename):
    "parser de un .cfg a un diccionario con comentarios en linea"
    config_file = configparser.ConfigParser(inline_comment_prefixes = ("#",))
    config_file.optionxform = lambda option: option
    config_file.read(filename)

    config = {}
    for section in config_file.sections():
        config[section] = {}
        for k, v in config_file[section].items():
            config[section][k] = converter(v)
    return config


def deep_update(base, updates):
    "Recursively update a dict of dicts."
    for key, value in updates.items():
        if (
            key in base
            and isinstance(base[key], dict)
            and isinstance(value, dict)
        ):
            deep_update(base[key], value)
        else:
            base[key] = value
    return base


def get_config(filename=None):
    "devuelve una configuracion o la configuracion por defecto"
    filename = os.path.join(os.path.dirname(__file__), "config.cfg")
    config = config_parser(filename)
    
    if filename:
        new_config = config_parser(filename)
        config = deep_update(config, new_config)

    return config


if is_in_psse_gui():
    print("cargar gui")
else:
    old_stdout = sys.stdout
    try:
        sys.stdout = open(os.devnull, 'w')
        ierr = psspy.psseinit()
    finally:
        sys.stdout.close()
        sys.stdout = old_stdout
    assert ierr == 0

default_config = get_config()
