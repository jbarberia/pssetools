"""Initialization script for pssetools workspaces.

This script creates the standard directory structure (lib, log, build, results)
and copies template configuration and scripts from the package to the 
current working directory.
"""
from __future__ import print_function
import os
import shutil

def run(**kwargs):
    # Crea carpetas de trabajo
    folders = ["lib", "log", "build", "results"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print("Created folder: {}".format(folder))
        else:
            print("Folder already exists: {}".format(folder))

    # Copia archivos basicos
    package_dir = os.path.dirname(__file__)
    templates_dir = os.path.join(package_dir, "template")

    if not os.path.exists(templates_dir):
        print("Error: Templates directory not found at {}".format(templates_dir))
        return

    for filename in os.listdir(templates_dir):
        full_path = os.path.join(templates_dir, filename)
        
        if os.path.isfile(full_path):
            if not os.path.exists(filename):
                shutil.copy2(
                    full_path, 
                    filename
                )
                print("Copied template: {}".format(filename))
            else:
                print("File already exists, skipping: {}".format(filename))

if __name__ == "__main__":
    run()

