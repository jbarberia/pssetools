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
    """Crea templates básicos en carpeta templates/."""
    templates_dir = os.path.join(base_dir, 'templates')
    
    imprimir_info("Generando templates básicos...")
    
    # Templates PSS/E
    templates_psse = {
        'accc.sub': 'SUBSYSTEM ESTUDIO\n  BUS 1 AREA 1\n  BUS 2 AREA 1\n  BUS 3 AREA 1\nENDSUB\n',
        'accc.mon': '; Puntos de monitoreo\n1\n2\n3\n',
        'accc.con': '; Contingencias\nFAULT - BUS  1\nFAULT - LINE  1  2\n',
        'accc.idv': '; Definición de canales\n1 ,BUS VOLTAGE , 1\n2 ,BUS VOLTAGE , 2\n'
    }
    
    for nombre, contenido in templates_psse.items():
        ruta = os.path.join(templates_dir, nombre)
        if not os.path.exists(ruta):
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write(contenido)
            imprimir_exito("Template: {}".format(nombre))
    
    if 'ACCC' in tipos_analisis:
        config = 'workspace:\n  base_dir: "."\nsimulationes:\n  - name: "ACCC_Base"\n    type: "accc"\n    case: "casos/caso.sav"\n    options:\n      sub: "templates/accc.sub"\n      mon: "templates/accc.mon"\n      con: "templates/accc.con"\n      dfx: "build/accc.dfx"\nexecution:\n  continue_on_error: false\n  logging: "normal"\n'
        ruta = os.path.join(templates_dir, 'config_accc.yml')
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(config)
        imprimir_exito("Configuración: config_accc.yml")


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
    """Copia ejemplos Python."""
    ejemplos_dir = os.path.join(template_base, 'optional', 'examples')
    
    if not os.path.exists(ejemplos_dir):
        return
    
    if pregunta_si_no("¿Incluir ejemplos Python?"):
        lib_dir = os.path.join(base_dir, 'lib')
        
        for archivo in os.listdir(ejemplos_dir):
            if archivo.endswith('.py'):
                src = os.path.join(ejemplos_dir, archivo)
                dst = os.path.join(lib_dir, archivo)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    imprimir_exito("Ejemplo: {}".format(archivo))


def crear_proyecto_nuevo(base_dir, template_base):
    """Crea un proyecto nuevo."""
    imprimir_encabezado("CREAR PROYECTO NUEVO")
    
    opciones_analisis = [
        ('1', 'ACCC (Análisis de Contingencias)'),
        ('2', 'ASCC (Análisis de Cortocircuito)'),
        ('3', 'Simulación Dinámica'),
        ('4', 'Todos'),
        ('5', 'Solo esenciales')
    ]
    
    seleccion = pregunta_opcion("¿Qué análisis ejecutarás?", opciones_analisis)
    
    tipos_analisis = set()
    if seleccion in ('1', '4'):
        tipos_analisis.add('ACCC')
    if seleccion in ('2', '4'):
        tipos_analisis.add('ASCC')
    if seleccion in ('3', '4'):
        tipos_analisis.add('DYN')
    
    imprimir_info("Creando estructura...")
    crear_carpetas(base_dir)
    copiar_archivos_esenciales(base_dir, template_base)
    crear_templates_basicos(base_dir, tipos_analisis)
    copiar_ejemplos(base_dir, template_base)
    
    imprimir_encabezado("PROYECTO CREADO!")
    print("Ubicación: {}\n".format(base_dir))
    print("Carpetas:")
    print("  lib/        - Scripts Python")
    print("  templates/  - Configuraciones YAML")
    print("  build/      - Salidas (.dfx, .acc)")
    print("  results/    - Reportes")
    print("  casos/      - Archivos .sav\n")
    print("Próximos pasos:")
    print("  1. Coloca archivos .sav en: casos/")
    print("  2. Edita: templates/config_accc.yml")
    print("  3. Ejecuta: pssetools sim-runner --config templates/config_accc.yml")


def modificar_proyecto_existente(base_dir, template_base):
    """Modifica un proyecto existente."""
    imprimir_encabezado("MODIFICAR PROYECTO")
    
    opciones = [
        ('1', 'Regenerar templates'),
        ('2', 'Copiar ejemplos'),
        ('3', 'Volver')
    ]
    
    seleccion = pregunta_opcion("¿Qué deseas?", opciones)
    
    if seleccion == '1':
        crear_templates_basicos(base_dir, {'ACCC', 'ASCC', 'DYN'})
        imprimir_exito("Templates regenerados")
    elif seleccion == '2':
        copiar_ejemplos(base_dir, template_base)
    
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
