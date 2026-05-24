"""Initialization script for pssetools workspaces.

This script delegates to the interactive setup wizard (setup_wizard.py)
which guides users through creating a standard workspace structure.
"""

from __future__ import print_function
import sys

try:
    from . import setup_wizard
except ImportError:
    import setup_wizard


def run(**kwargs):
    """Run the interactive setup wizard."""
    return setup_wizard.run_wizard()


if __name__ == "__main__":
    try:
        success = run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nSetup cancelled by user.")
        sys.exit(1)
