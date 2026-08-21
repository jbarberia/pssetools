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


class ConfigWizardApp(object):
    """
    Asistente para generar archivos de configuración PSS/E interactuando 
    con el diagrama SLD activo.
    """
    def __init__(self, parent):
        if not sys.argv:
            sys.argv = ["gui"]

        # Convertimos tk.Tk() a tk.Toplevel(parent) para que sea una ventana secundaria
        self.root = tk.Toplevel(parent)
        self.root.title("Config File Wizard")
        self.root.attributes("-topmost", True)
        self.root.geometry("650x350")
        self.root.resizable(False, True)

        self.tab_config = {
            0: {"ext": ".sub", "attr": "sub_text", "label": "Subsystem"},
            1: {"ext": ".mon", "attr": "mon_text", "label": "Monitor"},
            2: {"ext": ".con", "attr": "con_text", "label": "Contingency"},
            3: {"ext": ".idv", "attr": "chan_text", "label": "Channel"},
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

        self.create_sub_tab("SUB")
        self.create_mon_tab("MON")
        self.create_con_tab("CON")
        self.create_chan_tab("CHAN")

        self.root.bind("<Control-Tab>", self.next_tab)
        self.root.bind("<Control-Shift-Tab>", self.prev_tab)
        self.root.bind("<Control-w>", self.exit)
        self.root.bind("<Control-Key-1>", self.handle_ctrl_1)
        self.root.bind("<Alt-Key-1>", self.handle_ctrl_1)
        
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
        if current == 0: self.create_sub(self.sub_text)
        elif current == 1: self.create_mon(self.mon_text)
        elif current == 2: self.create_con(self.con_text)
        elif current == 3: self.create_chan(self.chan_text)
        return "break"

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
        text = tk.Text(text_frame, wrap="none", yscrollcommand=scrollbar.set)
        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)
        return text

    def create_sub_tab(self, name):
        frame = self._create_frame(name)
        text = self._create_text(frame)
        self.sub_text = text
        ttk.Button(frame, text="1 - Generar Subsystem", command=lambda: self.create_sub(text)).grid(row=0, column=1, sticky="n", pady=5, padx=5)

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

    def create_chan_tab(self, name):
        frame = self._create_frame(name)
        text = self._create_text(frame)
        self.chan_text = text
        ttk.Button(frame, text="1 - Generar Channel", command=lambda: self.create_chan(text)).grid(row=0, column=1, sticky="n", pady=5, padx=5)

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


    def create_sub(self, text_widget):
        content = []
        for ms in self.get_map_string_in_sld():
            if ms[0] in ["BU", "ME", "SWS", "LO", "FXS"]:
                content.append("BUS {}".format(int(ms[1])))
            elif ms[0] in ["TR", "SYS", "LII"]:
                content.append("BUS {}".format(int(ms[1])))
                content.append("BUS {}".format(int(ms[2])))
            elif ms[0] == "T3":
                content.append("BUS {}".format(int(ms[1])))
                content.append("BUS {}".format(int(ms[2])))
                content.append("BUS {}".format(int(ms[3])))

        if content:
            self.sub_number += 1
            content.insert(0, "SUBSYSTEM 'SYSTEM_{}'".format(str(self.sub_number).zfill(2)))
            content.append("END\n")

            txt = text_widget.get("1.0", tk.END)
            text_widget.delete("1.0", tk.END)
            txt = "END".join(txt.split("END")[:-1])
            text_widget.insert(tk.INSERT, txt + "\n".join(content) + "\nEND\n")

    def create_mon(self, text_widget):
        content = []
        for ms in self.get_map_string_in_sld():
            if ms[0] in ["BU", "ME", "SWS", "LO", "FXS"]:
                content.append("MONITOR VOLTAGE LIMIT BUS {}".format(int(ms[1])))
            elif ms[0] in ["TR", "SYS", "LII"]:
                content.append("MONITOR BRANCH FROM BUS {} TO BUS {} CKT {}".format(int(ms[1]), int(ms[2]), ms[3]))
            elif ms[0] == "T3":
                content.append("MONITOR BRANCH FROM BUS {} TO BUS {} TO BUS {} CKT {}".format(int(ms[1]), int(ms[2]), int(ms[3]), ms[4]))

        if content:
            txt = text_widget.get("1.0", tk.END)
            text_widget.delete("1.0", tk.END)
            txt = "END".join(txt.split("END")[:-1])
            text_widget.insert(tk.INSERT, txt + "\n".join(content) + "\nEND\n")

    def create_con(self, text_widget):
        import psspy
        content = []
        for ms in self.get_map_string_in_sld():
            if ms[0] == "ME":
                busi = int(ms[1])
                content.append("CONTINGENCY GEN-{}".format(busi))
                content.append("DISCONNECT BUS {}".format(busi))
                content.append("END\n")
            elif ms[0] == "T3":
                busi, busj, busk, ckt = int(ms[1]), int(ms[2]), int(ms[3]), ms[4]
                ierr, name = psspy.tr3nam(busi, busj, busk, ckt)
                name = name.strip() or "{}-{}-{}#{}".format(busi, busj, busk, ckt)
                content.append("CONTINGENCY {}".format(name))
                content.append("OPEN BRANCH FROM BUS {} TO BUS {} TO BUS {} CIRCUIT {}".format(busi, busj, busk, ckt))
                content.append("END\n")
            elif ms[0] in ["TR", "SYS", "LII"]:
                busi, busj, ckt = int(ms[1]), int(ms[2]), ms[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)
                name = name.strip() or "{}-{}#{}".format(busi, busj, ckt)
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
        for ms in self.get_map_string_in_sld():
            if ms[0] == "BU":
                busi = int(ms[1])
                ierr, name = psspy.notona(busi)
                name = name.strip()
                canales.append("BAT_BUS_FREQUENCY_CHANNEL -1 {} 'FREC {} - {}'".format(busi, busi, name))
                canales.append("BAT_VOLTAGE_CHANNEL -1 -1 -1 {} 'U {} - {}'".format(busi, busi, name))

            elif ms[0] == "ME":
                busi, identifier = int(ms[1]), ms[2]
                ierr, name = psspy.notona(busi)
                name = name[:12].strip() + " - " + identifier
                canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 1 {} '{}' '{} - ANGLE'".format(busi, identifier, name))
                canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 2 {} '{}' '{} - PELEC'".format(busi, identifier, name))
                canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 3 {} '{}' '{} - QELEC'".format(busi, identifier, name))
                canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 4 {} '{}' '{} - ETERM'".format(busi, identifier, name))
                canales.append("BAT_MACHINE_ARRAY_CHANNEL -1 7 {} '{}' '{} - SPEED'".format(busi, identifier, name))
            
            elif ms[0] == "T3":
                busi, busj, busk, ckt = int(ms[1]), int(ms[2]), int(ms[3]), ms[4]
                ierr, trname = psspy.tr3nam(busi, busj, busk, ckt)
                canales.append("BAT_THREE_WND_MVA_CHANNEL -1 -1 -1 {} {} {} '{}' '{} - MVA'".format(busi, busj, busk, ckt, trname.strip()))

            elif ms[0] in ["TR", "SYS", "LII"]:
                busi, busj, ckt = int(ms[1]), int(ms[2]), ms[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)
                name = name.strip() or "{}-{} CKT {}".format(busi, busj, ckt)
                canales.append("BAT_BRANCH_MVA_CHANNEL -1 -1 -1 {} {} '{}' '{} - MVA'".format(busi, busj, ckt, name))

        if canales:
            text_widget.insert(tk.INSERT, "\n".join(canales) + "\n")
