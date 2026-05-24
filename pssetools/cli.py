from __future__ import print_function
import argparse
import sys
import os
from . import acc, ascc, cnv, dfx, dyn, snp, dll, acc_pp, acc_unzip, runner, setup, sim_runner

def app():
    """Main entry point for the pssetools CLI.

    Defines the command-line interface, including subparsers for various
    PSS/E activities (acc, ascc, cnv, dfx, dyn, snp, dll, runner),
    handles file auto-assignment by extension, and dispatches the
    execution to the appropriate module.
    """
    # Common arguments for most activities
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--sav", type=str, help="PSS/E Case (.sav)")
    parent_parser.add_argument("--config", type=str, help="Configuration file (.cfg)")

    parser = argparse.ArgumentParser(
        prog="pssetools", 
        description="PSS/E Tools CLI - Centralized access to PSS/E activities"
    )
    
    # Python 2.7 subparsers doesn't support 'required=True'
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Helper to add positional files to each subparser
    def add_files_arg(p):
        p.add_argument("files", nargs="*", help="Auto-assign files by extension (.sav, .dyr, .acc, etc.)")

    # acc
    acc_p = subparsers.add_parser("acc", parents=[parent_parser], help="ACCC Contingency Analysis")
    acc_p.add_argument("--acc", type=str, help="Output .acc file")
    acc_p.add_argument("--dfx", type=str, help="Input .dfx file")
    acc_p.add_argument("--zipfile", type=str, help="Report .zip file")
    add_files_arg(acc_p)

    # acc-pp
    acc_pp_p = subparsers.add_parser("acc-pp", parents=[parent_parser], help="ACCC Post-processing")
    acc_pp_p.add_argument("--acc", type=str, help="Input .acc file")
    acc_pp_p.add_argument("--frp", type=str, help="Output flow report (.frp)")
    acc_pp_p.add_argument("--vrp", type=str, help="Output voltage report (.vrp)")
    add_files_arg(acc_pp_p)

    # acc-unzip
    acc_zip_p = subparsers.add_parser("acc-unzip", parents=[parent_parser], help="ACCC Unzip tool")
    acc_zip_p.add_argument("--zipfile", type=str, help="Input .zip file")
    acc_zip_p.add_argument("--folder", type=str, help="Output folder")
    add_files_arg(acc_zip_p)

    # ascc
    ascc_p = subparsers.add_parser("ascc", parents=[parent_parser], help="ASCC Short Circuit Analysis")
    ascc_p.add_argument("--sub", type=str, help="Input .sub file")
    ascc_p.add_argument("--report", type=str, help="Output report file")
    add_files_arg(ascc_p)

    # cnv
    cnv_p = subparsers.add_parser("cnv", parents=[parent_parser], help="Convert to snapshot/dynamic case")
    cnv_p.add_argument("--cnv", type=str, help="Output .cnv file")
    cnv_p.add_argument("--py", nargs="*", type=str, help="Input .py scripts")
    add_files_arg(cnv_p)

    # dfx
    dfx_p = subparsers.add_parser("dfx", parents=[parent_parser], help="Build Distribution Factors")
    dfx_p.add_argument("--sub", type=str, help="Input .sub file")
    dfx_p.add_argument("--mon", type=str, help="Input .mon file")
    dfx_p.add_argument("--con", type=str, help="Input .con file")
    dfx_p.add_argument("--dfx", type=str, help="Output .dfx file")
    add_files_arg(dfx_p)

    # dyn
    dyn_p = subparsers.add_parser("dyn", help="Run Dynamic Simulation")
    dyn_p.add_argument("--cnv", type=str, help="Input .cnv file")
    dyn_p.add_argument("--out", type=str, help="Output .out file")
    dyn_p.add_argument("--snp", type=str, help="Input .snp file")
    dyn_p.add_argument("--dll", nargs="*", type=str, help="User model DLLs")
    dyn_p.add_argument("--py", type=str, help="Input .py script")
    dyn_p.add_argument("--no-debug", dest="no_debug", action="store_true", default=False, help="Disable debug output")
    add_files_arg(dyn_p)

    # snp
    snp_p = subparsers.add_parser("snp", parents=[parent_parser], help="Create Snapshot")
    snp_p.add_argument("--snp", type=str, help="Output .snp file")
    snp_p.add_argument("--cc", type=str, help="Input .flx (CONEC) file")
    snp_p.add_argument("--ct", type=str, help="Input .flx (CONET) file")
    snp_p.add_argument("--idv", type=str, help="Response file with channels/options")
    snp_p.add_argument("--dyr", nargs="*", type=str, help="Input .dyr files")
    add_files_arg(snp_p)

    # dll
    dll_p = subparsers.add_parser("dll", help="Build User DLL")
    dll_p.add_argument("--dll", type=str, help="Output .dll file")
    dll_p.add_argument("--sources", nargs="*", type=str, help="Source files")
    dll_p.add_argument("--config", nargs="*", type=str, default=None, help="Source files")
    add_files_arg(dll_p)

    # runner
    runner_p = subparsers.add_parser("runner", parents=[parent_parser], help="Run custom script")
    runner_p.add_argument("--script", type=str, help="Python script to run")
    runner_p.add_argument("--report", type=str, help="Output report file")
    add_files_arg(runner_p)

    # setup
    setup_p = subparsers.add_parser("setup", help="Initialize workspace with templates and folders")

    # sim-runner (simulation runner with YAML config)
    simrunner_p = subparsers.add_parser("sim-runner", help="Execute simulations from YAML/JSON configuration")
    simrunner_p.add_argument("--config", type=str, default="config.yaml", help="Configuration file (default: config.yaml)")
    simrunner_p.add_argument("--validate", action="store_true", help="Validate configuration without executing")
    simrunner_p.add_argument("--interactive", action="store_true", help="Ask for confirmation before each simulation")
    simrunner_p.add_argument("--continue-on-error", action="store_true", help="Continue even if simulation fails")
    simrunner_p.add_argument("--dry-run", action="store_true", help="Show commands but do not execute")
    simrunner_p.add_argument("--summary", action="store_true", help="Show configuration summary and exit")

    # Show help if no subcommand is provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    cmd = args.command
    cmd_args = vars(args)
    files = cmd_args.pop("files", [])

    # Show subcommand help if no arguments provided (and no files)
    # Exclude booleans and 'command' itself
    if cmd != 'setup' and not any([v for k, v in cmd_args.items() if k != 'command' and v is not None and v is not False and not (isinstance(v, list) and len(v) == 0)]) and not files:
        # Find the subparser to print its help
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                if cmd in action.choices:
                    action.choices[cmd].print_help()
                    sys.exit(0)

    # Auto-assignment logic
    extension_map = {
        ".sav": "sav",
        ".acc": "acc",
        ".dfx": "dfx",
        ".zip": "zipfile",
        ".sub": "sub",
        ".mon": "mon",
        ".con": "con",
        ".dyr": "dyr",
        ".snp": "snp",
        ".cnv": "cnv",
        ".out": "out",
        ".cfg": "config",
        ".scf": "report",
        ".flx": "cc",
    }
    
    for f in files:
        _, ext = os.path.splitext(f.lower())
        arg_name = extension_map.get(ext)
        
        # Handle .py ambiguity
        if ext == ".py":
            if cmd == "cnv": arg_name = "py"
            elif cmd == "dyn": arg_name = "py"
            elif cmd in ("runner", "run"): arg_name = "script"

        # Handle .flx in snp (cc and ct)
        if ext == ".flx" and cmd == "snp":
            if cmd_args.get("cc") is None: arg_name = "cc"
            else: arg_name = "ct"

        if arg_name and arg_name in cmd_args:
            if isinstance(cmd_args[arg_name], list):
                cmd_args[arg_name].append(f)
            elif cmd_args[arg_name] is None:
                cmd_args[arg_name] = f
    
    # Dispatch
    modules = {
        "acc": acc,
        "acc-pp": acc_pp,
        "acc-unzip": acc_unzip,
        "ascc": ascc,
        "cnv": cnv,
        "dfx": dfx,
        "dyn": dyn,
        "snp": snp,
        "dll": dll,
        "runner": runner,
        "sim-runner": sim_runner,
        "setup": setup
    }
    
    if cmd in modules:
        modules[cmd].run(**cmd_args)

if __name__ == "__main__":
    app()
