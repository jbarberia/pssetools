# Instalación de pssetools

`pssetools` requiere una integración estrecha con la instalación de **Siemens PSS®E**. Dado que PSS®E utiliza versiones específicas de Python, la instalación debe realizarse en el intérprete asociado a la versión de PSS®E que estés utilizando.

## 📋 Requisitos Previos

1. **Licencia de Siemens PSS®E**: Debe estar activa y configurada en el sistema.
2. **Intérprete de Python**:
   - Para versiones antiguas de PSS®E $\rightarrow$ **Python 2.7**
   - Para versiones modernas (v34, v35, v36) $\rightarrow$ **Python 3.x** (según la versión instalada).

## 🛠️ Pasos de Instalación

### Opción 1: Instalación vía PIP (Recomendado)
Ejecuta el siguiente comando en la terminal del intérprete de Python de PSS®E:

**Para Python 2.7:**
```bash
C:\python27\python.exe -m pip install pandas openpyxl
C:\python27\python.exe -m pip install git+https://github.com/jbarberia/pssetools
```

**Para Python 3.x:**
```bash
C:\python314\python.exe -m pip install pandas openpyxl PyMuPDF
C:\python314\python.exe -m pip install git+https://github.com/jbarberia/pssetools
```

### Dependencias Clave
| Librería | Propósito |
| :--- | :--- |
| `pandas` | Manipulación de datos y exportación a tablas. |
| `openpyxl` | Motor necesario para generar archivos `.xlsx`. |
| `PyMuPDF` | Utilizado por las herramientas de corrección de SLDs a PDF. |
