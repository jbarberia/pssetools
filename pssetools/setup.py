"""Asistente interactivo de configuración para proyectos pssetools.

Este módulo proporciona un asistente interactivo completo para crear
y modificar proyectos pssetools con estructura estándar.
"""

from __future__ import print_function
import os
import sys
import shutil


class Colores:
    """Códigos de color ANSI para terminal."""

    CYAN = '\033[96m'
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    RESET = '\033[0m'
    NEGRITA = '\033[1m'


def imprimir_encabezado(texto):
    """Imprime encabezado formateado."""
    print("\n" + Colores.NEGRITA + Colores.CYAN + "=" * 60 + Colores.RESET)
    print(Colores.NEGRITA + Colores.CYAN + texto.center(60) + Colores.RESET)
    print(Colores.NEGRITA + Colores.CYAN + "=" * 60 + Colores.RESET + "\n")


def imprimir_exito(texto):
    """Imprime mensaje de éxito."""
    print(Colores.VERDE + "[OK] " + texto + Colores.RESET)


def imprimir_info(texto):
    """Imprime mensaje informativo."""
    print(Colores.AZUL + "[*] " + texto + Colores.RESET)


try:
    _input = raw_input
except NameError:
    _input = input


def preguntar(texto):
    return _input(texto).strip()


def preguntar_si_no(texto, default=True):
    default_tag = "S/n" if default else "s/N"
    while True:
        resp = preguntar("{} [{}]: ".format(texto, default_tag)).lower()
        if not resp:
            return default
        if resp in ("s", "si", "y", "yes"):
            return True
        if resp in ("n", "no"):
            return False
        imprimir_info("Respuesta invalida. Use s/n.")


def preguntar_seleccion_multiple(titulo, opciones):
    """Fallback por si falla el selector interactivo."""
    imprimir_info(titulo)
    for i, item in enumerate(opciones, start=1):
        print("  {}. {}".format(i, item["label"]))
    while True:
        resp = preguntar("Ingrese numeros (ej: 1,3), 'all' para todos, o ENTER para ninguno: ").lower()
        if not resp:
            return []
        if resp in ("all", "*", "todos"):
            return [opt["key"] for opt in opciones]

        parts = [p.strip() for p in resp.split(",") if p.strip()]
        indices = []
        for p in parts:
            if p.isdigit():
                idx = int(p)
                if 1 <= idx <= len(opciones):
                    indices.append(idx - 1)
        return [opciones[i]["key"] for i in indices]


def obtener_template_path():
    """Localiza la carpeta template del paquete."""
    template_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/template'
    if not os.path.exists(template_base):
        try:
            import pkg_resources
            template_base = pkg_resources.resource_filename('pssetools', 'template')
        except:
            pass
    return template_base


def obtener_archivos_template(template_base):
    """Lista todos los archivos disponibles en el template."""
    archivos = []
    for root, dirs, files in os.walk(template_base):
        for f in files:
            if f.endswith((".pyc", ".pyo")):
                continue
            rel_path = os.path.relpath(os.path.join(root, f), template_base)
            # Normalizar para cross-platform
            rel_path = rel_path.replace("\\", "/")
            archivos.append(rel_path)
    return sorted(archivos)


def copiar_archivos_seleccionados(base_dir, template_base, lista_archivos):
    """Copia solo los archivos indicados, recreando estructura de carpetas."""
    imprimir_info("Copiando archivos seleccionados...")
    for rel_path in lista_archivos:
        src = os.path.join(template_base, rel_path)
        dst = os.path.join(base_dir, rel_path)

        # Crear carpeta destino si no existe
        dst_dir = os.path.dirname(dst)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        if os.path.exists(dst):
            imprimir_info("Ya existe (se omite): {}".format(rel_path))
            continue

        shutil.copy2(src, dst)
        imprimir_exito("Copiado: {}".format(rel_path))


def selector_interactivo(titulo, opciones, preseleccionadas=None):
    """Implementa una TUI interactiva con selección de cruces [x]."""
    if preseleccionadas is None:
        preseleccionadas = []
    
    seleccion = list(preseleccionadas)
    cursor = 0
    
    try:
        if os.name == 'nt':
            import msvcrt
            def getch():
                ch = msvcrt.getch()
                if ch in (b'\x00', b'\xe0'):
                    return ch + msvcrt.getch()
                return ch
        else:
            import tty, termios
            def getch():
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                    if ch == '\x1b':
                        ch += sys.stdin.read(2)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch
    except ImportError:
        return preguntar_seleccion_multiple(titulo, opciones)

    def redibujar():
        # Limpiar pantalla y mostrar lista
        sys.stdout.write("\033[H\033[J") 
        imprimir_encabezado(titulo)
        print("Use flechas o 'w/s' para navegar, ESPACIO para marcar, ENTER para finalizar.")
        print("-" * 60)
        for i, opt in enumerate(opciones):
            marca = "[x]" if opt["key"] in seleccion else "[ ]"
            prefijo = "> " if i == cursor else "  "
            color = Colores.CYAN if i == cursor else ""
            print("{}{}{} {}".format(prefijo, color, marca, opt["label"]) + Colores.RESET)
        print("-" * 60)
        sys.stdout.flush()

    while True:
        redibujar()
        key = getch()
        
        # ENTER
        if key in (b'\r', '\r', '\n'):
            break
        # ESPACIO
        elif key in (b' ', ' '):
            val = opciones[cursor]["key"]
            if val in seleccion:
                seleccion.remove(val)
            else:
                seleccion.append(val)
        # ARRIBA
        elif key in (b'w', 'w', b'\xe0H', '\x1b[A'):
            cursor = (cursor - 1) % len(opciones)
        # ABAJO
        elif key in (b's', 's', b'\xe0P', '\x1b[B'):
            cursor = (cursor + 1) % len(opciones)

    return seleccion


def run(**kwargs):
    """Ejecuta el asistente interactivo de setup."""
    base_dir = os.getcwd()
    template_base = obtener_template_path()

    if not os.path.exists(template_base):
        imprimir_info("Error: No se encontro la carpeta template.")
        return

    archivos_template = obtener_archivos_template(template_base)
    
    # 1. Configuración rápida para pre-selección
    imprimir_encabezado("PSSETOOLS SETUP")
    incluye_dinamicos = preguntar_si_no("¿El proyecto incluira simulaciones dinamicas?", default=True)
    incluye_docs = preguntar_si_no("¿Desea incluir la documentacion de referencia (docs/)?", default=False)
    
    preseleccion = []
    for f in archivos_template:
        if f.startswith("src/"):
            if "dyn_" in f or f.endswith(".idv"):
                if incluye_dinamicos:
                    preseleccion.append(f)
            else:
                preseleccion.append(f)
        elif f.startswith("docs/") and incluye_docs:
            preseleccion.append(f)
        elif f == "main.py":
            preseleccion.append(f)
        elif f == "compila.sh":
            preseleccion.append(f)

    # 2. Selector visual de archivos
    opciones_archivos = [{"key": f, "label": f} for f in archivos_template]
    archivos_seleccionados = selector_interactivo(
        "PERSONALIZAR ARCHIVOS DEL PROYECTO",
        opciones_archivos,
        preseleccionadas=preseleccion
    )

    # 3. Ejecutar acción
    if archivos_seleccionados:
        copiar_archivos_seleccionados(base_dir, template_base, archivos_seleccionados)
        imprimir_exito("Setup finalizado correctamente")
    else:
        imprimir_info("Operacion cancelada.")
