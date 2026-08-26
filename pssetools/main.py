# coding: latin-1
"""
PSS/E Automation Suite
-----------------------
Interfaz gráfica (Tkinter) para descubrir, configurar y ejecutar programas
ubicados en el paquete `programs`. Compatible con Python 2 y 3.
"""

try:
    import tkinter as tk
    from tkinter import filedialog as tkFileDialog
    from tkinter import messagebox as TkMessageBox
except ImportError:
    import Tkinter as tk
    import tkFileDialog
    import tkMessageBox as TkMessageBox  # Fix: Alias coherente para Py2

import os
import re
import sys

from pssegui.programs import discover_programs
from state import ApplicationState


class PSSEAutomationApp(object):

    # ------------------------------------------------------------------
    # INICIALIZACIÓN / CONSTRUCCIÓN DE LA VENTANA PRINCIPAL
    # ------------------------------------------------------------------
    def __init__(self, root):    
        self.state = ApplicationState()
        self.param_entries = {}
        self.current_program_name = None

        # --- Interfaz gráfica ---
        self.root = root
        self.root.title("PSSE Automation")
        self.root.geometry("950x640")

        self._build_menu_bar()
        self._bind_hotkeys()
        self._build_main_layout()

        # --- Descubrimiento dinámico de programas ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        test_dir = os.path.abspath(os.path.join(base_dir, "..", "test"))
        
        self.programs_data, self.program_instances, errors = discover_programs(test_dir)
        self._initialize_program_state()
        self._populate_program_list()

        if errors:
            TkMessageBox.showwarning("Errores en Programas", "\n".join(errors))

        # Iniciar el monitoreo continuo del CWD en el main loop
        self._monitor_cwd()


    def _monitor_cwd(self):
        """
        Consulta el directorio de trabajo (CWD) actual de PSS/E cada 1000ms.
        Así la interfaz siempre muestra dónde está parada la consola realmente.
        """
        try:
            current_cwd = os.getcwd()
            self.cwd_var.set(current_cwd)            
        except Exception:
            pass
        # Reprogramar esta función para ejecutarse en 1 segundo (1000 ms)
        self.root.after(1000, self._monitor_cwd)


    def _initialize_program_state(self):
        for prog_name, info in self.programs_data.items():
            self.state.programs.setdefault(
                prog_name,
                {p["name"]: p.get("default") for p in info.get("parameters", [])}
            )


    def _populate_program_list(self):
        for prog_name in sorted(self.programs_data):
            self.program_listbox.insert(tk.END, prog_name)

        if self.program_listbox.size() > 0:
            self.program_listbox.selection_set(0)
            self.on_program_select(None)





    def get_selected_program_name(self):
        selection = self.program_listbox.curselection()
        if not selection:
            return None
        return self.program_listbox.get(selection[0])


    def get_program_definition(self, program_name):
        return self.programs_data.get(program_name, {})

    def get_program_state(self, program_name):
        return self.state.programs.setdefault(program_name, {})


    # ------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA INTERFAZ GRÁFICA (UI)
    # ------------------------------------------------------------------
    def _build_menu_bar(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Configuration", command=self.save_configurations, accelerator="Ctrl+S")
        file_menu.add_command(label="Load Configuration", command=self.load_configuration, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Config File Wizard...", command=self.open_config_wizard)        
        menubar.add_cascade(label="Tools", menu=tools_menu)

        paths_menu = tk.Menu(menubar, tearoff=0)
        paths_menu.add_command(label="Configure Paths...", command=self.configure_workspace_paths)
        paths_menu.add_separator()
        paths_menu.add_command(label="Open Output Folder", command=lambda: self._open_directory(self.state.workspace.output_dir))
        paths_menu.add_command(label="Open Temp Folder", command=lambda: self._open_directory(self.state.workspace.temp_dir))
        menubar.add_cascade(label="Paths", menu=paths_menu)
        
        self.root.config(menu=menubar)


    def _bind_hotkeys(self):        
        self.root.bind("<Control-s>", lambda event: self.save_configurations())
        self.root.bind("<Control-o>", lambda event: self.load_configuration())
        self.root.bind("<Control-Return>", lambda event: self.on_run_clicked())        
        self.root.bind("<Control-Up>", self.on_ctrl_arrow_key)
        self.root.bind("<Control-Down>", self.on_ctrl_arrow_key)


    def _build_main_layout(self):
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0) # Fila para la barra inferior
        self.root.columnconfigure(0, weight=1)
        
        # --- ZONA SUPERIOR: Aplicación Principal ---
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        
        # Panel Izquierdo: lista de programas
        left_frame = tk.LabelFrame(main_frame, text=" Available Programs (src/programs) ")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        
        self.program_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE, font=("Courier", 10), exportselection=False)
        self.program_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.program_listbox.bind('<<ListboxSelect>>', self.on_program_select)
        
        self.program_listbox.bind("<Up>", self.on_listbox_arrow_key)
        self.program_listbox.bind("<Down>", self.on_listbox_arrow_key)
        
        # Panel Derecho: documentación + parámetros + botón Run
        right_outer_frame = tk.Frame(main_frame)
        right_outer_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_outer_frame.rowconfigure(0, weight=1)
        right_outer_frame.rowconfigure(1, weight=1)
        right_outer_frame.rowconfigure(2, weight=0)
        right_outer_frame.columnconfigure(0, weight=1)

        self._build_documentation_panel(right_outer_frame)

        self.param_frame = tk.LabelFrame(right_outer_frame, text=" Parameters ")
        self.param_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 5))
               
        self.run_btn = tk.Button(right_outer_frame, text="Run Selected Program (Ctrl+Enter)", command=self.on_run_clicked, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.run_btn.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        # --- ZONA INFERIOR: Barra de CWD ---
        status_frame = tk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1) # El mensaje ocupa el espacio sobrante

        self.cwd_var = tk.StringVar()
        self.cwd_var.set(" CWD: Cargando... ")
        self.cwd_label = tk.Label(status_frame, textvariable=self.cwd_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 9), fg="black")
        self.cwd_label.grid(row=0, column=0, sticky="ew", ipady=2)


    def _build_documentation_panel(self, parent):
        # 1. Documentation Section
        doc_frame = tk.LabelFrame(parent, text=" Documentation ")
        doc_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        doc_frame.rowconfigure(0, weight=1)
        doc_frame.columnconfigure(0, weight=1)
        
        doc_container = tk.Frame(doc_frame)
        doc_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        doc_container.rowconfigure(0, weight=1)
        doc_container.columnconfigure(0, weight=1)
        

        self.doc_text = tk.Text(doc_container, wrap=tk.WORD, font=("Courier", 9), height=8)
        self.doc_text.grid(row=0, column=0, sticky="nsew")
        def _block_editing(event):        
            if event.state & 4 and event.keysym.lower() in ('c', 'a'):
                return
            return "break"
        self.doc_text.bind("<Key>", _block_editing)

        doc_scrollbar = tk.Scrollbar(doc_container, orient="vertical", command=self.doc_text.yview)
        doc_scrollbar.grid(row=0, column=1, sticky="ns")
        self.doc_text.config(yscrollcommand=doc_scrollbar.set)
        self._bind_mouse_scroll(self.doc_text)

        


    # ------------------------------------------------------------------
    # ESTADO DEL FORMULARIO / CONFIGURACIÓN (guardar / cargar)
    # ------------------------------------------------------------------    
    def cache_current_form_state(self):        
        if getattr(self, 'current_program_name', None) and self.param_entries:
            current_state = {}
            for name, widget in self.param_entries.items():
                if isinstance(widget, tk.Listbox):
                    vals = widget.get(0, tk.END)
                    current_state[name] = ";".join(vals)
                elif isinstance(widget, tk.IntVar):
                    current_state[name] = bool(widget.get())
                else:
                    current_state[name] = widget.get()
            self.state.programs[self.current_program_name] = current_state


    def save_configurations(self):
        self.cache_current_form_state()
        filename = tkFileDialog.asksaveasfilename(
            title="Save All Program Configurations",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")]
        )
        if not filename:
            return
        self.state.save(filename)


    def load_configuration(self):
        filename = tkFileDialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON Config Files", "*.json"), ("All Files", "*.*")],
        )
        if not filename:
            return

        if not self.state.load(filename):
            TkMessageBox.showerror("Error", "Unable to load configuration.")
            return

        self._initialize_program_state()
        self.state.workspace.ensure_workspace_exists()
        self.refresh_current_program()



    def refresh_current_program(self):
        program_name = self.get_selected_program_name()
        if not program_name:              
            return

        prog_info = self.get_program_definition(program_name)
        saved_params = self.get_program_state(program_name)

        # Resetea el título del panel al estándar
        self.param_frame.config(text=" Parameters ")

        # Documentación
        self.doc_text.config(state=tk.NORMAL)
        self.doc_text.delete("1.0", tk.END)
        self.doc_text.insert(tk.END, prog_info.get("doc", "No documentation available."))
        self.doc_text.config(state=tk.DISABLED)

        # Formulario
        self._build_parameter_form(prog_info.get("parameters", []), saved_params)


    # ------------------------------------------------------------------
    # CONSTRUCCIÓN DINÁMICA DEL FORMULARIO DE PARÁMETROS
    # ------------------------------------------------------------------
    def _build_parameter_form(self, parameters, saved_params):       
        for widget in self.param_frame.winfo_children():
            widget.destroy()
            
        self.param_entries = {}
        for i, param in enumerate(parameters):
            self.param_frame.rowconfigure(i, weight=0)
            self.param_frame.columnconfigure(1, weight=1)
            
            lbl = tk.Label(self.param_frame, text=param["label"], font=("Arial", 9))
            lbl.grid(row=i, column=0, sticky="nw", padx=5, pady=3)

            default_val = saved_params.get(param["name"], param.get("default"))

            if param["type"] == "multi_file":
                self._build_multi_file_row(i, param, default_val)
            elif param["type"] == "bool":
                self._build_bool_row(i, param, default_val)
            else:
                self._build_entry_row(i, param, default_val)


    def _build_multi_file_row(self, row, param, default_val):
        list_frame = tk.Frame(self.param_frame)
        list_frame.grid(row=row, column=1, sticky="nsew", padx=5, pady=3)

        lb = tk.Listbox(list_frame, font=("Courier", 9), height=4, selectmode=tk.EXTENDED)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = tk.Scrollbar(list_frame, command=lb.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        lb.config(yscrollcommand=scroll.set)

        if default_val:
            if isinstance(default_val, list):
                paths = default_val 
            else:
                paths = self.parse_paths(self.safe_text(default_val))
            
            for p in paths: 
                lb.insert(tk.END, p)

        self.param_entries[param["name"]] = lb
        self._bind_listbox_context_menu(lb)

        btn_frame = tk.Frame(self.param_frame)
        btn_frame.grid(row=row, column=2, columnspan=2, sticky="nw", pady=3)

        add_btn = tk.Button(btn_frame, text="Add", width=8, command=lambda l=lb: self._add_multi_files(l))
        add_btn.pack(side=tk.TOP, pady=(0, 2))

        rem_btn = tk.Button(btn_frame, text="Remove", width=8, command=lambda l=lb: self._remove_multi_files(l))
        rem_btn.pack(side=tk.TOP, pady=(0, 2))

        rem_all_btn = tk.Button(btn_frame, text="Remove All", width=8, command=lambda l=lb: l.delete(0, tk.END))
        rem_all_btn.pack(side=tk.TOP)


    def _build_bool_row(self, row, param, default_val):
        var = tk.IntVar()
        var.set(1 if default_val else 0)
        
        chk = tk.Checkbutton(self.param_frame, variable=var)
        chk.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        self.param_entries[param["name"]] = var

        
    def _build_entry_row(self, row, param, default_val):            
        entry = tk.Entry(self.param_frame, font=("Courier", 9))
        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=3)

        entry.delete(0, tk.END)
        if default_val is not None:
            entry.insert(0, self.safe_text(default_val))
        else:
            entry.insert(0, "")

        self.param_entries[param["name"]] = entry

        if param["type"] in ["file", "save"]:
            browse_btn = tk.Button(self.param_frame, text="...", width=3,
                                    command=lambda e=entry, t=param["type"]: self._browse_file(e, t))
            browse_btn.grid(row=row, column=2, padx=2, pady=3)

        if param.get("editable", True):
            edit_btn = tk.Button(self.param_frame, text="Edit", width=5,
                                  command=lambda e=entry: self._edit_file(e))
            edit_btn.grid(row=row, column=3, padx=(2, 5), pady=3)


    # ------------------------------------------------------------------
    # EVENTOS Y NAVEGACION
    # ------------------------------------------------------------------
    def on_program_select(self, event):
        self.cache_current_form_state()
        program_name = self.get_selected_program_name()
        if program_name:
            self.current_program_name = program_name
            self.refresh_current_program()

    def on_ctrl_arrow_key(self, event):
        self._navigate_listbox(event.keysym)


    def on_listbox_arrow_key(self, event):
        self._navigate_listbox(event.keysym)
        return "break"

    
    def _navigate_listbox(self, direction):
        selection = self.program_listbox.curselection()
        current_index = selection[0] if selection else 0
        max_index = self.program_listbox.size() - 1
        
        new_index = max(0, current_index - 1) if direction == "Up" else min(max_index, current_index + 1)
        
        self.program_listbox.selection_clear(0, tk.END)
        self.program_listbox.selection_set(new_index)
        self.program_listbox.see(new_index)
        self.on_program_select(None)    

    # ------------------------------------------------------------------
    # PORTAPAPELES PARA LA LISTA MULTI-ARCHIVO
    # ------------------------------------------------------------------
    def paste_multi_files(self, listbox_widget):
        try:
            clipboard_text = self.root.clipboard_get()
            if clipboard_text:
                clipboard_text = clipboard_text.strip().rstrip(";")
                parsed_paths = self.parse_paths(clipboard_text)
                for p in parsed_paths:
                    listbox_widget.insert(tk.END, p.encode("latin-1"))
        except Exception:
            pass
        return "break"

    def copy_multi_files(self, listbox_widget):
        selection = listbox_widget.curselection()
        if not selection:
            return "break"

        selected_paths = [listbox_widget.get(i) for i in selection]
        clipboard_value = ";".join(selected_paths)

        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_value)
        return "break"

    def cut_multi_files(self, listbox_widget):
        selection = listbox_widget.curselection()
        if not selection:
            return "break"

        selected_paths = [listbox_widget.get(i) for i in selection]
        clipboard_value = ";".join(selected_paths)

        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_value)

        for index in reversed(selection):
            listbox_widget.delete(index)
        return "break"

    # ------------------------------------------------------------------
    # EJECUCIÓN DEL PROGRAMA SELECCIONADO
    # ------------------------------------------------------------------
    def on_run_clicked(self):
        try:
            self.cache_current_form_state()
            program_name = self.get_selected_program_name()
            if not program_name:                
                return
            
            current_params = self.get_program_state(program_name)
            prog_info = self.get_program_definition(program_name)
            param_types = {p["name"]: p["type"] for p in prog_info.get("parameters", [])}

            parsed_params = {}
            for name, val in current_params.items():
                p_type = param_types.get(name)
                if p_type == "multi_file":
                    parsed_params[name] = val if isinstance(val, list) else self.parse_paths(self.safe_text(val))
                else:
                    parsed_params[name] = val

            parsed_params["output_dir"] = self.state.workspace.output_dir
            parsed_params["temp_dir"] = self.state.workspace.temp_dir
            self.state.workspace.ensure_workspace_exists()

            prog_instance = self.program_instances.get(program_name)
            if prog_instance and hasattr(prog_instance, "run"):                
                print("\nStarting Execution: " + program_name)
                prog_instance.run(parsed_params)                
                print("Finished Execution: " + program_name + "\n")

                
        except Exception as e:
            print("Execution Error: {}".format(e))

    # ------------------------------------------------------------------
    # RUTAS DE TRABAJO (Output / Temp)
    # ------------------------------------------------------------------
    def configure_workspace_paths(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Configure Workspace Paths")
        dlg.geometry("520x160")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        def add_path_row(row_idx, label_text, default_val):
            tk.Label(dlg, text=label_text).grid(row=row_idx, column=0, sticky="w", padx=10, pady=10)
            entry = tk.Entry(dlg, width=45, font=("Courier", 9))
            entry.grid(row=row_idx, column=1, padx=5, pady=10)
            entry.insert(0, default_val)
            tk.Button(dlg, text="...", command=lambda: self._browse_directory(entry)).grid(row=row_idx, column=2, padx=5)
            return entry

        cwd_entry = add_path_row(0, "Working Directory:", self.state.workspace.working_dir)
        out_entry = add_path_row(1, "Output Directory:", self.state.workspace.output_dir)
        temp_entry = add_path_row(2, "Temp Directory:", self.state.workspace.temp_dir)
        
        def save_and_close():
            self.state.workspace.working_dir = cwd_entry.get().strip()
            self.state.workspace.output_dir = out_entry.get().strip()
            self.state.workspace.temp_dir = temp_entry.get().strip()
            dlg.destroy()

        tk.Button(dlg, text="Save Paths", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"),
                  command=save_and_close).grid(row=2, column=1, sticky="e", pady=10)


    def _browse_file(self, entry_widget, dialog_type):
        if dialog_type == "file":
            filename = tkFileDialog.askopenfilename()
        else:
            filename = tkFileDialog.asksaveasfilename()
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)

    
    def _browse_directory(self, entry_widget):
        folder = tkFileDialog.askdirectory()
        if folder:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder)


    def _edit_file(self, entry_widget):
        raw_path = entry_widget.get().strip()
        if not raw_path:
            return
        paths = self.parse_paths(raw_path)
        target_path = paths[0] if paths else raw_path
        self._open_single_file(target_path)


    def _add_multi_files(self, listbox_widget):
        filenames = tkFileDialog.askopenfilenames()
        if filenames:
            for f in filenames:
                listbox_widget.insert(tk.END, f)


    def _remove_multi_files(self, listbox_widget):
        selected_indices = listbox_widget.curselection()
        for index in reversed(selected_indices):
            listbox_widget.delete(index)


    def _bind_listbox_context_menu(self, lb):
        lb.bind("<Control-v>", lambda e: self.paste_multi_files(lb))
        lb.bind("<Control-c>", lambda e: self.copy_multi_files(lb))
        lb.bind("<Control-x>", lambda e: self.cut_multi_files(lb))

        menu = tk.Menu(lb, tearoff=0)
        menu.add_command(label="Add Files...", command=lambda: self._add_multi_files(lb))
        menu.add_command(label="Open/Edit Selected", command=lambda: self._open_selected_listbox_file(lb))
        menu.add_separator()
        menu.add_command(label="Cut", command=lambda: self.cut_multi_files(lb))
        menu.add_command(label="Copy", command=lambda: self.copy_multi_files(lb))
        menu.add_command(label="Paste", command=lambda: self.paste_multi_files(lb))
        menu.add_separator()
        menu.add_command(label="Remove Selected", command=lambda: self._remove_multi_files(lb))

        def show_menu(event):
            if not lb.curselection():
                idx = lb.nearest(event.y)
                if idx >= 0: lb.selection_set(idx)
            menu.tk_popup(event.x_root, event.y_root)

        lb.bind("<Button-2>" if sys.platform == "darwin" else "<Button-3>", show_menu)
        if sys.platform == "darwin": lb.bind("<Control-Button-1>", show_menu)


    def open_config_wizard(self):
        try:
            from pssegui.tools.config_wizard import ConfigWizardApp
            ConfigWizardApp(self.root) 
        except Exception as e:
            TkMessageBox.showerror("Error", "No se pudo cargar la herramienta: {}".format(e))


    def _open_selected_listbox_file(self, listbox):
        selection = listbox.curselection()
        if not selection:
            print("No file selected in the list.")
            return

        for index in selection:
            filepath = listbox.get(index).strip()
            if filepath:
                self._open_single_file(filepath)




    def _bind_mouse_scroll(self, widget):
        if sys.platform == "win32" or sys.platform == "darwin":
            widget.bind("<MouseWheel>", lambda event: self._on_mouse_wheel(event, widget))
        else:
            widget.bind("<Button-4>", lambda event: self._on_linux_scroll(event, widget, -1))
            widget.bind("<Button-5>", lambda event: self._on_linux_scroll(event, widget, 1))

    def _on_mouse_wheel(self, event, widget):
        widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_linux_scroll(self, event, widget, direction):
        widget.yview_scroll(direction, "units")

    # ==================================================================
    # UTILERÍAS ESTÁTICAS (Independientes de clase)
    # ==================================================================
    
    @staticmethod
    def safe_text(val):
        if val is None:
            return ""
        if type(val).__name__ == 'unicode':
            return val
        if sys.version_info[0] < 3 and isinstance(val, str):
            try:
                return val.decode('utf-8')
            except Exception:
                try:
                    return val.decode('utf-8')
                except Exception:
                    return val
        return str(val)

    @staticmethod
    def parse_paths(entry_value):
        if not entry_value:
            return []

        # 1. Normalizar saltos de línea y comas, convirtiéndolos a punto y coma
        normalized = entry_value.replace("\r\n", ";").replace("\n", ";").replace(",", ";")

        # 2. Si es una sola línea pegada sin separadores (ej: "C:\ruta1" "D:\ruta2")
        if ";" not in normalized:
            if '"' in normalized:
                found_paths = re.findall(r'"([^"]*)"', normalized)
                if found_paths and len(found_paths) > 1:
                    return [p.strip() for p in found_paths if p.strip()]

            # Si pegan rutas por las letras de la unidad sin espacios/comas
            drive_splits = re.findall(r'[a-zA-Z]:\\[^:]+?(?=[a-zA-Z]:\\|$)', normalized)
            if len(drive_splits) > 1:
                return [p.strip().strip('"').strip("'") for p in drive_splits if p.strip()]

        # 3. Separar por punto y coma (que ahora incluye todos los saltos de línea)
        raw_splits = normalized.split(";")
        cleaned_paths = []
        for p in raw_splits:
            p_clean = p.strip().strip('"').strip("'")
            if p_clean:
                cleaned_paths.append(p_clean)

        return cleaned_paths


    @staticmethod
    def _open_single_file(target_path):
        try:
            directory = os.path.dirname(target_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            if not os.path.exists(target_path):
                with open(target_path, 'w') as f:
                    f.write("# Created automatically by PSS/E Automation Suite\n")
                print("Created missing file: " + target_path)

            if sys.platform == "win32":
                os.startfile(target_path)
            else:
                os.system('xdg-open "%s"' % target_path)
        except Exception as e:
            print("Could not open or create file: " + str(e))


    @staticmethod
    def _open_directory(target_dir):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        if sys.platform == "win32":
            os.startfile(target_dir)
        else:
            os.system('xdg-open "%s"' % target_dir)
