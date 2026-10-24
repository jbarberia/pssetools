 # coding: latin-1
import os
import re
import sys

try:
	import tkinter as tk
	from tkinter import filedialog as tkFileDialog
	from tkinter import messagebox as tkMessageBox
	from tkinter import ttk
except ImportError:
	import Tkinter as tk
	import tkFileDialog
	import tkMessageBox
	import ttk

from pssetools.utils.parse_sub import parse_sub
from pssetools.utils.sensitivity_report import save_sensitivity_table


class SensitivityAnalysisApp(object):
	"""Ventana de configuracion y ejecucion de sensibilidad de PSS/E.

	La ventana usa las APIs ``sensitivity_*`` de ``psspy`` y redirige cada
	reporte a ``temp_dir`` antes de convertirlo a una tabla Excel.
	"""

	def __init__(self, parent, temp_dir=None):
		if not sys.argv:
			sys.argv = ["gui"]

		self.root = tk.Toplevel(parent)
		self.root.title("Sensitivity Analysis")
		self.root.geometry("660x655")
		self.root.minsize(660, 655)
		self.root.resizable(False, False)
		self.root.attributes("-topmost", True)
		self.temp_dir = temp_dir or os.path.expanduser(os.path.join("~", "Desktop", "temp"))
		self.last_report_file = None
		self.last_table_file = None
		self._build_variables()
		self._build_layout()
		self.root.bind("<Escape>", self.close)

	def _build_variables(self):
		self.network_model = tk.StringVar(value="ac")
		self.tolerance = tk.StringVar(value="0.600")
		self.cutoff = tk.StringVar(value="0.001")
		self.device_type = tk.StringVar(value="bus")
		self.flow_type = tk.StringVar(value="MW")
		self.transformer_type = tk.StringVar(value="3W Transformer")
		self.branch_selection = tk.StringVar(value="2002, 2292, 2804, '1 '")
		self.bus_number = tk.StringVar(value="3000")
		self.branch_subsystem = tk.StringVar()
		self.bus_subsystem = tk.StringVar()
		self.interface = tk.StringVar()
		self.device_system = tk.StringVar()
		self.transfer_direction = tk.StringVar(value="to")
		self.opposing_type = tk.StringVar(value="subsystem")
		self.opposing_subsystem = tk.StringVar()
		self.dispatch_mode = tk.StringVar(value="DFAX generation")
		self.dfx_path = tk.StringVar()
		self.subsystem_names = []
		self.subsystem_file = None
		self.subsystem_widgets = []
		self.opposing_value_widget = None
		self.device_flags = {
			"bus": tk.BooleanVar(value=True),
			"generator": tk.BooleanVar(value=True),
			"load": tk.BooleanVar(value=True),
			"phase_shifter": tk.BooleanVar(value=True),
			"tap_changer": tk.BooleanVar(value=True),
			"switched_shunt": tk.BooleanVar(value=True),
		}

	def _build_layout(self):
		outer = tk.Frame(self.root, padx=10, pady=8)
		outer.pack(fill="both", expand=True)
		top = tk.Frame(outer)
		top.pack(fill="x")
		self._build_model_group(top)
		self._build_tolerance_group(top)
		self._build_device_group(outer)
		self._build_target_group(outer)
		self._build_output_row(outer)
		self._update_device_state()
		buttons = tk.Frame(outer)
		buttons.pack(fill="x", pady=(10, 0))
		tk.Button(buttons, text="Solve", width=10, command=self.solve).pack(side="left", padx=(237, 8))
		tk.Button(buttons, text="Close", width=10, command=self.close).pack(side="left")

	def _label_frame(self, parent, text):
		frame = tk.LabelFrame(parent, text=text, padx=8, pady=5)
		frame.pack(fill="x", pady=(0, 7))
		return frame

	def _build_model_group(self, parent):
		frame = tk.LabelFrame(parent, text="Network model", padx=5, pady=4, width=192, height=52)
		frame.pack(side="left", fill="y", padx=(0, 18))
		frame.pack_propagate(False)
		tk.Radiobutton(frame, text="DC network", variable=self.network_model, value="dc").pack(side="left")
		tk.Radiobutton(frame, text="AC network", variable=self.network_model, value="ac").pack(side="left")

	def _build_tolerance_group(self, parent):
		frame = tk.Frame(parent)
		frame.pack(side="left", fill="x", expand=True, pady=2)
		tk.Label(frame, text="Initial condition MW mismatch tolerance").grid(row=0, column=0, sticky="w")
		tk.Spinbox(frame, from_=0, to=999, increment=0.001, textvariable=self.tolerance, width=7).grid(row=0, column=1, padx=(8, 0))
		tk.Label(frame, text="Sensitivity factor cutoff").grid(row=1, column=0, sticky="w", pady=(6, 0))
		tk.Spinbox(frame, from_=0, to=999, increment=0.0001, textvariable=self.cutoff, width=7).grid(row=1, column=1, padx=(8, 0), pady=(6, 0))

	def _build_device_group(self, parent):
		frame = self._label_frame(parent, "Select device for which sensitivity factors are calculated")
		frame.columnconfigure(1, weight=1)
		tk.Radiobutton(frame, text="Branch", variable=self.device_type, value="branch", command=self._update_device_state).grid(row=0, column=0, sticky="w")
		tk.Label(frame, text="Flow type").grid(row=0, column=1, sticky="w")
		self.flow_type_widget = ttk.Combobox(frame, textvariable=self.flow_type, values=("MW", "MVAR", "MVA", "Amps"), state="disabled", width=15)
		self.flow_type_widget.grid(row=0, column=2, sticky="w", padx=5)
		tk.Label(frame, text="Type").grid(row=0, column=3, sticky="w", padx=(18, 0))
		self.transformer_type_widget = ttk.Combobox(frame, textvariable=self.transformer_type, values=("Non-Transformer", "2W Transformer", "3W Transformer"), state="disabled", width=20)
		self.transformer_type_widget.grid(row=0, column=4, sticky="w", padx=5)
		tk.Label(frame, text="From bus (Number)").grid(row=1, column=0, sticky="w", pady=(8, 0))
		tk.Label(frame, text="To bus (Number)").grid(row=1, column=1, sticky="w", pady=(8, 0))
		tk.Label(frame, text="Last bus (Number)").grid(row=1, column=2, sticky="w", pady=(8, 0))
		tk.Label(frame, text="Circuit ID").grid(row=1, column=3, sticky="w", padx=(18, 0), pady=(8, 0))
		tk.Entry(frame, textvariable=self.branch_selection, state="disabled", width=66).grid(row=2, column=0, columnspan=4, sticky="ew", pady=(2, 5))
		tk.Button(frame, text="Select...", width=9, command=lambda: self.select_value(self.branch_selection)).grid(row=2, column=4, padx=5)
		self._device_radio(frame, 3, "Branches in subsystem", "branch_subsystem", self.branch_subsystem, self.subsystem_names)
		self._device_radio(frame, 4, "Bus", "bus", self.bus_number)
		self._device_radio(frame, 5, "Buses in subsystem", "bus_subsystem", self.bus_subsystem, self.subsystem_names)
		self._device_radio(frame, 6, "Interface", "interface", self.interface, ("", "INTERFACE 1"))

	def _device_radio(self, frame, row, label, value, variable, values=None):
		tk.Radiobutton(frame, text=label, variable=self.device_type, value=value, command=self._update_device_state).grid(row=row, column=0, sticky="w", pady=2)
		if values is not None:
			widget = ttk.Combobox(frame, textvariable=variable, values=values, width=20, state="disabled")
			if value in ("branch_subsystem", "bus_subsystem"):
				self.subsystem_widgets.append(widget)
		else:
			widget = tk.Entry(frame, textvariable=variable, width=21, state="disabled")
		widget.grid(row=row, column=1, sticky="w", pady=2)
		setattr(self, value + "_widget", widget)

	def _build_target_group(self, parent):
		frame = self._label_frame(parent, "Select devices to which sensitivity factors are calculated")
		tk.Label(frame, text="Device system").grid(row=0, column=0, sticky="w")
		self.device_system_widget = ttk.Combobox(frame, textvariable=self.device_system, values=self.subsystem_names, width=18)
		self.device_system_widget.grid(row=0, column=1, sticky="w", padx=5)
		labels = (("bus", "Bus"), ("generator", "Generator bus"), ("load", "Load bus"), ("phase_shifter", "Phase shifter control"), ("tap_changer", "Tap changing transformer"), ("switched_shunt", "Switched shunt"))
		for row, (key, label) in enumerate(labels, 1):
			tk.Checkbutton(frame, text=label, variable=self.device_flags[key]).grid(row=row, column=0, columnspan=2, sticky="w")
		transfer = tk.LabelFrame(frame, text="Transfer", padx=8, pady=5)
		transfer.grid(row=1, column=2, rowspan=6, sticky="nsew", padx=(15, 0))
		tk.Radiobutton(transfer, text="From device", variable=self.transfer_direction, value="from").grid(row=0, column=0, sticky="w")
		tk.Radiobutton(transfer, text="To device", variable=self.transfer_direction, value="to").grid(row=0, column=1, sticky="w")
		tk.Label(transfer, text="Opposing subsys type").grid(row=1, column=0, sticky="w", pady=(8, 0))
		opposing_type_widget = ttk.Combobox(transfer, textvariable=self.opposing_type, values=("Slack", "Single Bus", "subsystem"), width=14, state="readonly")
		opposing_type_widget.grid(row=1, column=1, sticky="w", padx=5, pady=(8, 0))
		opposing_type_widget.bind("<<ComboboxSelected>>", self._update_opposing_state)
		self.opposing_value_widget = ttk.Combobox(transfer, textvariable=self.opposing_subsystem, values=self.subsystem_names, width=16)
		self.opposing_value_widget.grid(row=2, column=1, sticky="w", padx=5, pady=4)
		tk.Label(transfer, text="Dispatch mode").grid(row=3, column=0, sticky="w")
		ttk.Combobox(transfer, textvariable=self.dispatch_mode, values=("DFAX generation", "PTDF generation"), width=20).grid(row=3, column=1, sticky="w", padx=5)

	def _build_output_row(self, parent):
		frame = tk.Frame(parent)
		frame.pack(fill="x", pady=(0, 2))
		tk.Label(frame, text="Distribution\nfactor data file", justify="left").pack(side="left", anchor="w")
		tk.Entry(frame, textvariable=self.dfx_path).pack(side="left", fill="x", expand=True, padx=8)
		tk.Button(frame, text="...", width=3, command=self.browse_dfx).pack(side="left", padx=(0, 8))
		tk.Button(frame, text="DFAX...", width=9, command=self.generate_dfax).pack(side="left")

	def _update_device_state(self):
		selected = self.device_type.get()
		branch_state = "normal" if selected == "branch" else "disabled"
		self.flow_type_widget.configure(state=branch_state)
		self.transformer_type_widget.configure(state=branch_state)
		for name in ("branch_subsystem", "bus", "bus_subsystem", "interface"):
			widget = getattr(self, name + "_widget")
			widget.configure(state="normal" if selected == name else "disabled")

	def select_value(self, variable):
		self._open_branch_selector(variable)

	def _open_branch_selector(self, variable):
		try:
			import psspy
			buses = self._get_selector_buses(psspy)
			branches = self._get_selector_branches(psspy)
		except Exception as error:
			tkMessageBox.showerror("Branch Selection", "No se pudieron leer los elementos del caso activo:\n{}".format(error))
			return

		dialog = tk.Toplevel(self.root)
		dialog.title("Branch Selection")
		dialog.geometry("670x420")
		dialog.resizable(False, False)
		dialog.transient(self.root)
		dialog.grab_set()

		outer = tk.Frame(dialog, padx=10, pady=8)
		outer.pack(fill="both", expand=True)
		left = tk.LabelFrame(outer, text="From bus", padx=5, pady=5)
		left.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=(0, 8))
		right_title = "Winding 1 / 2 / 3" if self.transformer_type.get() == "3W Transformer" else "To bus / Circuit ID"
		right = tk.LabelFrame(outer, text=right_title, padx=5, pady=5)
		right.grid(row=0, column=1, rowspan=3, sticky="nsew")
		outer.columnconfigure(1, weight=1)

		filter_frame = tk.Frame(left)
		filter_frame.pack(fill="x")
		filter_var = tk.StringVar()
		tk.Label(filter_frame, text="Filter").pack(side="left")
		tk.Entry(filter_frame, textvariable=filter_var, width=19).pack(side="left", padx=5)
		bus_list = tk.Listbox(left, width=31, height=16, exportselection=False)
		bus_list.pack(fill="both", expand=True, pady=(6, 0))

		branch_list = tk.Listbox(right, width=47, height=16, exportselection=False)
		branch_list.pack(fill="both", expand=True)

		selection_var = tk.StringVar()
		tk.Label(outer, text="Selection").grid(row=3, column=0, sticky="w", pady=(8, 0))
		tk.Entry(outer, textvariable=selection_var, state="readonly", width=65).grid(row=3, column=1, sticky="ew", pady=(8, 0))

		filtered_buses = []
		filtered_branches = []

		def refresh_branches(event=None):
			branch_list.delete(0, tk.END)
			filtered_branches[:] = []
			selection = bus_list.curselection()
			if not selection:
				return
			bus_number = filtered_buses[selection[0]][0]
			for branch in branches:
				if branch[1] != bus_number:
					continue
				text = branch[0]
				filtered_branches.append(branch)
				branch_list.insert(tk.END, text)

		def refresh_buses(*args):
			bus_list.delete(0, tk.END)
			filtered_buses[:] = []
			term = filter_var.get().strip().lower()
			for bus in buses:
				if term and term not in bus[1].lower() and term not in str(bus[0]):
					continue
				filtered_buses.append(bus)
				bus_list.insert(tk.END, bus[1])
			if filtered_buses:
				bus_list.selection_set(0)
				refresh_branches()

		def update_selection(event=None):
			selection = branch_list.curselection()
			if not selection:
				return
			branch = filtered_branches[selection[0]]
			selection_var.set(branch[2])

		def accept():
			if not selection_var.get():
				tkMessageBox.showwarning("Branch Selection", "Selecciona una rama o transformador.", parent=dialog)
				return
			variable.set(selection_var.get())
			dialog.destroy()

		filter_var.trace("w", refresh_buses)
		bus_list.bind("<<ListboxSelect>>", refresh_branches)
		branch_list.bind("<<ListboxSelect>>", update_selection)
		refresh_buses()

		buttons = tk.Frame(outer)
		buttons.grid(row=4, column=1, sticky="e", pady=(10, 0))
		tk.Button(buttons, text="OK", width=10, command=accept).pack(side="left", padx=6)
		tk.Button(buttons, text="Cancel", width=10, command=dialog.destroy).pack(side="left")

	def _get_selector_buses(self, psspy):
		ierr, (numbers,) = psspy.abusint(-1, 2, ["NUMBER"])
		ierr, (names,) = psspy.abuschar(-1, 2, ["NAME"])
		ierr, (kv,) = psspy.abusreal(-1, 2, ["BASE"])
		return [(number, "{} [{}] {:.2f} kV".format(number, name.strip(), base)) for number, name, base in zip(numbers, names, kv)]

	def _get_selector_branches(self, psspy):
		if self.transformer_type.get() == "3W Transformer":
			ierr, (from_bus, to_bus, third_bus) = psspy.atr3int(string=["WIND1NUMBER", "WIND2NUMBER", "WIND3NUMBER"])
			ierr, (ckt,) = psspy.atr3char(string=["ID"])
			return [("{} - {} - {} #{}".format(i, j, k, c), i, "{},{},{},'{}'".format(i, j, k, c.strip())) for i, j, k, c in zip(from_bus, to_bus, third_bus, ckt)]

		ierr, (from_bus, to_bus) = psspy.abrnint(string=["FROMNUMBER", "TONUMBER"])
		ierr, (ckt,) = psspy.abrnchar(string=["ID"])
		return [("{} - {} #{}".format(i, j, c), i, "{},{},'{}'".format(i, j, c.strip())) for i, j, c in zip(from_bus, to_bus, ckt)]

	def browse_dfx(self):
		filename = tkFileDialog.askopenfilename(filetypes=[("DFX files", "*.dfx"), ("All files", "*.*")])
		if filename:
			self.dfx_path.set(filename)
			self.load_subsystems_from_dfx(filename)

	def generate_dfax(self):
		dialog = tk.Toplevel(self.root)
		dialog.title("Build Distribution Factor Data File")
		dialog.geometry("730x285")
		dialog.resizable(False, False)
		dialog.transient(self.root)
		dialog.grab_set()

		outer = tk.Frame(dialog, padx=10, pady=8)
		outer.pack(fill="both", expand=True)
		files_frame = tk.LabelFrame(outer, text="Input files", padx=8, pady=7)
		files_frame.pack(fill="x")
		files_frame.columnconfigure(1, weight=1)

		dfx_files = self._get_dfax_input_files(self.dfx_path.get().strip())
		file_vars = {
			"sub": tk.StringVar(value=dfx_files.get("sub", self.subsystem_file or "")),
			"mon": tk.StringVar(value=dfx_files.get("mon", "")),
			"con": tk.StringVar(value=dfx_files.get("con", "")),
			"dfx": tk.StringVar(value=self.dfx_path.get().strip()),
		}
		file_types = {
			"sub": [("Subsystem files", "*.sub"), ("All files", "*.*")],
			"mon": [("Monitor files", "*.mon"), ("All files", "*.*")],
			"con": [("Contingency files", "*.con"), ("All files", "*.*")],
			"dfx": [("DFAX files", "*.dfx"), ("All files", "*.*")],
		}
		labels = (
			("sub", "Subsystem definition file"),
			("mon", "Monitored element file"),
			("con", "Contingency description file"),
		)

		def browse_file(kind):
			filename = tkFileDialog.askopenfilename(filetypes=file_types[kind])
			if filename:
				file_vars[kind].set(filename)

		def edit_file(kind):
			filename = file_vars[kind].get().strip()
			if not filename:
				return
			try:
				if sys.platform == "win32":
					try:
						os.startfile(filename)
					except AttributeError:
						os.system('xdg-open "{}"'.format(filename))
				else:
					os.system('xdg-open "{}"'.format(filename))
			except Exception as error:
				tkMessageBox.showerror("DFAX", "No se pudo abrir el archivo:\n{}".format(error), parent=dialog)

		for row, (kind, label) in enumerate(labels):
			tk.Label(files_frame, text=label).grid(row=row, column=0, sticky="w", pady=4)
			entry = ttk.Combobox(files_frame, textvariable=file_vars[kind])
			entry.grid(row=row, column=1, sticky="ew", padx=8, pady=4)
			tk.Button(files_frame, text="...", width=3, command=lambda item=kind: browse_file(item)).grid(row=row, column=2, padx=(0, 8))
			tk.Button(files_frame, text="Edit...", width=8, command=lambda item=kind: edit_file(item)).grid(row=row, column=3)

		sort_var = tk.BooleanVar(value=True)
		out_of_service_var = tk.BooleanVar(value=True)
		tk.Checkbutton(outer, text="Sort Monitored elements for reporting", variable=sort_var).pack(anchor="w", pady=(7, 0))
		tk.Checkbutton(outer, text="Monitor out-of-service lines", variable=out_of_service_var).pack(anchor="w")

		mode_frame = tk.Frame(outer)
		mode_frame.pack(fill="x", pady=(5, 0))
		tk.Label(mode_frame, text="Prepare file for use with").pack(side="left")
		mode_var = tk.StringVar(value="AC and/or DC analysis")
		tk.Combobox(mode_frame, textvariable=mode_var, state="readonly", values=("AC and/or DC analysis", "DC analysis"), width=22).pack(side="left", padx=8)

		output_frame = tk.Frame(outer)
		output_frame.pack(fill="x", pady=(7, 0))
		tk.Label(output_frame, text="Distribution factor output file").pack(side="left")
		tk.Combobox(output_frame, textvariable=file_vars["dfx"]).pack(side="left", fill="x", expand=True, padx=8)
		tk.Button(output_frame, text="...", width=3, command=lambda: self._browse_dfax_output(file_vars["dfx"])).pack(side="left")

		buttons = tk.Frame(outer)
		buttons.pack(pady=(12, 0))
		tk.Button(buttons, text="Generate DFAX", width=16, command=lambda: self._run_dfax(dialog, file_vars, sort_var, out_of_service_var, mode_var)).pack(side="left", padx=8)
		tk.Button(buttons, text="Cancel", width=10, command=dialog.destroy).pack(side="left")

	def _browse_dfax_output(self, variable):
		filename = tkFileDialog.asksaveasfilename(
			defaultextension=".dfx",
			filetypes=[("DFAX files", "*.dfx"), ("All files", "*.*")],
		)
		if filename:
			variable.set(filename)

	def _get_dfax_input_files(self, dfx_path):
		if not dfx_path:
			return {}
		try:
			import arrbox.dfax_pp
			dfx_object = arrbox.dfax_pp.DFAX_PP(dfx_path)
			file_data = getattr(dfx_object.otdf_factors(), "file", None)
			result = {}
			for key in ("sub", "mon", "con"):
				value = getattr(file_data, key, None)
				if value:
					value = str(value)
					if not os.path.isabs(value):
						value = os.path.join(os.path.dirname(dfx_path), value)
					result[key] = os.path.abspath(value)
			return result
		except Exception:
			return {}

	def _run_dfax(self, dialog, file_vars, sort_var, out_of_service_var, mode_var):
		paths = {name: variable.get().strip() for name, variable in file_vars.items()}
		missing = [name for name in ("sub", "mon", "con", "dfx") if not paths[name]]
		if missing:
			tkMessageBox.showwarning("DFAX", "Completa todos los archivos de entrada y salida.", parent=dialog)
			return

		try:
			import psspy
		except ImportError:
			tkMessageBox.showinfo("DFAX", "La generación DFAX requiere el entorno de PSS/E.", parent=dialog)
			return

		try:
			flags = [
				1 if sort_var.get() else 0,
				1 if out_of_service_var.get() else 0,
				0 if mode_var.get() == "DC analysis" else 1,
			]
			ierr = psspy.dfax_2(flags, paths["sub"], paths["mon"], paths["con"], paths["dfx"])
			if ierr != 0:
				tkMessageBox.showerror("DFAX", "PSS/E devolvio el codigo de error {}.".format(ierr), parent=dialog)
				return
			self.dfx_path.set(paths["dfx"])
			self.load_subsystems_from_dfx(paths["dfx"])
			dialog.destroy()
		except Exception as error:
			tkMessageBox.showerror("DFAX", "No se pudo generar el archivo:\n{}".format(error), parent=dialog)

	def solve(self):
		"""Ejecutar la sensibilidad y exportar el reporte textual y tabular."""
		dfx_path = self.dfx_path.get().strip()
		if not dfx_path:
			tkMessageBox.showwarning("Sensitivity Analysis", "Select a distribution factor data file first.")
			return
		try:
			import psspy
		except ImportError:
			tkMessageBox.showinfo("Sensitivity Analysis", "Configuration ready. Solve requires the PSS/E environment.")
			return

		try:
			mainsys = self.device_system.get().strip()
			if not mainsys:
				tkMessageBox.showwarning("Sensitivity Analysis", "Select a device system first.")
				return

			oppsys = self.opposing_subsystem.get().strip()
			if not os.path.exists(self.temp_dir):
				os.makedirs(self.temp_dir)
			report_file = os.path.join(self.temp_dir, "sensitivity_report.txt")
			table_file = os.path.join(self.temp_dir, "sensitivity_report.xlsx")
			try:
				psspy.report_output(2, report_file, [0, 0])
				if self.device_type.get() == "branch":
					ierr = self._solve_flow(psspy, dfx_path, mainsys, oppsys)
				elif self.device_type.get() == "branch_subsystem":
					ierr = self._solve_flows(psspy, dfx_path, mainsys, oppsys)
				elif self.device_type.get() == "bus_subsystem":
					ierr = self._solve_voltages(psspy, dfx_path, mainsys, oppsys)
				elif self.device_type.get() == "interface":
					ierr = self._solve_interface(psspy, dfx_path, mainsys, oppsys)
				else:
					ierr = self._solve_voltage(psspy, dfx_path, mainsys, oppsys)
			finally:
				psspy.report_output(1, "", [0, 0])
			if ierr != 0:
				tkMessageBox.showerror("Sensitivity Analysis", "PSS/E devolvio el codigo de error {}.".format(ierr))
			else:
				save_sensitivity_table(report_file, table_file)
				self.last_report_file = report_file
				self.last_table_file = table_file
				tkMessageBox.showinfo(
					"Sensitivity Analysis",
					"Sensitivity analysis completed.\n\nReport:\n{}\n\nTable:\n{}".format(report_file, table_file),
				)
		except Exception as error:
			tkMessageBox.showerror("Sensitivity Analysis", "Sensitivity analysis failed:\n{}".format(error))

	def _solve_flow(self, psspy, dfx_path, mainsys, oppsys):
		ibus, jbus, kbus, ckt = self._parse_branch_selection()
		flow_codes = {"MW": 0, "MVAR": 1, "MVA": 2, "Amps": 3}
		flwopt = [
			ibus,
			jbus,
			kbus,
			1 if self.network_model.get() == "ac" else 0,
			flow_codes[self.flow_type.get()],
		]
		options = self._sensitivity_device_options(oppsys, voltage=False)
		labels = [mainsys, oppsys if self._opposing_type_code() == "subsystem" else ""]
		return psspy.sensitivity_flow(
			flwopt,
			options,
			[self._number(self.tolerance.get()), self._number(self.cutoff.get())],
			ckt,
			labels,
			dfx_path,
		)

	def _solve_voltage(self, psspy, dfx_path, mainsys, oppsys):
		try:
			bus_number = int(self.bus_number.get())
		except ValueError:
			raise ValueError("Bus number must be an integer.")
		options = self._sensitivity_device_options(oppsys, voltage=True)
		labels = [mainsys, oppsys if self._opposing_type_code() == "subsystem" else ""]
		return psspy.sensitivity_voltage(
			bus_number,
			options,
			[self._number(self.tolerance.get()), self._number(self.cutoff.get())],
			labels,
			dfx_path,
		)

	def _solve_flows(self, psspy, dfx_path, mainsys, oppsys):
		flow_codes = {"MW": 0, "MVAR": 1, "MVA": 2, "Amps": 3}
		flwopt = [
			1 if self.network_model.get() == "ac" else 0,
			flow_codes[self.flow_type.get()],
		]
		options = self._sensitivity_device_options(oppsys)
		labels = [mainsys, oppsys if self._opposing_type_code() == "subsystem" else "", self.branch_subsystem.get().strip()]
		return psspy.sensitivity_flows(
			flwopt,
			options,
			[self._number(self.tolerance.get()), self._number(self.cutoff.get())],
			labels,
			dfx_path,
		)

	def _solve_voltages(self, psspy, dfx_path, mainsys, oppsys):
		options = self._sensitivity_device_options(oppsys, voltage=True)
		labels = [mainsys, oppsys if self._opposing_type_code() == "subsystem" else "", self.bus_subsystem.get().strip()]
		return psspy.sensitivity_voltages(
			options,
			[self._number(self.tolerance.get()), self._number(self.cutoff.get())],
			labels,
			dfx_path,
		)

	def _solve_interface(self, psspy, dfx_path, mainsys, oppsys):
		interface = self.interface.get().strip()
		if not interface:
			raise ValueError("Select an interface first.")
		options = self._sensitivity_device_options(oppsys)
		labels = [mainsys, oppsys if self._opposing_type_code() == "subsystem" else "", interface]
		return psspy.sensitivity_interface(
			1 if self.network_model.get() == "ac" else 0,
			options,
			[self._number(self.tolerance.get()), self._number(self.cutoff.get())],
			labels,
			dfx_path,
		)

	def _sensitivity_device_options(self, oppsys, voltage=False):
		flags = [int(self.device_flags[key].get()) for key in ("bus", "generator", "load", "phase_shifter", "tap_changer", "switched_shunt")]
		opposing_type = self._opposing_type_code()
		if voltage:
			opposing_codes = {"slack bus": 0, "single bus": 1, "subsystem": 2}
			last_value = self._opposing_option_value(opposing_type, oppsys)
			transfer_code = 0 if self.transfer_direction.get() == "from" else 1
			return flags + [transfer_code, opposing_codes[opposing_type], last_value]

		opposing_codes = {"slack bus": 0, "single bus": 1, "subsystem": 2}
		last_value = self._opposing_option_value(opposing_type, oppsys)
		transfer_code = 0 if self.transfer_direction.get() == "from" else 1
		return flags + [transfer_code, opposing_codes[opposing_type], last_value]

	def _opposing_option_value(self, opposing_type, value):
		if opposing_type == "slack bus":
			return 0
		if opposing_type == "subsystem":
			return 1 if self.dispatch_mode.get() == "DFAX generation" else 3
		try:
			return int(value)
		except ValueError:
			return 0

	def _parse_branch_selection(self):
		values = [value for value in re.split(r"[,;\s]+", self.branch_selection.get().replace("'", "").replace('"', "")) if value]
		if len(values) < 3:
			raise ValueError("Branch selection must contain from bus, to bus and circuit ID.")

		try:
			buses = [int(value) for value in values[:-1]]
		except ValueError:
			raise ValueError("Branch bus numbers must be integers.")

		if self.transformer_type.get() != "3W Transformer":
			if len(buses) != 2:
				raise ValueError("Non-Transformer y 2W Transformer requieren dos buses y el circuito.")
			return buses[0], buses[1], 0, values[-1]
		if len(buses) != 3:
			raise ValueError("3W Transformer requiere tres buses y el circuito.")
		return buses[0], buses[1], buses[2], values[-1]

	def _opposing_type_code(self):
		return {
			"Slack": "slack bus",
			"Single Bus": "single bus",
			"subsystem": "subsystem",
		}.get(self.opposing_type.get(), "subsystem")

	@staticmethod
	def _number(value):
		return float(str(value).replace(",", "."))

	@staticmethod
	def _result_summary(result):
		ngen = getattr(result, "ngenbuses", "?")
		nload = getattr(result, "nloadbuses", "?")
		return "Sensitivity analysis completed.\nGenerator buses: {}\nLoad buses: {}".format(ngen, nload)
	def _get_sub_file_from_dfx(self, dfx_path):
		try:
			import arrbox.dfax_pp
			dfx_object = arrbox.dfax_pp.DFAX_PP(dfx_path)
			otdf_object = dfx_object.otdf_factors()
			sub_file = getattr(getattr(otdf_object, "file", None), "sub", None)
			if sub_file:
				sub_file = str(sub_file)
				if not os.path.isabs(sub_file):
					sub_file = os.path.join(os.path.dirname(dfx_path), sub_file)
				return os.path.abspath(sub_file)
		except Exception:
			pass

		return os.path.splitext(dfx_path)[0] + ".sub"

	def load_subsystems_from_dfx(self, dfx_path=None):
		dfx_path = dfx_path or self.dfx_path.get().strip()
		if not dfx_path:
			return

		sub_file = self._get_sub_file_from_dfx(dfx_path)
		if not os.path.exists(sub_file):
			tkMessageBox.showwarning("Subsystem", "No se encontro el archivo .sub asociado:\n{}".format(sub_file))
			return

		try:
			subsystems = parse_sub(sub_file)
		except Exception as error:
			tkMessageBox.showwarning("Subsystem", "No se pudieron leer los subsistemas:\n{}".format(error))
			return

		self.subsystem_file = sub_file
		self.subsystem_names = sorted(subsystems.keys())
		for widget in self.subsystem_widgets:
			widget.configure(values=self.subsystem_names)
		self.device_system_widget.configure(values=self.subsystem_names)
		self.opposing_value_widget.configure(values=self.subsystem_names)
		if self.subsystem_names:
			self.device_system.set(self.subsystem_names[0])
			self.opposing_subsystem.set(self.subsystem_names[0])
		self._update_opposing_state()

	def _update_opposing_state(self, event=None):
		selected = self.opposing_type.get()
		if selected == "Slack":
			self.opposing_subsystem.set("")
			self.opposing_value_widget.configure(state="disabled")
		else:
			self.opposing_value_widget.configure(state="normal")
			if selected == "Single Bus":
				self.opposing_value_widget.configure(values=())
			else:
				self.opposing_value_widget.configure(values=self.subsystem_names)

	def close(self, event=None):
		self.root.destroy()
		return "break"


SensitivityApp = SensitivityAnalysisApp
