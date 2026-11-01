# coding: latin-1
"""
Sensitivity Analysis
--------------------
Calcula factores de distribucion y sensibilidad en PSS/E a partir de
archivos de red (.sav), subsistema (.sub), monitoreo (.mon o .tsv) y contingencias (.con).
Tabula los resultados en un archivo Excel.
"""

import os
import pandas as pd

from pssetools.programs import BaseProgram
from pssetools.utils.sensitivity_report import (
    parse_sensitivity_report, save_sensitivity_table, write_sensitivity_excel,
    _EMPTY_TABLES,
)



def parse_elements_tsv(tsv_file):
    """
    Lee un archivo TSV de elementos (similar al usado en Custom ACCC)
    y retorna una lista de diccionarios con la informacion de cada componente.
    """
    elements = []
    if not tsv_file or not os.path.exists(tsv_file):
        return elements

    with open(tsv_file, "r") as stream:
        for line in stream:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = [p.strip() for p in line.split("\t")]
            etype = parts[0].upper()
            if etype in ("ELEMENTO", "TYPE"):
                continue

            if etype == "BU":
                if len(parts) > 1 and parts[1]:
                    try:
                        ibus = int(parts[1])
                        desc = parts[5] if len(parts) > 5 else ""
                        elements.append({
                            "type": "BU",
                            "ibus": ibus,
                            "jbus": 0,
                            "kbus": 0,
                            "ckt": "",
                            "desc": desc,
                        })
                    except ValueError:
                        pass

            elif etype in ("LII", "TR", "SYS"):
                if len(parts) > 2 and parts[1] and parts[2]:
                    try:
                        ibus = int(parts[1])
                        jbus = int(parts[2])
                        ckt = parts[3] if len(parts) > 3 and parts[3] else "1"
                        desc = parts[5] if len(parts) > 5 else ""
                        elements.append({
                            "type": etype,
                            "ibus": ibus,
                            "jbus": jbus,
                            "kbus": 0,
                            "ckt": ckt,
                            "desc": desc,
                        })
                    except ValueError:
                        pass

            elif etype == "T3":
                if len(parts) > 3 and parts[1] and parts[2] and parts[3]:
                    try:
                        ibus = int(parts[1])
                        jbus = int(parts[2])
                        kbus = int(parts[3])
                        ckt = parts[4] if len(parts) > 4 and parts[4] else "1"
                        desc = parts[5] if len(parts) > 5 else ""
                        elements.append({
                            "type": "T3",
                            "ibus": ibus,
                            "jbus": jbus,
                            "kbus": kbus,
                            "ckt": ckt,
                            "desc": desc,
                        })
                    except ValueError:
                        pass

    return elements





class SensitivityProgram(BaseProgram):
    order = 23

    def get_parameters(self):
        """Returns parameter definitions for Sensitivity Analysis."""
        return [
            {
                "name": "cases",
                "label": "Working Case (.sav):",
                "type": "multi_file",
                "default": "",
            },
            {
                "name": "sub_file",
                "label": "Subsystem (.sub):",
                "type": "file",
                "default": "estudio.sub",
            },
            {
                "name": "mon_file",
                "label": "Monitored (.mon):",
                "type": "file",
                "default": "estudio.mon",
            },
            {
                "name": "con_file",
                "label": "Contingency (.con):",
                "type": "file",
                "default": "estudio.con",
            },
            {
                "name": "elements_file",
                "label": "Elements (.tsv):",
                "type": "file",
                "default": "monitor.tsv",
            },
            {
                "name": "source_subsystem",
                "label": "Source subsystem (Origen):",
                "type": "text",
                "default": "SYSTEM1",
            },
            {
                "name": "target_subsystem",
                "label": "Target subsystem (Destino):",
                "type": "text",
                "default": "SYSTEM2",
            },
            {
                "name": "ac_network",
                "label": "Use AC Network:",
                "type": "bool",
                "default": True,
            },
        ]

    def run(self, parsed_params):
        """Execute the sensitivity analysis based on parsed parameters."""
        self._run(**parsed_params)

    def _run(
        self,
        cases,
        sub_file,
        mon_file,
        con_file,
        elements_file,
        source_subsystem,
        target_subsystem,
        ac_network=True,
        output_dir=".",
        temp_dir=".",
    ):
        psspy = self.psspy
        psspy.psseinit()

        elements = parse_elements_tsv(elements_file)
        if not elements:
            raise ValueError("No valid elements found in TSV file: {}".format(elements_file))


        # Configuracion del subsistema opuesto
        target_upper = target_subsystem.upper()
        if target_upper in ("", "SLACK"):
            opp_type = 0  # Slack bus
            opp_val = 0
            labels = [source_subsystem, ""]
        elif target_subsystem.isdigit():
            opp_type = 1  # Single bus
            opp_val = int(target_subsystem)
            labels = [source_subsystem, ""]
        else:
            opp_type = 2  # Subsystem
            opp_val = 1
            labels = [source_subsystem, target_subsystem]

        options = [1, 1, 1, 1, 1, 1, 1, opp_type, opp_val]
        values = [0.5, 0.001]

        keys = list(_EMPTY_TABLES.keys())
        dfs = {k: [] for k in keys}
        combined_report_lines = []

        for case in cases:

            # open case
            base = os.path.splitext(os.path.basename(case))[0]
            ierr = psspy.case(case)
            if ierr != 0:
                print("Warning: Could not load case: {}. Error code: {}".format(case, ierr))
                continue

            # create dfax file
            dfx_file = os.path.join(temp_dir, "{}.dfx".format(base))
            ierr = psspy.dfax_2([1, 0, 1], sub_file, mon_file, con_file, dfx_file)
            if ierr != 0:
                raise RuntimeError("PSS/E dfax_2 returned error code {} for case {}".format(ierr, case))

            # redirect to report
            case_report_txt = os.path.join(temp_dir, "sensitivity_report_{}.txt".format(base))
            psspy.t_report_output(2, case_report_txt, [0, 0])

            try:
                for elem in elements:
                    etype = elem["type"]
                    if etype == "BU":
                        psspy.sensitivity_voltage(elem["ibus"], options, values, labels, dfx_file)
                        psspy.report("\n" + "=" * 80 + "\n\n")
                    elif etype in ("LII", "TR", "SYS"):
                        flow_codes = [0, 1, 2, 3] if ac_network else [0]
                        for flow_code in flow_codes:
                            flwopt = [elem["ibus"], elem["jbus"], 0, 1 if ac_network else 0, flow_code]
                            psspy.sensitivity_flow(flwopt, options, values, str(elem["ckt"]), labels, dfx_file)
                            psspy.report("\n" + "=" * 80 + "\n\n")
                    elif etype == "T3":
                        flow_codes = [0, 1, 2, 3] if ac_network else [0]
                        for flow_code in flow_codes:
                            flwopt = [elem["ibus"], elem["jbus"], elem["kbus"], 1 if ac_network else 0, flow_code]
                            psspy.sensitivity_flow(flwopt, options, values, str(elem["ckt"]), labels, dfx_file)
                            psspy.report("\n" + "=" * 80 + "\n\n")
            finally:
                psspy.t_report_output(6, "", [0, 0])


            if os.path.exists(case_report_txt):
                with open(case_report_txt, "r") as rf:
                    combined_report_lines.append(rf.read())
                case_tables = parse_sensitivity_report(case_report_txt)
                for key in keys:
                    df = case_tables[key]
                    if not df.empty:
                        df = df.copy()
                        df.insert(0, "CASO", base)
                        dfs[key].append(df)

        main_report_file = os.path.join(temp_dir, "sensitivity_report.txt")
        with open(main_report_file, "w") as f:
            f.write("\n".join(combined_report_lines))

        table_file = os.path.join(output_dir, "sensitivity_report.xlsx")
        any_data = any(dfs[k] for k in keys)
        if any_data:
            final_tables = {}
            for key in keys:
                if dfs[key]:
                    final_tables[key] = pd.concat(dfs[key], ignore_index=True)
                else:
                    final_tables[key] = pd.DataFrame(columns=["CASO"] + _EMPTY_TABLES[key])
            write_sensitivity_excel(final_tables, table_file)
        else:
            save_sensitivity_table(main_report_file, table_file)
        print("Sensitivity analysis completed. Results saved to: {}".format(table_file))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Calcula factores de distribucion y sensibilidad en PSS/E a partir de un archivo TSV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-c", "--cases",
        nargs="+",
        required=True,
        help="Rutas a los casos de trabajo (.sav)."
    )

    parser.add_argument(
        "-s", "--sub-file",
        dest="sub_file",
        default="estudio.sub",
        help="Ruta al archivo de subsistema (.sub)."
    )

    parser.add_argument(
        "-m", "--mon-file",
        dest="mon_file",
        default="estudio.mon",
        help="Ruta al archivo de monitoreados (.mon)."
    )

    parser.add_argument(
        "-n", "--con-file",
        dest="con_file",
        default="estudio.con",
        help="Ruta al archivo de contingencias (.con)."
    )

    parser.add_argument(
        "-e", "--elements-file",
        dest="elements_file",
        default="monitor.tsv",
        help="Ruta al archivo de elementos monitoreados (.tsv)."
    )

    parser.add_argument(
        "--source", "--source-subsystem",
        dest="source_subsystem",
        default="",
        help="Subsistema origen de las sensibilidades."
    )

    parser.add_argument(
        "--target", "--target-subsystem",
        dest="target_subsystem",
        default="",
        help="Subsistema destino de las sensibilidades (o 'Slack')."
    )

    parser.add_argument(
        "-o", "--output-dir",
        dest="output_dir",
        default=".",
        help="Directorio de destino de los resultados."
    )

    parser.add_argument(
        "-t", "--temp-dir",
        dest="temp_dir",
        default=".",
        help="Directorio de archivos temporales."
    )

    args = parser.parse_args()

    program = SensitivityProgram()
    program._run(
        cases=args.cases,
        sub_file=args.sub_file,
        mon_file=args.mon_file,
        con_file=args.con_file,
        elements_file=args.elements_file,
        source_subsystem=args.source_subsystem,
        target_subsystem=args.target_subsystem,
        output_dir=args.output_dir,
        temp_dir=args.temp_dir,
    )
