# coding: latin-1
from __future__ import absolute_import, division, print_function, unicode_literals
try:
    import tkinter as tk    
except ImportError:
    import Tkinter as tk
from pssetools.tools.base_wizard import BaseWizardDialog, tkMessageBox
from pssetools.utils.sld import (
    get_selected_map_strings,
    get_bus_info,
    branch_label,
    three_winding_label,
    map_key,
)

class CustomACCCFileGenerator(BaseWizardDialog):
    """
    Generador de archivos TSV de monitoreo y rutinas de contingencias en Python
    interactuando con los elementos seleccionados en el diagrama unifilar (SLD).
    """
    def __init__(self, parent):
        super(CustomACCCFileGenerator, self).__init__(
            parent,
            title="List elements selected",
            geometry="650x350",
            resizable=(True, True)
        )
        self.create_text_tab(0, "MON", ".tsv", "mon_text", "1 - Generar Monitor", self.create_mon)
        self.create_text_tab(1, "CON", ".py", "con_text", "1 - Generar Contingency", self.create_con)

    def _iter_sld_tokens(self):
        try:
            for ms in get_selected_map_strings():
                yield ms
        except ImportError as e:
            tkMessageBox.showerror("Error de Entorno", str(e))
        except Exception as e:
            tkMessageBox.showwarning("Aviso", "No se pudo leer el diagrama SLD activo:\nError: {}".format(e))

    def _element_rows(self, psspy, map_string):
        kind = map_string[0]
        id1, id2, id3, id4 = (list(map_string[1:]) + [""] * 4)[:4]
        if kind in ("BU", "ME", "SWS", "LO", "FXS") and id1:
            name, _ = get_bus_info(psspy, int(id1))
            return [[kind, id1, id2, id3, id4, name]]
        if kind in ("LII", "TR", "SYS") and id1 and id2:
            ibus, jbus = int(id1), int(id2)
            ckt = id3 or "1"
            return [
                [kind, str(ibus), str(jbus), ckt, id4, branch_label(psspy, ibus, jbus, ckt)],
                [kind, str(jbus), str(ibus), ckt, id4, branch_label(psspy, jbus, ibus, ckt)],
            ]
        if kind == "T3" and id1 and id2 and id3:
            ibus, jbus, kbus = int(id1), int(id2), int(id3)
            ckt = id4 or "1"
            ierr, name = psspy.tr3nam(ibus, jbus, kbus, ckt)
            if ierr != 0:
                return []
            name = (name or "").strip()
            rows = []
            for winding, buses in enumerate(
                ((ibus, jbus, kbus), (jbus, kbus, ibus), (kbus, ibus, jbus)), start=1
            ):
                busi, busj, busk = buses
                rows.append([
                    kind, str(busi), str(busj), str(busk), ckt,
                    three_winding_label(psspy, busi, name, ckt, winding),
                ])
            return rows
        return []

    def create_mon(self, text_widget):
        import psspy
        content = []
        seen = set()
        for ms in self._iter_sld_tokens():
            try:
                rows = self._element_rows(psspy, ms)
            except (TypeError, ValueError):
                continue
            key = map_key(ms)
            if not rows or key in seen:
                continue
            seen.add(key)
            content.extend("\t".join(row) for row in rows)
        if content:
            txt = text_widget.get("1.0", tk.END)
            all_content = [line for line in txt.splitlines() if line.strip()]
            all_content.extend(content)
            text_widget.delete("1.0", tk.END)
            text_widget.insert(tk.END, "\n".join(all_content) + "\n")
            text_widget.see(tk.END)

    def create_con(self, text_widget):
        import psspy
        content = []
        for ms in self._iter_sld_tokens():
            kind = ms[0]
            if kind == "ME":
                busi = int(ms[1])
                mid = ms[2]
                ierr, name = psspy.notona(busi)
                name = (name[:12].strip() if name else "")
                content.append("def GEN_{}_{}():".format(ms[1], ms[2]))
                content.append('    "F/S {}"'.format(name))
                content.append("    psspy.machine_chng_2({},'{}',intgar1=0, realar1=_f)".format(busi, mid))
                content.append("")
            elif kind == "LO":
                busi = int(ms[1])
                lid = ms[2]
                ierr, name = psspy.notona(busi)
                name = (name[:12].strip() if name else "")
                content.append("def LOAD_{}_{}():".format(ms[1], ms[2]))
                content.append('    "F/S {}"'.format(name))
                content.append("    psspy.load_chng_5({},'{}',intgar1=0, realar1=_f, realar2=_f)".format(busi, lid))
                content.append("")
            elif kind == "T3":
                busi, busj, busk, ckt = int(ms[1]), int(ms[2]), int(ms[3]), ms[4]
                ierr, name = psspy.tr3nam(busi, busj, busk, ckt)
                name = (name or "").strip() or "{}_{}_{}_{}".format(busi, busj, busk, ckt)
                content.append("def TRAFO_{}():".format(name.replace("-", "_").replace("#", "_")))
                content.append('    "F/S {}"'.format(name))
                content.append("    psspy.three_wnd_imped_chng_4({},{},{},'{}', intgar8=0)".format(busi, busj, busk, ckt))
                content.append("")
            elif kind == "LII":
                busi, busj, ckt = int(ms[1]), int(ms[2]), ms[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)
                name = (name or "").strip() or "{}-{}#{}".format(busi, busj, ckt)
                content.append("def BRANCH_{}():".format(name.replace("-", "_").replace("#", "_")))
                content.append('    "F/S {}"'.format(name))
                content.append("    psspy.branch_chng_3({},{},'{}', intgar1=0)".format(busi, busj, ckt))
                content.append("")
            elif kind == "TR":
                busi, busj, ckt = int(ms[1]), int(ms[2]), ms[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)
                name = (name or "").strip() or "{}-{}#{}".format(busi, busj, ckt)
                content.append("def BRANCH_{}():".format(name.replace("-", "_").replace("#", "_")))
                content.append('    "F/S {}"'.format(name))
                content.append("    psspy.two_winding_chng_6({},{},'{}', intgar1=0)".format(busi, busj, ckt))
                content.append("")
            elif kind == "SYS":
                busi, busj, ckt = int(ms[1]), int(ms[2]), ms[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)
                name = (name or "").strip() or "{}-{}#{}".format(busi, busj, ckt)
                content.append("def BRANCH_{}():".format(name.replace("-", "_").replace("#", "_")))
                content.append('    "F/S {}"'.format(name))
                content.append("    psspy.system_swd_chng({},{},'{}', intgar1=0)".format(busi, busj, ckt))
                content.append("")

        if content:
            header = (
                "import psse34\n"
                "import psspy\n\n"
                "_i = psspy.getdefaultint()\n"
                "_f = psspy.getdefaultreal()\n"
                "_s = psspy.getdefaultchar()\n\n"
                "def base():\n"
                "    \"CASO-BASE\"\n"
                "    pass\n\n"
            )
            current_txt = text_widget.get("1.0", tk.END).strip()
            new_content = "\n".join(content)
            header_text = header.strip()
            if current_txt.startswith(header_text):
                current_txt = current_txt[len(header_text):].lstrip()
            sections = [header_text]
            if current_txt:
                sections.append(current_txt)
            sections.append(new_content)
            full_txt = "\n\n".join(sections)
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", full_txt + "\n")
