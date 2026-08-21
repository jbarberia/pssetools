# Guía de Contribución para pssetools

Gracias por tu interés en contribuir a **pssetools**. El objetivo de este proyecto es construir una suite estandarizada y fácil de usar.

## 🐛 Reportar Errores o Solicitar Mejoras

Si encuentras un error o tienes una idea para mejorar la herramienta, abre un **Issue** en GitHub. Por favor incluye:
* Versión de PSS®E (ej. v34, v36).
* Versión de Python.
* El mensaje de error completo (Traceback).
* Pasos para reproducir el problema.

## 💻 ¿Cómo crear un nuevo módulo (Programa)?

La gran ventaja de esta arquitectura es que **no necesitas modificar la interfaz gráfica** para añadir una nueva herramienta. Solo tienes que crear un archivo en el directorio de programas siguiendo la nomenclatura `XX_nombre.py`.

Tu clase debe heredar de `BaseProgram` y definir dos métodos fundamentales: `get_parameters()` y `run()`.

### Plantilla Básica:

```python
# coding: latin-1
"""
Nombre de la Herramienta
------------------------
Documentación que aparecerá en el panel lateral de la GUI. Explica
qué hace este script y qué parámetros necesita.
"""
from pssegui.programs import BaseProgram

class MiNuevoPrograma(BaseProgram):
    
    def get_parameters(self):
        """Define los campos que aparecerán en la GUI."""
        return [
            {
                "name": "case",               # Nombre de la variable
                "label": "Caso base (.sav):", # Texto en la GUI
                "type": "file",               # Tipo (file, multi_file, bool, etc.)
                "default": "",
                "editable": True
            },
            {
                "name": "do_something",
                "label": "Aplicar corrección",
                "type": "bool",
                "default": True
            }
        ]

    def run(self, parsed_params):
        """Punto de entrada cuando se presiona 'Run'."""
        self.logica_principal(**parsed_params)

    def logica_principal(self, case, do_something, output_dir=".", temp_dir="."):
        # Inicialización de PSS/E
        psspy = self.psspy
        psspy.psseinit()
        
        # Cargar caso
        ierr = psspy.case(case)
        if ierr != 0:
            print("Error cargando el caso.")
            return
            
        # ... Tu lógica aquí ...
        print(f"Ejecutando en {output_dir}")

```
