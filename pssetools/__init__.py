from __future__ import print_function
import os
import sys
import psse34
import psspy
import pssarrays
import argparse
import configparser
from ast import literal_eval
from functools import wraps


def pss_activity(func):
    """Decorator to standardize PSS/E activity execution.

    Handles case loading (sav or cnv), error code verification, and
    basic cleanup of output redirection on failure.

    Args:
        func: The activity function to wrap.

    Returns:
        The wrapped function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        sav = kwargs.get('sav')
        cnv = kwargs.get('cnv')
        
        if sav:
            ierr = psspy.case(sav)
            if ierr != 0:
                raise Exception("Error loading case {}: {}".format(sav, ierr))
        elif cnv:
            ierr = psspy.case(cnv)
            if ierr != 0:
                raise Exception("Error loading case {}: {}".format(cnv, ierr))
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            # Ensure output is redirected back to screen on failure if it was redirected
            psspy.t_progress_output(1, "", [0, 0])
            raise e
        
        if isinstance(result, int) and result > 0:
            raise Exception("Activity {} failed with error code: {}".format(func.__name__, result))
        
        return result
    return wrapper


def argument_parser(args_specs):
    """Creates an automatic argument parser based on provided specifications.

    Args:
        args_specs: Dictionary defining arguments and their argparse specs.

    Returns:
        Parsed arguments as a dictionary.
    """
    parser = argparse.ArgumentParser()
    for arg, specs in args_specs.items():
        parser.add_argument("--{}".format(arg), **specs)
    
    parser.add_argument("files", nargs="*")
    args = parser.parse_args().__dict__
    
    # en caso de no pasar argumentos mostrar una ayuda    
    need_help = []
    for k, v in args.items():
        if isinstance(v, list):
            need_help.append(len(v) == 0)            
        elif v is not None:
            need_help.append(False)
    if all(need_help):
        parser.print_help()
        sys.exit(0)

    # en caso de disponerlos sin especificar los asigna automaticamente
    for f in args["files"]:
        for arg in args_specs:
            if f.endswith(arg) and args[arg] is None:
                args[arg] = f   
    return args
    
    
def converter(in_str):
    """Attempts to convert a string to its literal Python value.

    Args:
        in_str: The string to convert.

    Returns:
        The converted value or the original string if conversion fails.
    """
    try:
        out = literal_eval(in_str)
    except Exception:
        out = in_str
    return out


def config_parser(filename):
    """Parses a .cfg file into a dictionary, supporting inline comments.

    Args:
        filename: Path to the configuration file.

    Returns:
        A dictionary containing the parsed configuration sections and keys.
    """
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
    """Recursively updates a dictionary of dictionaries.

    Args:
        base: The base dictionary to update.
        updates: The dictionary containing updates.

    Returns:
        The updated base dictionary.
    """
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
    """Retrieves the application configuration.

    Loads the default configuration and merges it with an optional
    user-provided configuration file.

    Args:
        filename: Optional path to a user configuration file.

    Returns:
        The merged configuration dictionary.
    """
    default_cfg = os.path.join(os.path.dirname(__file__), "config.cfg")
    config = config_parser(default_cfg)
    
    if filename:
        new_config = config_parser(filename)
        config = deep_update(config, new_config)

    return config


def is_in_psse_gui():                                               
    """Checks if the script is running inside the PSS/E GUI.        
                                                                    
    Returns:                                                        
        True if running in psse34.exe, False otherwise.             
    """                                                             
    return os.path.basename(sys.executable).lower() == "psse34.exe" 


# Start of the program
default_config = get_config()
if is_in_psse_gui():         
    from .gui import gui    
    gui = gui()
    gui.root.mainloop()
else:                             
    # Suppress stdout/stderr during psseinit to hide the initialization banner
    with open(os.devnull, 'w') as fnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = fnull
        sys.stderr = fnull
        try:
            psspy.psseinit()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
