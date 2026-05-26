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


def copiar_template_completo(base_dir, template_base):
    """Copia el template completo con estructura prearmada."""
    imprimir_info("Copiando estructura de proyecto...")
    ignore_patterns = shutil.ignore_patterns("*.pyc", "*.pyo", "__pycache__")

    for item in os.listdir(template_base):
        src = os.path.join(template_base, item)
        dst = os.path.join(base_dir, item)

        # Skip if already exists
        if os.path.exists(dst):
            imprimir_info("Ya existe: {}".format(item))
            continue

        # Copy directories
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=ignore_patterns)
            imprimir_exito("Carpeta: {}".format(item))
        # Copy files
        elif os.path.isfile(src):
            shutil.copy2(src, dst)
            imprimir_exito("Archivo: {}".format(item))


def run(**kwargs):
    """Ejecuta el asistente interactivo."""
    imprimir_encabezado("PSSETOOLS")

    base_dir = os.getcwd()
    template_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/template'

    if not os.path.exists(template_base):
        import pkg_resources

        template_base = pkg_resources.resource_filename('pssetools', 'template')
        copiar_template_completo(base_dir, template_base)
