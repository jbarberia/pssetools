# coding: latin-1
from __future__ import absolute_import, division, print_function, unicode_literals

import io
import re
from collections import namedtuple

Bus = namedtuple("Bus", ["number", "area", "owner", "zone", "kv"])


def parse_sub(filename):
    """Parsea archivos de subsistema (.sub) utilizando cache en memoria de barras."""
    with io.open(filename, "r", encoding="latin-1") as f:
        file_string = f.read()

    file_string = remove_comments(file_string)
    blocks = get_subsystem_blocks(file_string)

    # Optimizacion critica: Consultar las barras activas de PSS/E una sola vez
    buses_cache = extract_buses(only_in_service=True)

    data = {}
    for block in blocks:
        name = get_name(block)
        sub_groups = get_join_blocks(block)
        bus_subsystem = []

        for sub_group in sub_groups:
            kv_range = parse_kv(sub_group, buses_cache)
            areas = parse_areas(sub_group, buses_cache)
            buses = parse_buses(sub_group, buses_cache)
            owners = parse_owners(sub_group, buses_cache)
            zones = parse_zones(sub_group, buses_cache)

            elementos = [x for x in [kv_range, areas, buses, owners, zones] if len(x) > 0]
            if elementos:
                bus_subsystem.extend(set.intersection(*elementos))

        data[name] = sorted(list(set(bus_subsystem)))
    return data


def remove_comments(string):
    """Elimina lineas comentadas con prefijo 'COM'."""
    return "\n".join(l for l in string.splitlines() if not l.strip().startswith("COM"))


def get_subsystem_blocks(string):
    """Extrae bloques SUBSYSTEM o SYSTEM corrigiendo la sintaxis regex."""
    blocks = []
    block = []
    keep_reading = False
    in_join_block = False

    for line in string.splitlines():
        # Uso de prefijo estricto
        if line.startswith("SUBSYSTEM") or line.startswith("SYSTEM"):
            block.append(line)
            keep_reading = True
        elif line.startswith("JOIN"):
            in_join_block = True
        elif line.startswith("END"):
            if in_join_block:
                keep_reading = True
                in_join_block = False
            else:
                keep_reading = False
                if block:
                    blocks.append("\n".join(block))
                block = []
                continue

        if keep_reading and line not in block:
            block.append(line)

    return blocks


def get_join_blocks(string):
    """Extrae sub-bloques de agrupacion JOIN dentro de una definicion."""
    blocks = []
    block = []
    keep_reading = False
    in_join_block = False

    for line in string.splitlines():
        line_s = line.strip()
        if line_s.startswith("SUBSYSTEM") or line_s.startswith("SYSTEM"):
            keep_reading = True
            continue
        if line_s.startswith("JOIN"):
            in_join_block = True
            continue
        if line_s.startswith("END"):
            if in_join_block:
                keep_reading = True
                in_join_block = False
            else:
                keep_reading = False
                if block:
                    blocks.append("\n".join(block))
                block = []
                continue

        if keep_reading:
            block.append(line)
            if not in_join_block and block:
                blocks.append("\n".join(block))
                block = []
    return blocks


def get_name(block):
    """Extrae el nombre de la definicion con regex de grupo correcta."""
    # Corregido: (?:SUBSYSTEM|SYSTEM) en lugar del erroneo [SUBSYSTEM|SYSTEM]
    match = re.search(r"^(?:SUBSYSTEM|SYSTEM)\s+['\"]?([^'\"\n\r]+)['\"]?", block, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "UNKNOWN"


def extract_buses(only_in_service=True):
    """Consulta la API de PSS/E de forma segura y devuelve una lista de namedtuples."""
    import psspy

    flag = 1 if only_in_service else 2
    ierr1, (number, area, owner, zone) = psspy.abusint(-1, flag, ["NUMBER", "AREA", "OWNER", "ZONE"])
    ierr2, (kv,) = psspy.abusreal(-1, flag, ["BASE"])
    if ierr1 != 0 or ierr2 != 0:
        return []

    return [
        Bus(number[i], area[i], owner[i], zone[i], round(kv[i], 2))
        for i in range(len(number))
    ]


def parse_areas(block, buses):
    areas = set()
    for m in re.finditer(r"\bAREA\s+([0-9]{1,6})\b", block):
        areas.add(int(m.group(1)))
    for m in re.finditer(r"\bAREAS\s+([0-9]{1,6})\s+([0-9]{1,6})\b", block):
        areas.update(range(int(m.group(1)), int(m.group(2)) + 1))
    return {b.number for b in buses if b.area in areas} if areas else set()


def parse_buses(block, buses):
    buses_to_keep = set()
    for m in re.finditer(r"\bBUS\s+([0-9]{1,6})\b", block):
        buses_to_keep.add(int(m.group(1)))
    # Corregido: limite superior inclusivo bus2 + 1
    for m in re.finditer(r"\bBUSES\s+([0-9]{1,6})\s+([0-9]{1,6})\b", block):
        buses_to_keep.update(range(int(m.group(1)), int(m.group(2)) + 1))

    buses_to_remove = {int(m.group(1)) for m in re.finditer(r"\bSKIP\s+BUS\s+([0-9]{1,6})\b", block)}
    active_bus_numbers = {b.number for b in buses}
    return (buses_to_keep - buses_to_remove) & active_bus_numbers


def parse_owners(block, buses):
    owners = set()
    for m in re.finditer(r"\bOWNER\s+([0-9]{1,6})\b", block):
        owners.add(int(m.group(1)))
    for m in re.finditer(r"\bOWNERS\s+([0-9]{1,6})\s+([0-9]{1,6})\b", block):
        owners.update(range(int(m.group(1)), int(m.group(2)) + 1))
    return {b.number for b in buses if b.owner in owners} if owners else set()


def parse_zones(block, buses):
    zones = set()
    for m in re.finditer(r"\bZONE\s+([0-9]{1,6})\b", block):
        zones.add(int(m.group(1)))
    for m in re.finditer(r"\bZONES\s+([0-9]{1,6})\s+([0-9]{1,6})\b", block):
        zones.update(range(int(m.group(1)), int(m.group(2)) + 1))
    return {b.number for b in buses if b.zone in zones} if zones else set()


def parse_kv(block, buses):
    m_kv = re.search(r"\bKV\s+([0-9]+\.?[0-9]*)\b", block)
    if m_kv:
        kv_val = float(m_kv.group(1))
        return {b.number for b in buses if abs(b.kv - kv_val) <= 0.01}

    m_range = re.search(r"\bKVRANGE\s+([0-9]+\.?[0-9]*)\s+([0-9]+\.?[0-9]*)\b", block)
    if m_range:
        lb, ub = float(m_range.group(1)), float(m_range.group(2))
        return {b.number for b in buses if lb <= b.kv <= ub}

    return set()
