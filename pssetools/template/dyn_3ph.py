# pssetools
# Copyright (C) 2026 Barberia Juan Luis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v3.0 or later.
# See the LICENSE file for details.

ibus = XXXX
jbus = YYYY
ckt  = "1"

# Falla trifasica.
psspy.run(0,1.0,0,0,0)
psspy.dist_branch_fault(ibus,jbus,ckt,1,0.0,[0.0,-0.2E+10])
psspy.run(0,1.120,0,0,0)

# Despejo falla.
psspy.dist_clear_fault(1)
psspy.dist_branch_trip(ibus,jbus,ckt)

# Fin.
psspy.run(0,30,0,0,0)
