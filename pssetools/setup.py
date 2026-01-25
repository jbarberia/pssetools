import os
import shutil

# Crea carpetas de trabajo
os.makedirs("lib")
os.makedirs("log")
os.makedirs("build")
os.makedirs("results")

# Copia archivos basicos
package_dir = os.path.dirname(__file__)
templates_dir = os.path.join(package_dir, "template")

for filename in os.listdir(templates_dir):
    full_path = os.path.join(templates_dir, filename)
    
    if os.path.isfile(full_path):    
        shutil.copy2(
            full_path, 
            filename
        )

