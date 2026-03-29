# pssetools
# Copyright (C) 2026 Barberia Juan Luis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v3.0 or later.
# See the LICENSE file for details.

ibus = XXXX
jbus = YYYY
ckt  = "1"

# Falla monofasica.
psspy.run(0,1.0,0,0,0)
psspy.dist_spcb_fault_2(ibus,jbus,ckt,[3,0,1,1,0,0,0],[0.45,0.0, 100.0,0.0,0.0])

# Apertura fase fallada.
psspy.run(0,1.120,0,0,0)
psspy.dist_clear_fault(1)
psspy.dist_spcb_fault_2(ibus,jbus,ckt,[1,0,1,1,0,0,0],[0.0,0.0,0.0,0.0,0.0])

# Fin del tiempo muerto con reconexion exitosa - 800 ms
psspy.run(0,1.920,0,0,0)
psspy.dist_clear_fault(1)

# Fin.
psspy.run(0,30,0,0,0)
