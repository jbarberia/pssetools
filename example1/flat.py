# ------------------------------------------------------------------------------
# FLAT RUN
# ------------------------------------------------------------------------------
psspy.set_relang(1,2620,'1')
psspy.set_voltage_dip_check(1,0.8,1.0)
psspy.set_vltscn(1,1.2,0.7)
psspy.trig_volt_violation_check(1)
psspy.set_relscn(1)
psspy.set_osscan(1,1)
psspy.run(0,30.0,0,0,0)
