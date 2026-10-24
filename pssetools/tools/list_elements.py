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
        self.root.resizable(False, True)

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
        text = tk.Text(text_frame, wrap="none", yscrollcommand=scrollbar.set)
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



    def create_mon(self, text_widget):
        """
        Cuatro campos + un campo de texto para reportes
        """
        import psspy
        content = []
        for ms in self.get_map_string_in_sld():
            if ms[0] in ["BU", "ME", "SWS", "LO", "FXS"]:
                ms = ms + [""] * (6 - len(ms))                
                ierr, name = psspy.notona(int(ms[1]))
                if ierr != 0:
                    continue
                if name:
                    ms[-1] = name[:12].strip()
                content.append("\t".join(ms))

            elif ms[0] in ["TR", "SYS", "LII"]:
                ms = ms + [""] * (6 - len(ms))
                busi, busj, ckt = int(ms[1]), int(ms[2]), ms[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)                
                if ierr != 0:
                    continue
                name = name.strip() or "{}-{}#{}".format(busi, busj, ckt)
                ms[-1] = name
                content.append("\t".join(ms))

            elif ms[0] == "T3":
                ms = ms + [""] * (6 - len(ms))
                busi, busj, busk, ckt = int(ms[1]), int(ms[2]), int(ms[3]), ms[4]
                ierr, name = psspy.tr3nam(busi, busj, busk, ckt)
                if ierr != 0:
                    continue
                name = name.strip() or "{}-{}-{}#{}".format(busi, busj, busk, ckt)
                ms[-1] = name
                content.append("\t".join(ms))

        if content:
            content.sort()
            txt = text_widget.get("1.0", tk.END)
            all_content = [line for line in txt.splitlines() if line.strip()]
            all_content.extend(content)
            all_content.sort()
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
