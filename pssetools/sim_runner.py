"""Simulation runner for pssetools workspaces.

This module provides a unified interface for executing PSS/E simulations
(ACCC, ASCC, Dynamic) defined in YAML/JSON configuration files.

Usage:
    pssetools sim-runner                    # Execute default config.yaml
    pssetools sim-runner --config study.yml # Execute custom config
    pssetools sim-runner --interactive      # Interactive mode
    pssetools sim-runner --validate config.yml # Validate configuration only
"""

from __future__ import print_function
import os
import sys
import argparse
import subprocess
from datetime import datetime
from multiprocessing import Pool, Manager
import signal


class Colors:
    """ANSI color codes for terminal output."""
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print("\n" + Colors.BOLD + Colors.CYAN + "=" * 70 + Colors.RESET)
    print(Colors.BOLD + Colors.CYAN + text.center(70) + Colors.RESET)
    print(Colors.BOLD + Colors.CYAN + "=" * 70 + Colors.RESET + "\n")


def print_success(text):
    """Print success message."""
    print(Colors.GREEN + "[OK] " + text + Colors.RESET)


def print_info(text):
    """Print info message."""
    print(Colors.BLUE + "[*] " + text + Colors.RESET)


def print_warn(text):
    """Print warning message."""
    print(Colors.YELLOW + "[!] " + text + Colors.RESET)


def print_error(text):
    """Print error message."""
    print(Colors.RED + "[ERROR] " + text + Colors.RESET)


def load_yaml_safe(filename):
    """Load YAML file safely (compatible with Python 2.7).
    
    Tries PyYAML first, then falls back to JSON.
    
    Args:
        filename: Path to YAML/JSON file
        
    Returns:
        Dictionary with configuration or None on error
    """
    try:
        import yaml
        with open(filename, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback: Try JSON
        try:
            import json
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print_error("Failed to load config: {}".format(str(e)))
            return None
    except Exception as e:
        print_error("Failed to load config: {}".format(str(e)))
        return None


def validate_simulation_config(sim_config, sim_index):
    """Validate a single simulation configuration.
    
    Args:
        sim_config: Configuration dictionary for one simulation
        sim_index: Index of simulation in list
        
    Returns:
        (is_valid, error_message)
    """
    required_fields = ['name', 'type']
    for field in required_fields:
        if field not in sim_config:
            return False, "Simulation {} missing required field: {}".format(sim_index, field)
    
    sim_type = sim_config.get('type')
    if sim_type not in ['accc', 'ascc', 'dynamic', 'cnv', 'snp', 'dll', 'dfx', 'acc-pp']:
        return False, "Simulation {} has invalid type: {}".format(sim_index, sim_type)
    
    # Type-specific validation
    case_types = {'accc', 'ascc', 'dynamic', 'cnv', 'snp', 'dfx', 'acc-pp'}
    if sim_type in case_types and 'case' not in sim_config:
        return False, "Simulation {} ({}) requires 'case' field".format(sim_index, sim_type)
    
    return True, None


def validate_config(config):
    """Validate configuration file structure.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        (is_valid, errors_list)
    """
    errors = []
    
    if not config:
        errors.append("Configuration is empty")
        return False, errors
    
    if 'simulations' not in config:
        errors.append("Configuration must have 'simulations' section")
        return False, errors
    
    simulations = config.get('simulations', [])
    if not isinstance(simulations, list) or len(simulations) == 0:
        errors.append("'simulations' must be a non-empty list")
        return False, errors
    
    for i, sim in enumerate(simulations):
        valid, error = validate_simulation_config(sim, i)
        if not valid:
            errors.append(error)
    
    return len(errors) == 0, errors


def build_pssetools_command(sim_config):
    """Build pssetools CLI command for a simulation.
    
    Args:
        sim_config: Configuration dictionary for simulation
        
    Returns:
        List representing command arguments, or None if invalid
    """
    sim_type = sim_config.get('type')
    options = sim_config.get('options', {})
    
    cmd = ['python', '-m', 'pssetools', sim_type]
    
    # Add options dynamically
    for key, value in sorted(options.items()):
        cmd.append('--{}'.format(key))
        if isinstance(value, bool):
            if not value:
                cmd.pop()  # Remove flag if False
        else:
            cmd.append(str(value))
    
    return cmd


def execute_simulation(sim_config, workspace_dir=None, dry_run=False):
    """Execute a single simulation.
    
    Args:
        sim_config: Configuration dictionary for simulation
        workspace_dir: Working directory for execution
        dry_run: If True, show command but don't execute
        
    Returns:
        (success, output_message, sim_name)
    """
    sim_name = sim_config.get('name', 'unknown')
    
    try:
        cmd = build_pssetools_command(sim_config)
        if not cmd:
            return False, "Failed to build command for {}".format(sim_name), sim_name
        
        cmd_str = ' '.join(cmd)
        
        if dry_run:
            print_info("[DRY] {}: {}".format(sim_name, cmd_str))
            return True, "Dry run", sim_name
        
        # Execute command
        cwd = workspace_dir if workspace_dir and os.path.exists(workspace_dir) else None
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            return True, stdout.decode('utf-8', errors='ignore') if stdout else "", sim_name
        else:
            error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Unknown error"
            return False, error_msg, sim_name
            
    except Exception as e:
        return False, "Exception: {}".format(str(e)), sim_name


def _execute_simulation_wrapper(args):
    """Wrapper for parallel execution (multiprocessing compatibility)."""
    sim_config, workspace_dir, dry_run = args
    return execute_simulation(sim_config, workspace_dir, dry_run)


def run_simulations(config, workspace_dir=None, interactive=False, 
                   continue_on_error=False, dry_run=False):
    """Execute all simulations in configuration.
    
    Args:
        config: Configuration dictionary
        workspace_dir: Base directory for simulations
        interactive: If True, ask for confirmation before execution
        continue_on_error: If True, continue even if a simulation fails
        dry_run: If True, show commands but don't execute
        
    Returns:
        (total, successful, failed)
    """
    simulations = config.get('simulations', [])
    execution_opts = config.get('execution', {})
    
    if interactive is None:
        interactive = execution_opts.get('interactive', False)
    
    if continue_on_error is None:
        continue_on_error = execution_opts.get('continue_on_error', False)
    
    parallel_jobs = execution_opts.get('parallel', 1)
    if parallel_jobs < 1:
        parallel_jobs = 1
    
    total = len(simulations)
    successful = 0
    failed = 0
    
    print_info("Starting execution of {} simulation(s)".format(total))
    if parallel_jobs > 1:
        print_info("Parallel execution: {} jobs".format(parallel_jobs))
    if dry_run:
        print_warn("DRY RUN MODE - No commands will be executed")
    
    # Sequential execution with interactive option
    if interactive or parallel_jobs == 1:
        for i, sim in enumerate(simulations, 1):
            print("\n" + Colors.BOLD + "[{}/{}] {}".format(i, total, sim.get('name', 'Unknown')) + Colors.RESET)
            
            if interactive:
                try:
                    response = input("Execute this simulation? [y/n]: ").strip().lower()
                except:
                    response = raw_input("Execute this simulation? [y/n]: ").strip().lower()
                
                if response not in ['y', 'yes']:
                    print_warn("Skipped")
                    continue
            
            success, output, sim_name = execute_simulation(sim, workspace_dir, dry_run)
            
            if success:
                print_success("Completed: {}".format(sim_name))
                successful += 1
            else:
                failed += 1
                error_preview = output[:200] if output else "Unknown error"
                print_error("Failed: {}".format(error_preview))
                
                if not continue_on_error and not dry_run:
                    print_warn("Stopping execution (continue_on_error=false)")
                    break
    else:
        # Parallel execution
        try:
            pool = Pool(processes=parallel_jobs)
            tasks = [(sim, workspace_dir, dry_run) for sim in simulations]
            
            print_info("Queuing {} simulations on {} workers...".format(total, parallel_jobs))
            results = pool.map(_execute_simulation_wrapper, tasks)
            pool.close()
            pool.join()
            
            for i, (success, output, sim_name) in enumerate(results, 1):
                if success:
                    print_success("[{}/{}] Completed: {}".format(i, total, sim_name))
                    successful += 1
                else:
                    failed += 1
                    error_preview = output[:100] if output else "Unknown error"
                    print_error("[{}/{}] Failed {}: {}".format(i, total, sim_name, error_preview))
                    
                    if not continue_on_error and not dry_run:
                        print_warn("Stopping execution (continue_on_error=false)")
                        break
        except Exception as e:
            print_error("Parallel execution error: {}".format(str(e)))
            return total, 0, total
    
    return total, successful, failed


def show_config_summary(config):
    """Display configuration summary."""
    print_header("CONFIGURATION SUMMARY")
    
    workspace = config.get('workspace', {})
    print(Colors.BOLD + "Workspace:" + Colors.RESET)
    print("  Base directory: {}".format(workspace.get('base_dir', '.')))
    
    simulations = config.get('simulations', [])
    print("\n" + Colors.BOLD + "Simulations ({}):" + Colors.RESET.format(len(simulations)))
    
    for i, sim in enumerate(simulations, 1):
        sim_type = sim.get('type', 'unknown').upper()
        case = sim.get('case', 'N/A')
        print("  [{}] {} ({}) - {}".format(i, sim.get('name', 'Unknown'), sim_type, case))
    
    execution = config.get('execution', {})
    print("\n" + Colors.BOLD + "Execution Options:" + Colors.RESET)
    print("  Parallel jobs: {}".format(execution.get('parallel', 1)))
    print("  Continue on error: {}".format(execution.get('continue_on_error', False)))
    print("  Logging level: {}".format(execution.get('logging', 'normal')))


def main():
    """Main entry point for simulation runner command."""
    parser = argparse.ArgumentParser(
        prog='pssetools sim-runner',
        description='Execute PSS/E simulations from YAML/JSON configuration'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate configuration without executing'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Ask for confirmation before each simulation'
    )
    
    parser.add_argument(
        '--continue-on-error',
        action='store_true',
        help='Continue execution even if a simulation fails'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show commands but do not execute'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show configuration summary and exit'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if not os.path.exists(args.config):
        print_error("Configuration file not found: {}".format(args.config))
        return 1
    
    config = load_yaml_safe(args.config)
    if not config:
        return 1
    
    # Validate configuration
    valid, errors = validate_config(config)
    if not valid:
        print_error("Configuration validation failed:")
        for error in errors:
            print("  - {}".format(error))
        return 1
    
    print_success("Configuration valid")
    
    # Show summary
    if args.summary or args.validate:
        show_config_summary(config)
        if args.validate:
            return 0
    
    # Get workspace directory
    workspace_opts = config.get('workspace', {})
    base_dir = workspace_opts.get('base_dir', '.')
    
    if not os.path.isdir(base_dir):
        print_error("Workspace directory not found: {}".format(base_dir))
        return 1
    
    # Execute simulations
    print_header("STARTING SIMULATIONS")
    
    total, successful, failed = run_simulations(
        config,
        workspace_dir=base_dir,
        interactive=args.interactive,
        continue_on_error=args.continue_on_error,
        dry_run=args.dry_run
    )
    
    # Summary
    print_header("EXECUTION SUMMARY")
    print("Total simulations: {}".format(total))
    print_success("Successful: {}".format(successful))
    if failed > 0:
        print_error("Failed: {}".format(failed))
    
    print("\nCompleted at: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    return 0 if failed == 0 else 1


def run(**kwargs):
    """Entry point for pssetools CLI."""
    # Extraer argumentos desde kwargs pasados por CLI
    config_file = kwargs.get('config', 'config.yaml')
    validate = kwargs.get('validate', False)
    interactive = kwargs.get('interactive', False)
    continue_on_error = kwargs.get('continue_on_error', False)
    dry_run = kwargs.get('dry_run', False)
    summary = kwargs.get('summary', False)
    
    # Reconstruir sys.argv para main()
    sys.argv = ['pssetools sim-runner', '--config', config_file]
    
    if validate:
        sys.argv.append('--validate')
    if interactive:
        sys.argv.append('--interactive')
    if continue_on_error:
        sys.argv.append('--continue-on-error')
    if dry_run:
        sys.argv.append('--dry-run')
    if summary:
        sys.argv.append('--summary')
    
    return main()


if __name__ == '__main__':
    sys.exit(main())
