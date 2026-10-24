# Guía de Desarrollo (API)

`pssetools` está diseñado para ser extensible. Puedes añadir nuevos programas de automatización siguiendo el patrón de diseño de la suite.

## 🛠️ Cómo añadir un nuevo Programa

Para agregar una nueva funcionalidad, crea un archivo `.py` en la carpeta `pssetools/programs/`.

### Requisitos del Script
El programa debe seguir estas convenciones para ser descubierto dinámicamente por la GUI:

1. **Herencia**: La clase principal debe heredar de `BaseProgram`.
2. **Definición de Parámetros**: El script debe definir una lista de parámetros que la GUI convertirá en campos de entrada. Cada parámetro debe tener:
   - `label`: Nombre visible en la interfaz.
   - `type`: Tipo de dato (`file`, `save`, `bool`, `multi_file`, `text`).
   - `default`: Valor predeterminado.
3. **Método `run`**: Debe implementar el método `run(self, params)`, donde `params` es un diccionario con los valores ingresados en la GUI.

### Ejemplo de estructura
```python
from pssetools.programs.base import BaseProgram

class MiNuevoPrograma(BaseProgram):
    def get_parameters(self):
        return [
            {"name": "input_file", "label": "Archivo de Entrada", "type": "file", "default": "input.sav"},
            {"name": "do_export", "label": "Exportar a Excel", "type": "bool", "default": True}
        ]

    def run(self, params):
        # Lógica de automatización de PSS®E aquí
        print("Ejecutando con: " + params['input_file'])
```

## 📦 Utilidades Disponibles
Puedes aprovechar las funciones en `pssetools/utils/` para:
- Procesar DataFrames de PSS®E.
- Gestionar la descompresión de archivos ACCC.
- Corregir archivos PDF generados por PSS®E.
