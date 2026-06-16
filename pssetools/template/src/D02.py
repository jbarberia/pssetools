# pssetools
# Copyright (C) 2026 Barberia Juan Luis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v3.0 or later.
# See the LICENSE file for details.
import psspy
from pssetools.scripts.dinamico import correr_por, correr_hasta, falla_trifasica, aplica_dag

ibus, jbus, ckt = 11, 1008, "1"

# aplicacion falla
correr_hasta(segundos=1.0)
falla_monofasica(ibus, jbus, ckt, zf=0 + 0j)
correr_por(ciclos=4)

# despeje y apertura monofasica
psspy.dist_clear_fault(1)
apertura_fase_fallada(ibus, jbus, ckt)
correr_por(segundos=0.800)

# recierre exitoso
psspy.dist_clear_fault(1)
correr_hasta(segundos=30)
