from __future__ import print_function
import Tkinter as tk
import psse34
import psspy
import sliderPy
import sys
import re

sys.argv = ["psse"]

def sub_mon_con():
    """Generates subsystem, monitor, and contingency definitions from selected SLD elements.

    Identifies selected components in the active SLD (SliderPy) and 
    extracts bus, machine, transformer, and branch info to create
    formatted PSS/E report-style configuration.
    """
    mydoc = sliderPy.GetActiveDocument()
    diagram = mydoc.GetDiagram()
    components = diagram.GetComponents()

    subsystem = []
    monitor = []
    contingency = []
    for component in components:
        if component.IsSelected() == False:
            continue
        
        map_string = re.findall(r"\S+", component.GetMapString())
        if len(map_string) == 0:
            continue

        if map_string[0] in ["BU", "ME", "SWS", "LO", "FXS"]:
            busi = int(map_string[1])
            monitor.append("MONITOR VOLTAGE LIMIT BUS {}".format(busi))
            subsystem.append("BUS {}".format(busi))
            # monitor.append("MONITOR VOLTAGE DEVIATION BUS {} 0.01 0.01".format(busi))
        
        if map_string[0] in ["ME"]:
            busi = int(map_string[1])
            contingency.append("CONTINGENCY GEN-{}".format(busi))
            contingency.append("DISCONNECT BUS {}".format(busi))
            contingency.append("END")

        elif map_string[0] == "T3":
            busi = int(map_string[1])
            busj = int(map_string[2])
            busk = int(map_string[3])
            ckt = map_string[4]
                                  
            monitor.append("MONITOR BRANCH FROM BUS {} TO BUS {} TO BUS {} CKT {}".format(busi, busj, busk, ckt))
            
            contingency.append("CONTINGENCY {}-{}-{}-{}".format(busi, busj, busk, ckt))
            contingency.append("OPEN BRANCH FROM BUS {} TO BUS {} TO BUS {} CIRCUIT {}".format(busi, busj, busk, ckt))
            contingency.append("END")

        elif map_string[0] in ["TR", "SYS", "LII"]:
            busi = int(map_string[1])
            busj = int(map_string[2])
            ckt = map_string[3]
            
            ierr, name = psspy.brnnam(busi, busj, ckt)
            name = name.strip()
            if not name:
                name = "{}-{}#{}".format(busi, busj, ckt)

            monitor.append("MONITOR BRANCH FROM BUS {} TO BUS {} CKT {}".format(busi, busj, ckt))
            contingency.append("CONTINGENCY {}".format(name))
            contingency.append("OPEN BRANCH FROM BUS {} TO BUS {} CKT {}".format(busi, busj, ckt))
            contingency.append("END")
    
    sub_content = "\n".join(subsystem)
    con_content = "\n".join(contingency)
    mon_content = "\n".join(monitor)

    psspy.beginreport()
    psspy.report("SUBSYSTEM 'SYSTEM'\n")
    psspy.report(sub_content)
    psspy.report("\nEND")
    psspy.report("\nEND")

    psspy.beginreport()
    psspy.report(con_content)
    psspy.report("\nEND")

    psspy.beginreport()
    psspy.report(mon_content)
    psspy.report("\nEND")


def canales():
    """Extracts dynamic recording channels from selected SLD elements.

    Identifies selected buses, machines, and branches in the active SLD 
    and generates PSS/E batch commands to add frequency, voltage, 
    power, and speed recording channels.
    """
    mydoc = sliderPy.GetActiveDocument()
    diagram = mydoc.GetDiagram()
    components = diagram.GetComponents()

    canales = []
    for component in components:
        if component.IsSelected() == False:
            continue
        
        map_string = re.findall(r"\S+", component.GetMapString())
        if len(map_string) == 0:
            continue

        if map_string[0] in ["BU"]:
            busi = int(map_string[1])
            ierr, name = psspy.notona(busi)
            name = name.strip()
            canales.append("BAT_BUS_FREQUENCY_CHANNEL -1 {} 'FREC {} - {}'".format(busi, busi, name))
            canales.append("BAT_VOLTAGE_CHANNEL -1 -1 -1 {} 'U {} - {}'".format(busi, busi, name))
        
        if map_string[0] in ["ME"]:
            busi = int(map_string[1])
            identifier = map_string[2]
            ierr, name = psspy.notona(busi)
            name = name[:12].strip()
            canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 1 {} '{}' '{} - ANGLE'".format(busi, identifier, name))
            canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 2 {} '{}' '{} - PELEC'".format(busi, identifier, name))
            canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 3 {} '{}' '{} - QELEC'".format(busi, identifier, name))
            canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 4 {} '{}' '{} - ETERM'".format(busi, identifier, name))
            canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 7 {} '{}' '{} - SPEED'".format(busi, identifier, name))

        elif map_string[0] == "T3":
            busi = int(map_string[1])
            busj = int(map_string[2])
            busk = int(map_string[3])
            ckt = map_string[4]  
            ierr, trname = psspy.tr3nam(busi, busj, busk, ckt)
            trname = trname.strip()
            canales.append("BAT_THREE_WND_MVA_CHANNEL -1 -1 -1 {} {} {} '{}' '{} - MVA'".format(busi, busj, busk, ckt, trname))
            
        elif map_string[0] in ["TR", "SYS", "LII"]:
            busi = int(map_string[1])
            busj = int(map_string[2])
            ckt = map_string[3]
            ierr, name = psspy.brnnam(busi, busj, ckt)
            name = name.strip()
            if not name:
                name = "{}-{} CKT {}".format(busi, busj, ckt)
            canales.append("BAT_BRANCH_MVA_CHANNEL -1 -1 -1 {} {} '{}' '{} - MVA'".format(busi, busj, ckt, name))
            
    content = "\n".join(canales)
    psspy.beginreport()
    psspy.report(content)
    
    
def gui():
    """Initializes and displays the PSSETOOLS Tkinter window.

    Creates a compact, floating GUI with options to generate
    definitions or add channels based on active diagram selection.
    """
    # Create window
    root = tk.Tk()
    root.title("PSSETOOLS")
    root.geometry("200x100")
    root.attributes("-topmost", True)

    # Create buttons
    btn1 = tk.Button(root, text="SUB - MON - CON", command=sub_mon_con)
    btn2 = tk.Button(root, text="CHANNELS", command=canales)

    # Layout
    btn1.pack(pady=5, expand=True)
    btn2.pack(pady=5, expand=True)

    # Start GUI loop
    root.mainloop()

if __name__ == "__main__":
    gui()
