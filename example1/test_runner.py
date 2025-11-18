import psse34
import psspy

sav, _ = psspy.sfiles()
psspy.beginreport()
for i in range(5):
    psspy.case(sav)    
    psspy.report("Prueba" + str(i) + "\n")
