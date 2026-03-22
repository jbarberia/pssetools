# -*- coding: utf-8 -*-
import Tkinter as tk
import ttk
import psse34
import psspy
import sliderPy
import sys
import re
import tkFileDialog
import tkMessageBox


class gui(object):
    """Main application class for the pssetools GUI.

    Provides a multi-tab interface to generate and manage PSS/E configuration
    files (subsystems, monitors, contingencies, and channels) by interacting
    with active PSS/E SLD diagrams.
    """

    def __init__(self):
        """Initializes the GUI window, tabs, and event bindings."""
        sys.argv = ["gui"]

        root = tk.Tk()
        root.title("Config File Wizard")
        root.attributes("-topmost", True)
        root.geometry("650x350")
        root.resizable(False, True)
        self.root = root

        # Tab configuration: (Index, Name, Extension, Text Widget Attribute)
        self.tab_config = {
            0: {"ext": ".sub", "attr": "sub_text", "label": "Subsystem"},
            1: {"ext": ".mon", "attr": "mon_text", "label": "Monitor"},
            2: {"ext": ".con", "attr": "con_text", "label": "Contingency"},
            3: {"ext": ".idv", "attr": "chan_text", "label": "Channel"},
        }

        # Counter of subsistems
        self.sub_number = 0

        # Main notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # Create menu bar
        menubar = tk.Menu(root)
        self.menubar = menubar
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save", command=self.save_file, accelerator="ctrl-s")
        file_menu.add_command(label="Load", command=self.load_file, accelerator="ctrl-o")
        file_menu.add_separator()
        file_menu.add_command(label="Save All", command=self.save_all, accelerator="ctrl-shift-s>")
        file_menu.add_command(label="Load All", command=self.load_all, accelerator="ctrl-shift-o>")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit)
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)

        # Create tabs
        self.create_sub_tab("SUB"),
        self.create_mon_tab("MON"),
        self.create_con_tab("CON"),
        self.create_chan_tab("CHAN"),

        # Bindings
        self.root.bind_all("<Control-Tab>", self.next_tab)
        self.root.bind_all("<Control-Shift-Tab>", self.prev_tab)
        self.root.bind_all("<Control-w>", self.exit)
        self.root.bind_all("<Control-Key-1>", self.handle_ctrl_1)
        self.root.bind_all("<Alt-Key-1>", self.handle_ctrl_1)
        self.root.bind_all("<Alt-|>", self.handle_ctrl_1)

        self.root.bind_all("<Control-s>", lambda e: self.save_file())
        self.root.bind_all("<Control-o>", lambda e: self.load_file())
        self.root.bind_all("<Control-S>", lambda e: self.save_all())
        self.root.bind_all("<Control-O>", lambda e: self.load_all())

    def next_tab(self, event=None):
        """Avanza a la siguiente pestaña de forma circular."""
        current = self.notebook.index(self.notebook.select())
        total = self.notebook.index("end")
        next_index = (current + 1) % total
        self.notebook.select(next_index)
        return "break"  # Evita que el evento se propague a otros widgets

    def prev_tab(self, event=None):
        """Retrocede a la pestaña anterior de forma circular."""
        current = self.notebook.index(self.notebook.select())
        total = self.notebook.index("end")
        prev_index = (current - 1) % total
        self.notebook.select(prev_index)
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
        """Asks for a base filename and saves all tabs with respective extensions."""
        base_path = tkFileDialog.asksaveasfilename(title="Select Base Filename for All Configs", filetypes=[("Base Name", "*.*")])

        if base_path:
            # Strip existing extension if user provided one
            base_name = os.path.splitext(base_path)[0]
            for idx, conf in self.tab_config.items():
                text_widget = getattr(self, conf["attr"])
                full_path = "{}{}".format(base_name, conf["ext"])
                with open(full_path, 'w') as f:
                    f.write(text_widget.get("1.0", tk.END).encode('utf-8'))
            tkMessageBox.showinfo("Success", "All files saved with base name: " + base_name)

    def load_all(self):
        """Attempts to load all files sharing a common base name selected by user."""
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
        """Checks the active tab and runs the corresponding action."""
        # 0: SUB, 1: MON, 2: CON, 3: CHAN
        current_tab_index = self.notebook.index(self.notebook.select())
        if current_tab_index == 0:
            self.create_sub(self.sub_text)
        elif current_tab_index == 1:
            self.create_mon(self.mon_text)
        elif current_tab_index == 2:
            self.create_con(self.con_text)
        elif current_tab_index == 3:
            self.create_chan(self.chan_text)
        return "break"

    # TAB CREATION -------------------------------------------------------------

    def _create_frame(self, name):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=name)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
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
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=1, sticky="ns")
        ttk.Button(button_frame, text="1 - subsystem", command=lambda: self.create_sub(text)).pack(pady=5, padx=5)
        return frame

    def create_mon_tab(self, name):
        frame = self._create_frame(name)
        text = self._create_text(frame)
        self.mon_text = text
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=1, sticky="ns")
        ttk.Button(button_frame, text="1 - monitor", command=lambda: self.create_mon(text)).pack(pady=5, padx=5)
        return frame

    def create_con_tab(self, name):
        frame = self._create_frame(name)
        text = self._create_text(frame)
        self.con_text = text
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=1, sticky="ns")
        ttk.Button(button_frame, text="1 - contingency", command=lambda: self.create_con(text)).pack(pady=5, padx=5)
        return frame

    def create_chan_tab(self, name):
        frame = self._create_frame(name)
        text = self._create_text(frame)
        self.chan_text = text
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=1, sticky="ns")
        ttk.Button(button_frame, text="1 - channel", command=lambda: self.create_chan(text)).pack(pady=5, padx=5)
        return frame

    # --- SUB ACTIONS ---
    def get_map_string_in_sld(self):
        mydoc = sliderPy.GetActiveDocument()
        diagram = mydoc.GetDiagram()
        components = diagram.GetComponents()
        for component in components:
            if component.IsSelected() == False:
                continue
            map_string = re.findall(r"\S+", component.GetMapString())
            if len(map_string) == 0:
                continue
            yield map_string

    def create_sub(self, text_widget):
        print("crate sub")
        content = []
        for map_string in self.get_map_string_in_sld():
            if map_string[0] in ["BU", "ME", "SWS", "LO", "FXS"]:
                busi = int(map_string[1])
                content.append("BUS {}".format(busi))
            elif map_string[0] in ["TR", "SYS", "LII"]:
                busi = int(map_string[1])
                busj = int(map_string[2])
                content.append("BUS {}".format(busi))
                content.append("BUS {}".format(busj))
            elif map_string[0] in ["T3"]:
                busi = int(map_string[1])
                busj = int(map_string[2])
                busk = int(map_string[3])
                content.append("BUS {}".format(busi))
                content.append("BUS {}".format(busj))
                content.append("BUS {}".format(busk))

        if content:
            self.sub_number += 1
            content.insert(0, "SUBSYSTEM 'SYSTEM_{}'".format(str(self.sub_number)).zfill(2))
            content.append("END\n")

            txt = text_widget.get("1.0", tk.END)
            text_widget.delete("1.0", tk.END)
            txt = "END".join(txt.split("END")[:-1])
            text_widget.insert(tk.INSERT, txt + "\n".join(content) + "\nEND\n")

    def create_mon(self, text_widget):
        print("crate mon")
        content = []
        for map_string in self.get_map_string_in_sld():

            if map_string[0] in ["BU", "ME", "SWS", "LO", "FXS"]:
                busi = int(map_string[1])
                content.append("MONITOR VOLTAGE LIMIT BUS {}".format(busi))

            if map_string[0] in ["TR", "SYS", "LII"]:
                busi = int(map_string[1])
                busj = int(map_string[2])
                ckt = map_string[3]
                content.append("MONITOR BRANCH FROM BUS {} TO BUS {} CKT {}".format(busi, busj, ckt))

            if map_string[0] == "T3":
                busi = int(map_string[1])
                busj = int(map_string[2])
                busk = int(map_string[3])
                ckt = map_string[4]
                content.append("MONITOR BRANCH FROM BUS {} TO BUS {} TO BUS {} CKT {}".format(busi, busj, busk, ckt))

        if content:
            txt = text_widget.get("1.0", tk.END)
            text_widget.delete("1.0", tk.END)
            txt = "END".join(txt.split("END")[:-1])
            text_widget.insert(tk.INSERT, txt + "\n".join(content) + "\nEND\n")

    def create_con(self, text_widget):
        print("crate con")
        content = []
        for map_string in self.get_map_string_in_sld():
            if map_string[0] in ["ME"]:
                busi = int(map_string[1])
                content.append("CONTINGENCY GEN-{}".format(busi))
                content.append("DISCONNECT BUS {}".format(busi))
                content.append("END\n")

            if map_string[0] in ["T3"]:
                busi = int(map_string[1])
                busj = int(map_string[2])
                busk = int(map_string[3])
                ckt = map_string[4]
                ierr, name = psspy.tr3nam(busi, busj, busk, ckt)
                name = name.strip()
                if not name:
                    name = "{}-{}-{}#{}".format(busi, busj, busk, ckt)
                content.append("CONTINGENCY {}-{}-{}-{}".format(busi, busj, busk, ckt))
                content.append("OPEN BRANCH FROM BUS {} TO BUS {} TO BUS {} CIRCUIT {}".format(busi, busj, busk, ckt))
                content.append("END\n")

            if map_string[0] in ["TR", "SYS", "LII"]:
                busi = int(map_string[1])
                busj = int(map_string[2])
                ckt = map_string[3]
                ierr, name = psspy.brnnam(busi, busj, ckt)
                name = name.strip()
                if not name:
                    name = "{}-{}#{}".format(busi, busj, ckt)
                content.append("CONTINGENCY {}".format(name))
                content.append("OPEN BRANCH FROM BUS {} TO BUS {} CKT {}".format(busi, busj, ckt))
                content.append("END\n")

        if content:
            txt = text_widget.get("1.0", tk.END)
            text_widget.delete("1.0", tk.END)
            txt = "END".join(txt.split("END")[:-1])
            text_widget.insert(tk.INSERT, txt + "\n".join(content) + "\nEND\n")

    def create_chan(self, text_widget):
        canales = []
        for map_string in self.get_map_string_in_sld():
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
        if content:
            text_widget.insert(tk.INSERT, content + "\n")

    def run_action(self, text_widget):
        content = text_widget.get("1.0", tk.END)
        print("Run pressed. Content length:", len(content))

    def clear_text(self, text_widget):
        text_widget.delete("1.0", tk.END)

    def print_text(self, text_widget):
        print(text_widget.get("1.0", tk.END))


if __name__ == "__main__":
    app = gui()
    app.root.mainloop()
