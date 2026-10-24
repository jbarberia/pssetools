# Guía de Usuario

Esta guía detalla el uso de la interfaz gráfica de `pssetools` para automatizar tareas en PSS®E.

## 🖥️ La Interfaz Principal

Al ejecutar `pssetools.gui()`, se abre una ventana dividida en tres secciones principales:

### 1. Panel de Programas (Izquierda)
Contiene la lista de todos los scripts disponibles en la carpeta `pssetools/programs/`. Al seleccionar un programa, la interfaz carga automáticamente su documentación y sus parámetros.

### 2. Panel de Configuración (Derecha)
- **Documentación**: Muestra una descripción breve de qué hace el programa seleccionado y cómo deben configurarse sus parámetros.
- **Parámetros**: Formulario dinámico donde puedes ingresar rutas de archivos, activar opciones booleanas o seleccionar múltiples archivos.
- **Botón Run**: Ejecuta el programa seleccionado con los parámetros actuales.

### 3. Barra de Estado (Inferior)
Muestra el **CWD (Current Working Directory)** actual de PSS®E, permitiéndote verificar en qué carpeta está operando la consola de Siemens.

## ⚙️ Gestión de Configuración

Para evitar reingresar los mismos parámetros en cada sesión, la herramienta ofrece:

- **Guardar/Cargar Configuración**: Permite exportar todos los parámetros actuales a un archivo `.json` y recuperarlos posteriormente (`File > Save/Load Configuration`).
- **Exportar como .BAT**: Si necesitas ejecutar un proceso fuera de la GUI, puedes exportar la configuración actual como un archivo ejecutable de Windows (`.bat`) que llama al script de Python con los argumentos correspondientes.

## 📂 Configuración de Rutas (Workspace)
A través del menú `Paths > Configure Paths...`, puedes definir:
- **Working Directory**: Carpeta base de operación.
- **Output Directory**: Donde se guardarán los resultados finales.
- **Temp Directory**: Carpeta para archivos temporales y reportes intermedios.
