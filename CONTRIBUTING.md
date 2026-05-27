# Contribuyendo a pssetools

## Configuración del Desarrollador
1. **Clonar e instalar:**
   ```bash
   git clone https://github.com/User/pssetools.git
   cd pssetools   
   ```
2. **Estándar:** Utiliza Python 2.7 (compatible con PSS/E 34).
3. **Docstrings:** Todas las funciones nuevas deben seguir el **estilo de Google**.

## Añadir una Nueva Actividad
Para añadir una nueva actividad de PSS/E (ej: OPF, GIC):

1. **Crear un nuevo módulo:** en `pssetools/` (ej: `pssetools/opf.py`).
2. **Usar el decorador `@pss_activity`:** 
   El decorador `pssetools.pss_activity` gestiona tareas comunes:
   - Carga automáticamente el caso `.sav` o `.cnv` antes de que se ejecute la función.
   - Captura excepciones y asegura que la salida de PSS/E se redirija de nuevo a la pantalla si fue capturada.
   - Verifica el código de retorno de la actividad y lanza una excepción en caso de fallo (si el valor de retorno es un entero distinto de cero).

   ```python
   from pssetools import pss_activity
   import psspy

   @pss_activity
   def run(sav, output_file, **kwargs):
       ierr = psspy.my_psse_activity(output_file)
       return ierr
   ```

3. **Registrar en la CLI:** Añade el comando al parser en `pssetools/cli.py`.
4. **Actualizar Configuración:** Añade parámetros de configuración por defecto a `pssetools/config.cfg` si la actividad requiere ajustes específicos.

## Manejo de Configuración
Utiliza siempre `pssetools.get_config()` para obtener los ajustes. Esto asegura que los archivos de configuración proporcionados por el usuario (vía `--config`) se fusionen correctamente con los valores por defecto del sistema.

## Reportar Problemas
Por favor, utiliza el rastreador de problemas (Issues) de GitHub para informar errores o solicitar nuevas funcionalidades.
