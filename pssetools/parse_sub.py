# coding: latin-1
from . import psse34
from . import psspy
import re
from collections import namedtuple

Bus = namedtuple("Bus", ["number", "area", "owner", "zone", "kv"])

def parse_sub(filename):
    """Lee los valores del archivo de configuración de subsistema para poder 
    pasarlo a la función psspy.bsys.

    Args:
        filename (str): archivo de subsistema en formato *.sub

    Returns:
        dict: elementos del subsistema donde las llaves son los nombres y los valores son listas con las barras del subsistema.
    """

    # lee archivo
    with open(filename, "r") as f:
        file_string = f.read()

    # elimina comentarios
    file_string = remove_comments(file_string)

    # get block of subsystems
    blocks = get_subsystem_blocks(file_string)
    
    data = {}
    for block in blocks:

        # TODO obtnener bloques join

        name = get_name(block)
        sub_groups = get_join_blocks(block)
        # import pdb; pdb.set_trace()
        bus_subsystem = []
        
        for sub_group in sub_groups:
            kv_range = parse_kv(sub_group)
            areas = parse_areas(sub_group)
            buses = parse_buses(sub_group)
            owners = parse_owners(sub_group)
            zones = parse_zones(sub_group)

            elementos = [x for x in [kv_range, areas, buses, owners, zones] if len(x) > 0]   
            if elementos:
                bus_subsystem += list(set.intersection(*elementos))
            else:
                bus_subsystem += []

        data[name] = list(set(bus_subsystem))
    return data


def remove_comments(string):
    lines = string.splitlines()
    lines = [l for l in lines if not l.strip().startswith("COM")]
    string = "\n".join(lines)
    return string


def get_subsystem_blocks(string):
    blocks = []
    block = []

    keep_reading = False
    in_join_block = False

    for line in string.splitlines():
        if line.startswith("SUBSYSTEM") or line.startswith("SYSTEM"):
            block.append(line)
            keep_reading = True

        if line.startswith("JOIN"):
            in_join_block = True

        if line.startswith("END"):
            if in_join_block:
                keep_reading = True
                in_join_block = False
            else:
                keep_reading = False
                if len(block) > 0:
                    blocks.append("\n".join(block))
                block = []

        if keep_reading:
            block.append(line)

    # TODO: chequear bloques JOIN
    return blocks


def get_join_blocks(string):
    blocks = []
    block = []

    keep_reading = False
    in_join_block = False

    for line in string.splitlines():
        line = line.strip()

        if line.startswith("SUBSYSTEM") or line.startswith("SYSTEM"):
            # block.append(line)
            keep_reading = True
            continue

        if line.startswith("JOIN"):
            in_join_block = True
            continue

        if line.startswith("END"):
            if in_join_block:
                keep_reading = True
                in_join_block = False
            else:
                keep_reading = False
                if len(block) > 0:
                    blocks.append("\n".join(block))
                block = []

        if keep_reading:
            block.append(line)
            if not in_join_block:
                blocks.append("\n".join(block))
                block = []

    return blocks


def get_name(block):
    name = re.search(r"[SUBSYSTEM|SYSTEM]\s+(.*)", block).group(1)
    name = name.replace("'", "")
    name = name.replace('"', "")
    return name


def extract_buses(only_in_service=True):
    flag = 1 if only_in_service else 2       
    ierr1, (number, area, owner, zone,) = psspy.abusint(-1, flag, ["NUMBER", "AREA", "OWNER", "ZONE"])    
    ierr2, (kv,) = psspy.abusreal(-1, flag, ["BASE"])
    assert ierr1 == 0 and ierr2 == 0

    buses = []
    for i, bus in enumerate(number):
        buses.append(Bus(
            number[i],
            area[i],
            owner[i],
            zone[i],
            round(kv[i], 2),
        ))
    return buses


def parse_areas(block):
    "Devuelve los buses en las areas dadas"
    areas = []

    # single buses
    matches = re.findall("AREA\s+([0-9]{,6})", block)
    areas += [int(b) for b in matches]

    # multiples buses
    matches = re.findall("AREAS\s+([0-9]{,6})\s([0-9]{,6})", block)
    for match in matches:
        area1 = int(match[0])
        area2 = int(match[1])
        areas += [b for b in range(area1, area2 + 1)]

    # extrae buses 
    buses = extract_buses(only_in_service=True)
    buses = [b.number for b in buses if b.area in areas]

    
    if buses:
        return set(buses)
    else:
        return set()


def parse_buses(block):
    buses = []

    # single buses
    matches = re.findall("BUS\s+([0-9]{,6})", block)
    buses += [int(b) for b in matches]

    # multiples buses
    matches = re.findall("BUSES\s+([0-9]{,6})\s([0-9]{,6})", block)
    for match in matches:
        bus1 = int(match[0])
        bus2 = int(match[1])
        buses += [b for b in range(bus1 + 1, bus2)]

    # skip buses - simple
    buses_to_remove = []
    matches = re.findall("\s+SKIP BUS\s+([0-9]{,6})", block)
    buses_to_remove += [int(b) for b in matches]

    # skip buses with conditions
    # TODO - esta complicado
    
    # barras a mantener/eliminar
    buses_to_keep = set(buses)
    buses_to_remove = set(buses_to_remove)

    buses = extract_buses(only_in_service=True)
    buses = [b.number for b in buses if 
             (b.number in buses_to_keep) and not (b.number in buses_to_remove)]
    
    if buses:
        return set(buses)
    else:
        return set()
    

def parse_owners(block):
    "Devuelve los buses en los owners dados"
    owners = []

    # single buses
    matches = re.findall("OWNER\s+([0-9]{,6})", block)
    owners += [int(b) for b in matches]

    # multiples buses
    matches = re.findall("OWNERS\s+([0-9]{,6})\s([0-9]{,6})", block)
    for match in matches:
        owner1 = int(match[0])
        owner2 = int(match[1])
        owners += [b for b in range(owner1, owner2 + 1)]

    # extrae buses 
    buses = extract_buses(only_in_service=True)
    buses = [b.number for b in buses if b.owner in owners]
    if buses:
        return set(buses)
    else:
        return set()


def parse_zones(block):
    "Devuelve los buses en las zonas dadas"
    zones = []

    # single buses
    matches = re.findall("ZONE\s+([0-9]{,6})", block)
    zones += [int(b) for b in matches]

    # multiples buses
    matches = re.findall("ZONES\s+([0-9]{,6})\s([0-9]{,6})", block)
    for match in matches:
        zone1 = int(match[0])
        zone2 = int(match[1])
        zones += [b for b in range(zone1, zone2 + 1)]

    # extrae buses 
    buses = extract_buses(only_in_service=True)
    buses = [b.number for b in buses if b.zone in zones]
    if buses:
        return set(buses)
    else:
        return set()


def parse_kv(block):
    buses = extract_buses(only_in_service=True)

    # single buses
    match = re.search("KV\s+([0-9]{,6}\.{,1}[0-9]{,6})", block)
    if match:
        kv_value = float(match.group(1))
        buses = [b.number for b in buses if abs(b.kv - kv_value) / kv_value <= 1e-6]
        
        if buses:
            return set(buses)
        else:
            return set()

    # multiples buses
    match = re.search("KVRANGE\s+([0-9]{,6}\.{,1}[0-9]{,6})\s+([0-9]{,6}\.{,1}[0-9]{,6})", block)
    if match:
        lb = float(match.group(1))
        ub = float(match.group(2))
        buses = [b.number for b in buses if lb <= b.kv <= ub]

        if buses:
            return set(buses)
        else:
            return set()
        
    return set()

    