"""Interactive setup wizard for pssetools workspaces.

This wizard guides users through creating a standard pssetools project structure
and selectively copying templates based on their analysis needs.
"""

from __future__ import print_function
import os
import sys
import shutil


class Colors:
    """ANSI color codes for terminal output."""
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print("\n" + Colors.BOLD + Colors.CYAN + "=" * 60 + Colors.RESET)
    print(Colors.BOLD + Colors.CYAN + text.center(60) + Colors.RESET)
    print(Colors.BOLD + Colors.CYAN + "=" * 60 + Colors.RESET + "\n")


def print_success(text):
    """Print success message."""
    print(Colors.GREEN + "[OK] " + text + Colors.RESET)


def print_info(text):
    """Print info message."""
    print(Colors.BLUE + "[*] " + text + Colors.RESET)


def print_warn(text):
    """Print warning message."""
    print(Colors.YELLOW + "[!] " + text + Colors.RESET)


def prompt_choice(question, choices):
    """Prompt user to select from multiple choices.
    
    Args:
        question: Question to display
        choices: List of tuples (key, description)
    
    Returns:
        Selected key or None if cancelled
    """
    print(Colors.BOLD + question + Colors.RESET)
    for key, desc in choices:
        print("  [{}] {}".format(key, desc))
    
    while True:
        answer = input("\nYour choice [{}]: ".format("/".join([c[0] for c in choices]))).strip()
        if answer in [c[0] for c in choices]:
            return answer
        print_warn("Invalid choice. Please try again.")


def prompt_yes_no(question):
    """Prompt user for yes/no answer.
    
    Args:
        question: Question to display
    
    Returns:
        True if yes, False if no
    """
    while True:
        answer = input(Colors.BOLD + question + Colors.RESET + " [y/n]: ").strip().lower()
        if answer in ['y', 'yes']:
            return True
        elif answer in ['n', 'no']:
            return False
        print_warn("Please answer 'y' or 'n'")


def create_workspace_structure():
    """Create standard workspace directories."""
    print_info("Creating workspace structure...")
    
    folders = ["lib", "log", "build", "results"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print_success("Created folder: {}".format(folder))
        else:
            print_warn("Folder already exists: {}".format(folder))


def get_template_base_dir():
    """Get the template directory path."""
    package_dir = os.path.dirname(__file__)
    return os.path.join(package_dir, "template")


def copy_essential_templates():
    """Copy essential configuration files."""
    print_info("Copying essential configuration files...")
    
    template_base = get_template_base_dir()
    essential_dir = os.path.join(template_base, "essential")
    
    if not os.path.exists(essential_dir):
        print_warn("Essential templates directory not found")
        return False
    
    essential_files = [
        "config.cfg",
        "estudio.sub",
        "estudio.mon",
        "estudio.con",
        "estudio.idv"
    ]
    
    copied = 0
    for filename in essential_files:
        src = os.path.join(essential_dir, filename)
        dst = filename
        
        if os.path.exists(src):
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                print_success("Copied: {}".format(filename))
                copied += 1
            else:
                print_warn("File already exists: {}".format(filename))
        else:
            print_warn("Template not found: {}".format(filename))
    
    return copied > 0


def copy_optional_templates(include_scripts=False, include_examples=False, include_docs=False):
    """Copy optional templates based on user selection.
    
    Args:
        include_scripts: Whether to copy script templates
        include_examples: Whether to copy example Python scripts
        include_docs: Whether to copy documentation reference files
    """
    template_base = get_template_base_dir()
    
    if include_scripts:
        print_info("Copying script templates...")
        scripts_dir = os.path.join(template_base, "optional", "scripts")
        if os.path.exists(scripts_dir):
            for filename in os.listdir(scripts_dir):
                src = os.path.join(scripts_dir, filename)
                dst = filename
                if os.path.isfile(src) and not os.path.exists(dst):
                    shutil.copy2(src, dst)
                    print_success("Copied: {}".format(filename))
    
    if include_examples:
        print_info("Copying example Python scripts...")
        examples_dir = os.path.join(template_base, "optional", "examples")
        if os.path.exists(examples_dir):
            for filename in os.listdir(examples_dir):
                if filename.endswith(".py"):
                    src = os.path.join(examples_dir, filename)
                    dst = filename
                    if not os.path.exists(dst):
                        shutil.copy2(src, dst)
                        print_success("Copied: {}".format(filename))
    
    if include_docs:
        print_info("Copying documentation reference files...")
        docs_src = os.path.join(template_base, "docs")
        docs_dst = "docs"
        
        if os.path.exists(docs_src):
            if not os.path.exists(docs_dst):
                shutil.copytree(docs_src, docs_dst)
                print_success("Copied docs/ directory")
            else:
                print_warn("docs/ directory already exists")


def show_summary():
    """Show summary of created structure."""
    print("\n" + Colors.BOLD + Colors.GREEN + "=" * 60 + Colors.RESET)
    print(Colors.BOLD + Colors.GREEN + "Workspace Setup Complete!".center(60) + Colors.RESET)
    print(Colors.BOLD + Colors.GREEN + "=" * 60 + Colors.RESET)
    
    print("\n" + Colors.BOLD + "Workspace structure:" + Colors.RESET)
    structure = {
        "lib/": "Store compiled DLLs and libraries",
        "log/": "Activity logs and progress files",
        "build/": "Temporary files (DFX, ACC, CNV, SNP)",
        "results/": "Final reports and simulation output",
        "config.cfg": "Configuration for ACCC, ASCC, etc.",
        "estudio.sub/mon/con/idv": "PSS/E configuration files",
    }
    
    for item, description in structure.items():
        print("  {:<20} {}".format(Colors.BOLD + item + Colors.RESET, description))
    
    print("\n" + Colors.BOLD + "Next steps:" + Colors.RESET)
    print("  1. Copy your PSS/E case files (*.sav, *.dyr) here")
    print("  2. Edit estudio.sub/mon/con to define your study")
    print("  3. Run: " + Colors.BOLD + "pssetools --help" + Colors.RESET)
    print("  4. Try: " + Colors.BOLD + "pssetools acc --help" + Colors.RESET)
    
    print("\n" + Colors.BOLD + "Documentation:" + Colors.RESET)
    print("  Configuration guide: Check GEMINI.md or config.cfg")
    print("  API reference: See docs/ folder (if copied)")
    print("\n")


def run_wizard():
    """Run the interactive setup wizard."""
    print_header("PSS/E Tools - Workspace Setup Wizard")
    
    print("This wizard will create a standard pssetools workspace structure")
    print("and copy templates based on your analysis needs.\n")
    
    # Step 1: Create workspace structure
    create_workspace_structure()
    
    # Step 2: Copy essential files
    if not copy_essential_templates():
        print_warn("Failed to copy essential templates")
        return False
    
    # Step 3: Ask about analysis types
    print("\n" + Colors.BOLD + "What types of studies will you run?" + Colors.RESET)
    
    studies = prompt_choice(
        "Select your primary analysis type:",
        [
            ("1", "ACCC (Contingency Analysis)"),
            ("2", "ASCC (Short Circuit Analysis)"),
            ("3", "Dynamic Simulation"),
            ("4", "All of the above"),
            ("5", "Just essentials (decide later)"),
        ]
    )
    
    # Step 4: Ask about optional components
    print("\n" + Colors.BOLD + "Additional options:" + Colors.RESET)
    
    include_scripts = False
    include_examples = False
    include_docs = False
    
    if studies in ["3", "4"]:
        include_examples = prompt_yes_no(
            "Include example dynamic simulation scripts (dyn_1ph.py, dyn_3ph.py, convload.py)?"
        )
    
    include_scripts = prompt_yes_no(
        "Include automation scripts (script.sh for Linux/Mac, script.ps1 for Windows)?"
    )
    
    include_docs = prompt_yes_no(
        "Include PSS/E API reference documentation files?"
    )
    
    # Step 5: Copy optional templates
    copy_optional_templates(include_scripts, include_examples, include_docs)
    
    # Step 6: Show summary
    show_summary()
    
    return True


if __name__ == "__main__":
    try:
        success = run_wizard()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n" + Colors.YELLOW + "Setup cancelled by user." + Colors.RESET)
        sys.exit(1)
    except Exception as e:
        print("\n" + Colors.RED + "Error: {}".format(str(e)) + Colors.RESET)
        sys.exit(1)
