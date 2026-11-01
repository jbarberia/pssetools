# coding: latin-1
import os
import sys
import re

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog as tkFileDialog
    from tkinter import messagebox as tkMessageBox
except ImportError:
    import Tkinter as tk
    import ttk
    import tkFileDialog
    import tkMessageBox


class CustomACCCFileGenerator(object):
    """
    Asistente para generar archivos de configuración PSS/E interactuando 
    con el diagrama SLD activo.
    """
    def __init__(self, parent):
        if not sys.argv:
            sys.argv = ["gui"]

        # Convertimos tk.Tk() a tk.Toplevel(parent) para que sea una ventana secundaria
        self.root = tk.Toplevel(parent)
        self.root.title("List elements selected")
        self.root.attributes("-topmost", True)
        self.root.geometry("650x350")
        self.root.resizable(True, True)

        self.tab_config = {
            0: {"ext": ".tsv", "attr": "mon_text", "label": "Monitor"},
            1: {"ext": ".py", "attr": "con_text", "label": "Contingency"},

        }

        self.sub_number = 0

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Load", command=self.load_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save All", command=self.save_all, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Load All", command=self.load_all, accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="Close", command=self.exit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        self.create_mon_tab("MON")
        self.create_con_tab("CON")        

        self.root.bind("<Control-Tab>", self.next_tab)
        self.root.bind("<Control-Shift-Tab>", self.prev_tab)
        self.root.bind("<Control-w>", self.exit)
        self.root.bind("<Control-Key-1>", self.handle_ctrl_1)
        self.root.bind("<Alt-Key-1>", self.handle_ctrl_1)
        self.root.bind("<Control-a>", self.select_all)
        self.root.bind("<Control-A>", self.select_all)
        
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-o>", lambda e: self.load_file())
        self.root.bind("<Control-S>", lambda e: self.save_all())
        self.root.bind("<Control-O>", lambda e: self.load_all())

    def next_tab(self, event=None):
        current = self.notebook.index(self.notebook.select())
        total = self.notebook.index("end")
        self.notebook.select((current + 1) % total)
        return "break"

    def prev_tab(self, event=None):
        current = self.notebook.index(self.notebook.select())
        total = self.notebook.index("end")
        self.notebook.select((current - 1) % total)
        return "break"

    def save_file(self):
        idx = self.notebook.index(self.notebook.select())
        conf = self.tab_config[idx]
        text_widget = getattr(self, conf["attr"])
        filename = tkFileDialog.asksaveasfilename(
            defaultextension=conf["ext"], filetypes=[(conf["label"], "*{}".format(conf["ext"])), ("All Files", "*.*")]
        )
        if filename:
            with open(filename, 'w') as f:
                f.write(text_widget.get("1.0", tk.END).encode('utf-8'))

    def load_file(self):
        idx = self.notebook.index(self.notebook.select())
        conf = self.tab_config[idx]
        text_widget = getattr(self, conf["attr"])
        filename = tkFileDialog.askopenfilename(filetypes=[(conf["label"], "*{}".format(conf["ext"])), ("All Files", "*.*")])
        if filename:
            with open(filename, 'r') as f:
                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", f.read().decode('utf-8'))

    def save_all(self):
        base_path = tkFileDialog.asksaveasfilename(title="Select Base Filename for All Configs")
        if base_path:
            base_name = os.path.splitext(base_path)[0]
            for idx, conf in self.tab_config.items():
                text_widget = getattr(self, conf["attr"])
                full_path = "{}{}".format(base_name, conf["ext"])
                with open(full_path, 'w') as f:
                    f.write(text_widget.get("1.0", tk.END).encode('utf-8'))
            tkMessageBox.showinfo("Success", "All files saved with base name: " + base_name)

    def load_all(self):
        base_path = tkFileDialog.askopenfilename(title="Select any file from the set to load all")
        if base_path:
            base_name = os.path.splitext(base_path)[0]
            for idx, conf in self.tab_config.items():
                full_path = "{}{}".format(base_name, conf["ext"])
                if os.path.exists(full_path):
                    text_widget = getattr(self, conf["attr"])
                    with open(full_path, 'r') as f:
                        text_widget.delete("1.0", tk.END)
                        text_widget.insert("1.0", f.read().decode('utf-8'))

    def exit(self, event=None):
        self.root.destroy()
        return "break"

    def handle_ctrl_1(self, event=None):
        current = self.notebook.index(self.notebook.select())
        if current == 0: self.create_mon(self.mon_text)
        elif current == 1: self.create_con(self.con_text)
        return "break"

    def select_all(self, event=None):    
        widget = self.root.focus_get()
        if isinstance(widget, tk.Text):
            widget.tag_add("sel", "1.0", "end-1c")
            widget.mark_set("insert", "1.0")
            widget.see("insert")
            return "break"  # Prevents default behavior/propagation

    # --- UI GENERATION ---
    def _create_frame(self, name):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=name)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        return frame

    def _create_text(self, frame):
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=0, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        text = tk.Text(text_frame, wrap="none", yscrollcommand=scrollbar.set, font=("Courier New", 10))
        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)
        return text


    def create_mon_tab(self, name):
        frame = self._create_frame(name)
        text = self._create_text(frame)
        self.mon_text = text
        ttk.Button(frame, text="1 - Generar Monitor", command=lambda: self.create_mon(text)).grid(row=0, column=1, sticky="n", pady=5, padx=5)

    def create_con_tab(self, name):
        frame = self._create_frame(name)
        text = self._create_text(frame)
        self.con_text = text
        ttk.Button(frame, text="1 - Generar Contingency", command=lambda: self.create_con(text)).grid(row=0, column=1, sticky="n", pady=5, padx=5)


    # --- LÓGICA CON PSS/E ---
    def get_map_string_in_sld(self):
        try:
            import sliderPy
        except ImportError:
            tkMessageBox.showerror("Error de Entorno", "El módulo sliderPy no está disponible.\nEsta herramienta solo funciona si abres la suite desde dentro de la GUI de PSS/E.")
            return

        try:
            mydoc = sliderPy.GetActiveDocument()
            diagram = mydoc.GetDiagram()
            components = diagram.GetComponents()
            for component in components:
                if component.IsSelected():
                    map_string = re.findall(r"\S+", component.GetMapString())
                    if map_string:
                        yield map_string
        except Exception as e:
            tkMessageBox.showwarning("Aviso", "No se pudo leer el diagrama SLD activo.\nAsegúrate de tener un diagrama abierto en PSS/E y elementos seleccionados.\nError: {}".format(e))



    # --- HELPERS DE FORMATO ---
    @staticmethod
    def _bus_info(psspy, bus):
        """
        Devuelve (nombre, tension base) de la barra `bus`.
        Si PSS/E no la encuentra, usa su numero y 0.0.
        """
        name = str(bus)
        ierr, value = psspy.notona(bus)
        if ierr == 0 and value and value.strip():
            name = value.strip()
        kv = 0.0
        ierr, value = psspy.busdat(bus, "BASE")
        if ierr == 0:
            kv = value
        return name, kv

    def _branch_label(self, psspy, ibus, jbus, ckt):
        """
        Etiqueta de una rama con el mismo formato que PSS/E:
            2201     SNIC.OESTE  132.00   2387     SNICOLA4    132.00 1
        """
        iname, ikv = self._bus_info(psspy, ibus)
        jname, jkv = self._bus_info(psspy, jbus)
        return "{:<9d}{:<12s}{:6.2f}   {:<9d}{:<12s}{:6.2f} {}".format(
            ibus, iname[:12], ikv, jbus, jname[:12], jkv, ckt
        )

    def _three_winding_label(self, psspy, bus, name, ckt, winding):
        """
        Etiqueta de un devanado de un transformador de tres arrollamientos,
        con el mismo formato que PSS/E: la barra del devanado ocupa el lugar de
        la barra de origen y el nombre del trafo el de la barra de destino:
            2106     RAMALLOB    220.00 3WNDTR T1RA             WND 1 1
        """
        iname, ikv = self._bus_info(psspy, bus)
        return "{:<9d}{:<12s}{:6.2f} {:<6s} {:<17s}{:<6s}{}".format(
            bus, iname[:12], ikv, "3WNDTR", name[:17], "WND {}".format(winding), ckt
        )

    @staticmethod
    def _map_key(map_string):
        """
        Identidad del elemento, para no listarlo dos veces cuando el SLD lo
        devuelve una vez por terminal. El sentido de las ramas y el orden de
        las barras de un trafo de tres arrollamientos no cambian la identidad.
        """
        kind = map_string[0]
        if kind in ("LII", "TR", "SYS") and len(map_string) >= 3:
            ckt = map_string[3] if len(map_string) > 3 else ""
            return (kind, tuple(sorted(map_string[1:3])), ckt)
        if kind == "T3" and len(map_string) >= 4:
            ckt = map_string[4] if len(map_string) > 4 else ""
            return ("T3", tuple(sorted(map_string[1:4])), ckt)
        return tuple(map_string)

    def _element_rows(self, psspy, map_string):
        """
        Traduce un map string del SLD a una o mas filas de 6 columnas:
        ELEMENTO, ID1, ID2, ID3, ID4 y DESCRIPCION.

        Cada rama genera los dos sentidos (i-j y j-i). Un transformador de tres
        arrollamientos genera una fila por devanado, rotando las barras para
        que el devanado quede primero (i-j-k, j-k-i, k-i-j):

            linea:     2201     SNIC.OESTE  132.00   2387     SNICOLA4    132.00 1
                       2387     SNICOLA4    132.00   2201     SNIC.OESTE  132.00 1
            trafo 3W:  2106     RAMALLOB    220.00 3WNDTR T1RA             WND 1 1
                       2107     BARRA2      132.00 3WNDTR T1RA             WND 2 1
                       2108     BARRA3       13.80 3WNDTR T1RA             WND 3 1
        """
        kind = map_string[0]
        id1, id2, id3, id4 = (list(map_string[1:]) + [""] * 4)[:4]

        if kind in ("BU", "ME", "SWS", "LO", "FXS") and id1:
            name, _ = self._bus_info(psspy, int(id1))
            return [[kind, id1, id2, id3, id4, name]]

        if kind in ("LII", "TR", "SYS") and id1 and id2:
            ibus, jbus = int(id1), int(id2)
            ckt = id3 or "1"
            return [
                [kind, str(ibus), str(jbus), ckt, id4,
                 self._branch_label(psspy, ibus, jbus, ckt)],
                [kind, str(jbus), str(ibus), ckt, id4,
                 self._branch_label(psspy, jbus, ibus, ckt)],
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
                    self._three_winding_label(psspy, busi, name, ckt, winding),
                ])
            return rows

        return []

    def create_mon(self, text_widget):
        """
        Agrega las filas de los elementos seleccionados en el SLD.

        Cada fila conserva el formato de 6 columnas del TSV
        (ELEMENTO, ID1, ID2, ID3, ID4 y DESCRIPCION) y la descripción muestra
        las barras, su tensión y el circuito, igual que la etiqueta de PSS/E.
        Un transformador de tres arrollamientos agrega una fila por devanado.
        """
        import psspy
        content = []
        seen = set()
        for ms in self.get_map_string_in_sld():
            try:
                rows = self._element_rows(psspy, ms)
            except (TypeError, ValueError):
                continue
            key = self._map_key(ms)
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
        for ms in self.get_map_string_in_sld():
            if ms[0] == "ME":
                busi = int(ms[1])
                id = ms[2]
                ierr, name = psspy.notona(int(ms[1]))
                name = name[:12].strip()
                content.append("def GEN_{}_{}():".format(ms[1], ms[2]))
                content.append('    "F/S {}"'.format(name))
                content.append("    psspy.machine_chng_2({},{},intgar1=0, realar1=_f)".format(busi, id))
                content.append("")

            if ms[0] == "LO":
                busi = int(ms[1])
                id = ms[2]
                ierr, name = psspy.notona(int(ms[1]))
                name = name[:12].strip()
                content.append("def LOAD_{}_{}():".format(ms[1], ms[2]))
                content.append('    "F/S {}"'.format(name))
                content.append("    psspy.load_chng_5({},'{}',intgar1=0, realar1=_f, realar2=_f)".format(busi, id))
                content.append("")

            if ms[0] == "T3":
                busi, busj, busk, ckt = int(ms[1]), int(ms[2]), int(ms[3]), ms[4]
                ierr, name = psspy.tr3nam(busi, busj, busk, ckt)
                name = name.strip() or "{}_{}_{}_{}".format(busi, busj, busk, ckt)
                content.append("def TRAFO_{}():".format(name.replace("-", "_").replace("#", "_")))
                content.append('    "F/S {}"'.format(name))
                content.append("    psspy.three_wnd_imped_chng_4({},{},{},'{}', intgar8=0)".format(busi, busj, busk, ckt))
                content.append("")
                
            if ms[0] in ["LII"]:
                busi, busj, ckt = int(ms[1]), int(ms[2]), ms[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)
                name = name.strip() or "{}-{}#{}".format(busi, busj, ckt)
                content.append("def BRANCH_{}():".format(name.replace("-", "_").replace("#", "_")))
                content.append('    "F/S {}"'.format(name))
                content.append("    psspy.branch_chng_3({},{},'{}', intgar1=0)".format(busi, busj, ckt))
                content.append("")

            if ms[0] in ["TR"]:
                busi, busj, ckt = int(ms[1]), int(ms[2]), ms[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)
                name = name.strip() or "{}-{}#{}".format(busi, busj, ckt)
                content.append("def BRANCH_{}():".format(name.replace("-", "_").replace("#", "_")))
                content.append('    "F/S {}"'.format(name))
                content.append("    psspy.two_winding_chng_6({},{},'{}', intgar1=0)".format(busi, busj, ckt))
                content.append("")

            if ms[0] == "SYS":
                busi, busj, ckt = int(ms[1]), int(ms[2]), ms[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)
                name = name.strip() or "{}-{}#{}".format(busi, busj, ckt)
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
