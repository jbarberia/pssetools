"""Converter: Simple format config → expanded simulations list.

Converts the user-friendly simple config format to internal simulations list.

Format:
    accc:
        sav: [...list of .sav files...]
        sub: estudio.sub
        con: estudio.con
        mon: estudio.mon
    
    ascc:
        sav: [...list of .sav files...]
        sub: estudio.sub
    
    dinamico:
        sav: [...list of .sav files...]
        py: [...list of .py event scripts...]

Expands to:
    - Each ACCC case generates 1 simulation
    - Each ASCC case generates 1 simulation
    - Each (sav, py) combination generates 1 Dynamic simulation
"""

from __future__ import print_function
import os


def expand_simple_format(config):
    """Convert simple format config to simulations list.
    
    Args:
        config: Dictionary with 'accc', 'ascc', 'dinamico' sections
        
    Returns:
        List of simulation dictionaries (standard format)
    """
    simulations = []
    
    # ACCC: list of .sav + shared sub/con/mon
    if 'accc' in config:
        accc_config = config['accc']
        sav_list = accc_config.get('sav', [])
        sub = accc_config.get('sub')
        con = accc_config.get('con')
        mon = accc_config.get('mon')
        
        if not isinstance(sav_list, list):
            sav_list = [sav_list]
        
        for i, sav in enumerate(sav_list):
            case_name = os.path.basename(sav).replace('.sav', '')
            sim = {
                'name': 'ACCC_{}'.format(case_name),
                'type': 'accc',
                'case': sav,
                'options': {
                    'sub': sub,
                    'con': con,
                    'mon': mon,
                    'dfx': 'build/{}.dfx'.format(case_name),
                    'acc': 'build/{}.acc'.format(case_name),
                }
            }
            simulations.append(sim)
    
    # ASCC: list of .sav + shared sub
    if 'ascc' in config:
        ascc_config = config['ascc']
        sav_list = ascc_config.get('sav', [])
        sub = ascc_config.get('sub')
        
        if not isinstance(sav_list, list):
            sav_list = [sav_list]
        
        for i, sav in enumerate(sav_list):
            case_name = os.path.basename(sav).replace('.sav', '')
            sim = {
                'name': 'ASCC_{}'.format(case_name),
                'type': 'ascc',
                'case': sav,
                'options': {
                    'sub': sub,
                    'asc': 'build/{}.asc'.format(case_name),
                }
            }
            simulations.append(sim)
    
    # Dinámico: Cartesian product of sav × py scripts
    if 'dinamico' in config:
        dyn_config = config['dinamico']
        sav_list = dyn_config.get('sav', [])
        py_list = dyn_config.get('py', [])
        
        if not isinstance(sav_list, list):
            sav_list = [sav_list]
        if not isinstance(py_list, list):
            py_list = [py_list]
        
        # Generate all combinations
        for sav in sav_list:
            for py in py_list:
                case_name = os.path.basename(sav).replace('.sav', '')
                py_name = os.path.basename(py).replace('.py', '')
                
                # Sequence: CNV → SNP → DYN per case+py combo
                
                # CNV: convert case
                cnv_sim = {
                    'name': 'CNV_{}_{}'.format(case_name, py_name),
                    'type': 'cnv',
                    'case': sav,
                    'options': {
                        'cnv': 'build/{}_{}.cnv'.format(case_name, py_name),
                        'py': 'lib/convload.py',  # Standard conversion script
                    }
                }
                simulations.append(cnv_sim)
                
                # SNP: build snapshot
                snp_sim = {
                    'name': 'SNP_{}_{}'.format(case_name, py_name),
                    'type': 'snp',
                    'case': sav,
                    'options': {
                        'snp': 'build/{}_{}.snp'.format(case_name, py_name),
                        'dyr': 'estudio.dyr',
                        'idv': 'estudio.idv',
                    }
                }
                simulations.append(snp_sim)
                
                # DYN: run dynamic simulation
                dyn_sim = {
                    'name': 'DYN_{}_{}'.format(case_name, py_name),
                    'type': 'dyn',
                    'case': sav,
                    'options': {
                        'cnv': 'build/{}_{}.cnv'.format(case_name, py_name),
                        'snp': 'build/{}_{}.snp'.format(case_name, py_name),
                        'out': 'build/{}_{}.out'.format(case_name, py_name),
                        'outx': 'build/{}_{}.outx'.format(case_name, py_name),
                        'py': py,  # User's event script
                    }
                }
                simulations.append(dyn_sim)
    
    return simulations


def detect_format(config):
    """Detect which format the config is in.
    
    Returns:
        'simple' or 'standard'
    """
    if not config:
        return None
    
    # Simple format has 'accc', 'ascc', 'dinamico' at top level
    has_simple_sections = any(key in config for key in ['accc', 'ascc', 'dinamico'])
    
    # Standard format has 'simulations' at top level
    has_standard = 'simulations' in config
    
    if has_simple_sections and not has_standard:
        return 'simple'
    elif has_standard:
        return 'standard'
    else:
        return None


def normalize_config(config):
    """Convert config to standard 'simulations' format if needed.
    
    If simple format is detected, expand to simulations list.
    If already standard, return as-is.
    """
    fmt = detect_format(config)
    
    if fmt == 'simple':
        # Convert simple → standard
        simulations = expand_simple_format(config)
        return {
            'workspace': config.get('workspace', {'base_dir': '.'}),
            'simulations': simulations,
            'execution': config.get('execution', {}),
        }
    elif fmt == 'standard':
        return config
    else:
        return config
