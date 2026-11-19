# coding: latin-1
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys

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

class BaseWizardDialog(object):
    """
    Clase base para dialogos con pestañas tipo 'Wizard' / generadores de archivos.
    Provee navegacion por tabs, manejo de menues (File), atajos de teclado y dialogos
    de guardar/cargar texto de forma compatible con Python 2 y 3.
    """
    def __init__(self, parent, title="Wizard", geometry="650x350", resizable=(True, True)):
        if not sys.argv:
            sys.argv = ["gui"]

        self.root = tk.Toplevel(parent)
        self.root.title(title)
        self.root.geometry(geometry)
        self.root.resizable(*resizable)
        self.root.attributes("-topmost", True)

        self.tab_config = {}
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self._build_menu()
        self._bind_keys()

    def _build_menu(self):
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

    def _bind_keys(self):
        self.root.bind("<Control-Tab>", self.next_tab)
        self.root.bind("<Control-Shift-Tab>", self.prev_tab)
        self.root.bind("<Control-w>", self.exit)
        self.root.bind("<Control-Key-1>", self.handle_action_1)
        self.root.bind("<Alt-Key-1>", self.handle_action_1)

        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-o>", lambda e: self.load_file())
        self.root.bind("<Control-S>", lambda e: self.save_all())
        self.root.bind("<Control-O>", lambda e: self.load_all())
        self.root.bind("<Control-a>", self.select_all)
        self.root.bind("<Control-A>", self.select_all)

    def create_text_tab(self, index, name, ext, attr_name, label_btn=None, btn_command=None):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=name)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        text_frame = ttk.Frame(frame)
        text_frame.grid(row=0, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        text_widget = tk.Text(text_frame, wrap="none", yscrollcommand=scrollbar.set, font=("Courier New", 10))
        text_widget.pack(fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)

        setattr(self, attr_name, text_widget)
        self.tab_config[index] = {
            "ext": ext,
            "attr": attr_name,
            "label": name,
            "action": btn_command
        }

        if label_btn and btn_command:
            ttk.Button(frame, text=label_btn, command=lambda: btn_command(text_widget)).grid(
                row=0, column=1, sticky="n", pady=5, padx=5
            )

        return frame, text_widget

    def next_tab(self, event=None):
        total = self.notebook.index("end")
        if total > 0:
            current = self.notebook.index(self.notebook.select())
            self.notebook.select((current + 1) % total)
        return "break"

    def prev_tab(self, event=None):
        total = self.notebook.index("end")
        if total > 0:
            current = self.notebook.index(self.notebook.select())
            self.notebook.select((current - 1) % total)
        return "break"

    def handle_action_1(self, event=None):
        idx = self.notebook.index(self.notebook.select())
        conf = self.tab_config.get(idx)
        if conf and conf.get("action"):
            text_widget = getattr(self, conf["attr"])
            conf["action"](text_widget)
        return "break"

    def select_all(self, event=None):
        widget = self.root.focus_get()
        if isinstance(widget, tk.Text):
            widget.tag_add("sel", "1.0", "end-1c")
            widget.mark_set("insert", "1.0")
            widget.see("insert")
            return "break"

    def exit(self, event=None):
        self.root.destroy()
        return "break"

    def save_file(self):
        idx = self.notebook.index(self.notebook.select())
        conf = self.tab_config.get(idx)
        if not conf:
            return
        text_widget = getattr(self, conf["attr"])
        filename = tkFileDialog.asksaveasfilename(
            defaultextension=conf["ext"],
            filetypes=[(conf["label"], "*{}".format(conf["ext"])), ("All Files", "*.*")]
        )
        if filename:
            content = text_widget.get("1.0", tk.END)
            # En Python 2/3 compatibilidad segura de encode
            if sys.version_info[0] == 2 and isinstance(content, unicode):
                content = content.encode("utf-8")
            elif sys.version_info[0] >= 3:
                content = content.encode("utf-8")
            with open(filename, "wb") as f:
                f.write(content)

    def load_file(self):
        idx = self.notebook.index(self.notebook.select())
        conf = self.tab_config.get(idx)
        if not conf:
            return
        text_widget = getattr(self, conf["attr"])
        filename = tkFileDialog.askopenfilename(
            filetypes=[(conf["label"], "*{}".format(conf["ext"])), ("All Files", "*.*")]
        )
        if filename:
            with open(filename, "rb") as f:
                raw = f.read()
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", raw.decode("utf-8", errors="replace"))

    def save_all(self):
        base_path = tkFileDialog.asksaveasfilename(title="Select Base Filename for All Configs")
        if not base_path:
            return
        base_name = os.path.splitext(base_path)[0]
        for conf in self.tab_config.values():
            text_widget = getattr(self, conf["attr"])
            full_path = "{}{}".format(base_name, conf["ext"])
            content = text_widget.get("1.0", tk.END)
            if sys.version_info[0] == 2 and isinstance(content, unicode):
                content = content.encode("utf-8")
            elif sys.version_info[0] >= 3:
                content = content.encode("utf-8")
            with open(full_path, "wb") as f:
                f.write(content)
        tkMessageBox.showinfo("Success", "All files saved with base name: " + base_name)

    def load_all(self):
        base_path = tkFileDialog.askopenfilename(title="Select any file from the set to load all")
        if not base_path:
            return
        base_name = os.path.splitext(base_path)[0]
        for conf in self.tab_config.values():
            full_path = "{}{}".format(base_name, conf["ext"])
            if os.path.exists(full_path):
                text_widget = getattr(self, conf["attr"])
                with open(full_path, "rb") as f:
                    raw = f.read()
                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", raw.decode("utf-8", errors="replace"))
