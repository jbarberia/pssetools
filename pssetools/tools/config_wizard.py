# coding: latin-1
from __future__ import absolute_import, division, print_function, unicode_literals
try:
    import tkinter as tk    
except ImportError:
    import Tkinter as tk
from pssetools.tools.base_wizard import BaseWizardDialog, tkMessageBox
from pssetools.utils.sld import get_selected_map_strings

class ConfigWizardApp(BaseWizardDialog):
    """
    Asistente para generar archivos de configuracion (.sub, .mon, .con, .idv)
    a partir de elementos seleccionados en el diagrama unifilar (SLD) de PSS/E.
    """
    def __init__(self, parent):
        super(ConfigWizardApp, self).__init__(
            parent,
            title="Config File Wizard",
            geometry="650x350",
            resizable=(False, True)
        )
        self.sub_number = 0
        self.create_text_tab(0, "SUB", ".sub", "sub_text", "1 - Generar Subsystem", self.create_sub)
        self.create_text_tab(1, "MON", ".mon", "mon_text", "1 - Generar Monitor", self.create_mon)
        self.create_text_tab(2, "CON", ".con", "con_text", "1 - Generar Contingency", self.create_con)
        self.create_text_tab(3, "CHAN", ".idv", "chan_text", "1 - Generar Channel", self.create_chan)

    def _iter_sld_tokens(self):
        try:
            for ms in get_selected_map_strings():
                yield ms
        except ImportError as e:
            tkMessageBox.showerror("Error de Entorno", str(e))
        except Exception as e:
            tkMessageBox.showwarning("Aviso", "No se pudo leer el diagrama SLD activo:\nError: {}".format(e))

    def create_sub(self, text_widget):
        content = []
        for ms in self._iter_sld_tokens():
            elem = ms[0]
            if elem in ("BU", "ME", "SWS", "LO", "FXS"):
                content.append("BUS {}".format(int(ms[1])))
            elif elem in ("TR", "SYS", "LII"):
                content.append("BUS {}".format(int(ms[1])))
                content.append("BUS {}".format(int(ms[2])))
            elif elem == "T3":
                content.append("BUS {}".format(int(ms[1])))
                content.append("BUS {}".format(int(ms[2])))
                content.append("BUS {}".format(int(ms[3])))
        if content:
            self.sub_number += 1
            content.insert(0, "SUBSYSTEM 'SYSTEM_{:02d}'".format(self.sub_number))
            content.append("END\n")
            txt = text_widget.get("1.0", tk.END)
            text_widget.delete("1.0", tk.END)
            txt = "END".join(txt.split("END")[:-1])
            text_widget.insert(tk.INSERT, txt + "\n".join(content) + "\nEND\n")

    def create_mon(self, text_widget):
        content = []
        for ms in self._iter_sld_tokens():
            elem = ms[0]
            if elem in ("BU", "ME", "SWS", "LO", "FXS"):
                content.append("MONITOR VOLTAGE LIMIT BUS {}".format(int(ms[1])))
            elif elem in ("TR", "SYS", "LII"):
                content.append("MONITOR BRANCH FROM BUS {} TO BUS {} CKT {}".format(int(ms[1]), int(ms[2]), ms[3]))
            elif elem == "T3":
                content.append("MONITOR BRANCH FROM BUS {} TO BUS {} TO BUS {} CKT {}".format(int(ms[1]), int(ms[2]), int(ms[3]), ms[4]))
        if content:
            txt = text_widget.get("1.0", tk.END)
            text_widget.delete("1.0", tk.END)
            txt = "END".join(txt.split("END")[:-1])
            text_widget.insert(tk.INSERT, txt + "\n".join(content) + "\nEND\n")

    def create_con(self, text_widget):
        import psspy
        content = []
        for ms in self._iter_sld_tokens():
            elem = ms[0]
            if elem == "ME":
                busi = int(ms[1])
                content.append("CONTINGENCY GEN-{}".format(busi))
                content.append("DISCONNECT BUS {}".format(busi))
                content.append("END\n")
            elif elem == "T3":
                busi, busj, busk, ckt = int(ms[1]), int(ms[2]), int(ms[3]), ms[4]
                ierr, name = psspy.tr3nam(busi, busj, busk, ckt)
                name = (name or "").strip() or "{}-{}-{}#{}".format(busi, busj, busk, ckt)
                content.append("CONTINGENCY {}".format(name))
                content.append("OPEN BRANCH FROM BUS {} TO BUS {} TO BUS {} CIRCUIT {}".format(busi, busj, busk, ckt))
                content.append("END\n")
            elif elem in ("TR", "SYS", "LII"):
                busi, busj, ckt = int(ms[1]), int(ms[2]), ms[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)
                name = (name or "").strip() or "{}-{}#{}".format(busi, busj, ckt)
                content.append("CONTINGENCY {}".format(name))
                content.append("OPEN BRANCH FROM BUS {} TO BUS {} CKT {}".format(busi, busj, ckt))
                content.append("END\n")
        if content:
            txt = text_widget.get("1.0", tk.END)
            text_widget.delete("1.0", tk.END)
            txt = "END".join(txt.split("END")[:-1])
            text_widget.insert(tk.INSERT, txt + "\n".join(content) + "\nEND\n")

    def create_chan(self, text_widget):
        import psspy
        canales = []
        for ms in self._iter_sld_tokens():
            elem = ms[0]
            if elem == "BU":
                busi = int(ms[1])
                ierr, name = psspy.notona(busi)
                name = (name or "").strip()
                canales.append("BAT_BUS_FREQUENCY_CHANNEL -1 {} 'FREC {} - {}'".format(busi, busi, name))
                canales.append("BAT_VOLTAGE_CHANNEL -1 -1 -1 {} 'U {} - {}'".format(busi, busi, name))
            elif elem == "ME":
                busi, identifier = int(ms[1]), ms[2]
                ierr, name = psspy.notona(busi)
                name = (name[:12].strip() if name else "") + " - " + identifier
                canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 1 {} '{}' '{} - ANGLE'".format(busi, identifier, name))
                canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 2 {} '{}' '{} - PELEC'".format(busi, identifier, name))
                canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 3 {} '{}' '{} - QELEC'".format(busi, identifier, name))
                canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 4 {} '{}' '{} - ETERM'".format(busi, identifier, name))
                canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 7 {} '{}' '{} - SPEED'".format(busi, identifier, name))
            elif elem == "T3":
                busi, busj, busk, ckt = int(ms[1]), int(ms[2]), int(ms[3]), ms[4]
                ierr, trname = psspy.tr3nam(busi, busj, busk, ckt)
                trname = (trname or "").strip()
                canales.append("BAT_THREE_WND_MVA_CHANNEL -1 -1 -1 {} {} {} '{}' '{} - MVA'".format(busi, busj, busk, ckt, trname))
            elif elem in ("TR", "SYS", "LII"):
                busi, busj, ckt = int(ms[1]), int(ms[2]), ms[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)
                name = (name or "").strip() or "{}-{} CKT {}".format(busi, busj, ckt)
                canales.append("BAT_BRANCH_MVA_CHANNEL -1 -1 -1 {} {} '{}' '{} - MVA'".format(busi, busj, ckt, name))
        if canales:
            text_widget.insert(tk.INSERT, "\n".join(canales) + "\n")
