"""Asistente interactivo de configuración para proyectos pssetools."""

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


def imprimir_advertencia(texto):
    """Imprime mensaje de advertencia."""
    print(Colores.AMARILLO + "[!] " + texto + Colores.RESET)


def pregunta_opcion(pregunta, opciones):
    """Solicita al usuario seleccionar de varias opciones."""
    print(Colores.NEGRITA + pregunta + Colores.RESET)
    for clave, desc in opciones:
        print("  {}) {}".format(clave, desc))
    
    while True:
        respuesta = raw_input("Tu elección: ").strip() if sys.version_info[0] < 3 else input("Tu elección: ").strip()
        for clave, _ in opciones:
            if str(respuesta) == str(clave):
                return clave
        imprimir_advertencia("Opción no válida. Intenta de nuevo.")


def pregunta_si_no(pregunta):
    """Pregunta sí/no y retorna booleano."""
    while True:
        prompt = Colores.NEGRITA + pregunta + " (s/n): " + Colores.RESET
        respuesta = raw_input(prompt).strip().lower() if sys.version_info[0] < 3 else input(prompt).strip().lower()
        if respuesta in ('s', 'y', 'si', 'yes'):
            return True
        elif respuesta in ('n', 'no'):
            return False
        imprimir_advertencia("Respuesta no válida. Escribe 's' o 'n'.")


def crear_carpetas(base_dir):
    """Crea estructura de carpetas estándar."""
    carpetas = ['lib', 'log', 'build', 'results', 'casos', 'templates']
    
    for carpeta in carpetas:
        ruta = os.path.join(base_dir, carpeta)
        if not os.path.exists(ruta):
            os.makedirs(ruta)
            imprimir_exito("Carpeta creada: {}".format(carpeta))
        else:
            imprimir_info("Carpeta ya existe: {}".format(carpeta))


def crear_templates_basicos(base_dir, tipos_analisis):
    """Crea archivo de configuración único (NO templates ACCC.* innecesarios)."""
    templates_dir = os.path.join(base_dir, 'templates')
    
    # Solo crear config.yml unificado - SIN templates genéricos ACCC.sub, etc
    imprimir_info("Generando configuración unificada...")
    
    config_content = '''# Configuración Unificada - pssetools
# Descomentar los estudios que quieras ejecutar
# Uso: pssetools sim-runner --config config.yml

workspace:
  base_dir: "."

simulations:
  # ===== ESTUDIOS ESTÁTICOS =====
  # ACCC (Contingency Analysis)
  - name: "ACCC_CasoBase"
    type: "accc"
    case: "casos/caso_base.sav"
    options:
      sub: "estudio.sub"
      mon: "estudio.mon"
      con: "estudio.con"
      dfx: "build/caso_base.dfx"
      acc: "build/caso_base.acc"
      zipfile: "build/caso_base.zip"

  # ASCC (Short Circuit)
  - name: "ASCC_CasoBase"
    type: "ascc"
    case: "casos/caso_base.sav"
    options:
      sub: "estudio.sub"
      asc: "build/caso_base.asc"
      dfx: "build/caso_base_ascc.dfx"

  # ===== SIMULACIÓN DINÁMICA =====
  # Conversión de caso (conversion)
  - name: "CNV_Snapshot"
    type: "cnv"
    case: "casos/caso_base.sav"
    options:
      cnv: "build/caso_base.cnv"
      py: "lib/convload.py"

  # Snapshot para simulación dinámica
  - name: "SNP_Build"
    type: "snp"
    case: "casos/caso_base.sav"
    options:
      snp: "build/snapshot.snp"
      dyr: "estudio.dyr"
      idv: "estudio.idv"

  # Simulación dinámica transient stability
  - name: "DYN_Transient"
    type: "dyn"
    case: "casos/caso_base.sav"
    options:
      cnv: "build/caso_base.cnv"
      snp: "build/snapshot.snp"
      out: "build/resultado_dyn.out"
      outx: "build/resultado_dyn.outx"

execution:
  # Ejecutar en paralelo (1=secuencial, 2-4=paralelo típico)
  parallel: 1
  continue_on_error: false
  logging: "normal"
  interactive: false

# INSTRUCCIONES DE USO:
# 1. Descomentar los estudios que quieras ejecutar
# 2. Editar rutas de archivos (.sav, .sub, .mon, .con, etc.)
# 3. Validar: pssetools sim-runner --config config.yml --validate
# 4. Ejecutar: pssetools sim-runner --config config.yml
'''
    
    ruta = os.path.join(templates_dir, 'config.yml')
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(config_content)
    imprimir_exito("Configuración única: config.yml")



def copiar_archivos_esenciales(base_dir, template_base):
    """Copia archivos esenciales."""
    esenciales = ['config.cfg', 'estudio.sub', 'estudio.mon', 'estudio.con', 'estudio.idv']
    
    imprimir_info("Copiando archivos esenciales...")
    
    for archivo in esenciales:
        src = os.path.join(template_base, 'essential', archivo)
        dst = os.path.join(base_dir, archivo)
        
        if os.path.exists(src):
            shutil.copy2(src, dst)
            imprimir_exito("Copiado: {}".format(archivo))


def copiar_ejemplos(base_dir, template_base):
    """Copia ejemplos a lib/ - organizados por tipo de simulación."""
    ejemplos_dir = os.path.join(template_base, 'optional', 'examples')
    
    if not os.path.exists(ejemplos_dir):
        return
    
    if pregunta_si_no("¿Incluir scripts de ejemplo (Dynamic)?"):
        lib_dir = os.path.join(base_dir, 'lib')
        
        # Scripts que van a lib/ (dinámico + convload.py)
        scripts_lib = ['convload.py', 'dyn_1ph.py', 'dyn_3ph.py']
        
        for archivo in scripts_lib:
            src = os.path.join(ejemplos_dir, archivo)
            dst = os.path.join(lib_dir, archivo)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                imprimir_exito("Script: {}".format(archivo))


def crear_proyecto_nuevo(base_dir, template_base):
    """Crea un proyecto nuevo."""
    imprimir_encabezado("CREAR PROYECTO NUEVO")
    
    # Ya no preguntamos qué análisis - dejamos que el usuario comente/descomente en config.yml
    imprimir_info("Se creará estructura con configuración única (config.yml)")
    imprimir_info("El usuario puede descomentar los estudios que desee ejecutar")
    
    imprimir_info("Creando estructura...")
    crear_carpetas(base_dir)
    copiar_archivos_esenciales(base_dir, template_base)
    crear_templates_basicos(base_dir, {'ACCC', 'ASCC', 'DYN'})
    copiar_ejemplos(base_dir, template_base)
    
    imprimir_encabezado("PROYECTO CREADO!")
    print("Ubicación: {}\n".format(base_dir))
    print("Estructura de carpetas:")
    print("  lib/        - Scripts Python (convload.py, dyn_*.py) y DLLs de modelos")
    print("  templates/  - config.yml (configuración única)")
    print("  build/      - Archivos intermedios (.dfx, .cnv, .snp)")
    print("  results/    - Reportes y resultados (.acc, .asc, .out)")
    print("  casos/      - Archivos .sav\n")
    print("Archivos principales:")
    print("  config.cfg       - Configuración general")
    print("  estudio.sub      - Subsistema")
    print("  estudio.mon      - Puntos de monitoreo")
    print("  estudio.con      - Contingencias")
    print("  estudio.idv      - Canales dinámicos")
    print("  templates/config.yml - CONFIGURACIÓN UNIFICADA\n")
    print("Próximos pasos:")
    print("  1. Coloca archivos .sav en: casos/")
    print("  2. Edita archivos .sub/.mon/.con según tu estudio")
    print("  3. Descomentar estudios en: templates/config.yml")
    print("  4. Validar: pssetools sim-runner --config templates/config.yml --validate")
    print("  5. Ejecutar: pssetools sim-runner --config templates/config.yml")


def modificar_proyecto_existente(base_dir, template_base):
    """Modifica un proyecto existente."""
    imprimir_encabezado("MODIFICAR PROYECTO")
    
    opciones = [
        ('1', 'Regenerar config.yml'),
        ('2', 'Copiar scripts (Dynamic)'),
        ('3', 'Volver')
    ]
    
    seleccion = pregunta_opcion("¿Qué deseas?", opciones)
    
    if seleccion == '1':
        crear_templates_basicos(base_dir, {'ACCC', 'ASCC', 'DYN'})
        imprimir_exito("config.yml regenerado (descomentar estudios según necesidad)")
    elif seleccion == '2':
        copiar_ejemplos(base_dir, template_base)
        imprimir_info("Scripts copiados a: lib/")
    
    imprimir_exito("Completado")


def detectar_proyecto_existente(base_dir):
    """Detecta si existe un proyecto."""
    return os.path.exists(os.path.join(base_dir, 'config.cfg'))


def run_wizard():
    """Ejecuta el asistente interactivo."""
    imprimir_encabezado("ASISTENTE PSSETOOLS")
    
    base_dir = os.getcwd()
    template_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/template'
    
    if not os.path.exists(template_base):
        import pkg_resources
        template_base = pkg_resources.resource_filename('pssetools', 'template')
    
    if detectar_proyecto_existente(base_dir):
        print("Proyecto detectado: {}".format(base_dir))
        
        opciones = [
            ('1', 'Modificar'),
            ('2', 'Crear nuevo'),
            ('3', 'Salir')
        ]
        
        seleccion = pregunta_opcion("¿Qué deseas?", opciones)
        
        if seleccion == '1':
            modificar_proyecto_existente(base_dir, template_base)
        elif seleccion == '2':
            if pregunta_si_no("¿Continuar?"):
                crear_proyecto_nuevo(base_dir, template_base)
        else:
            imprimir_info("Saliendo...")
    else:
        crear_proyecto_nuevo(base_dir, template_base)
