# pssetools

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/jbarberia/pssetools)](https://github.com/jbarberia/pssetools/issues)

**pssetools** es una colección de módulos, scripts y utilidades en Python para automatizar, analizar y extender las capacidades de Siemens PSS®E. Este proyecto busca simplificar tareas repetitivas como la ejecución de flujos de carga, simulaciones dinámicas y la extracción/procesamiento de resultados.

## 🚀 Características principales

* **Automatización:** Scripts listos para ejecutar simulaciones masivas.
* **Extracción de datos:** Convierte los resultados de PSS®E (.sav, .out) a formatos manejables (Pandas DataFrames, CSV, Excel).
* **Gestión de la API:** Funciones envolventes (*wrappers*) que facilitan la inicialización de `psspy` y la configuración del entorno.

## 📋 Requisitos previos

Para utilizar esta librería, es **estrictamente necesario** contar con:

1. Una instalación válida y con licencia de **Siemens PSS®E** (v34 o v36 recomendadas).
2. **Python** compatible con tu versión de PSS®E (por ejemplo, Python 2.7 para versiones antiguas, o Python 3.14 para PSS®E 36).
3. Dependencias de Python (listadas en `requirements.txt`).

## 🛠️ Instalación

```bash
C:\python27\python.exe -m pip install pandas openpyxl
C:\python27\python.exe -m pip install git+https://github.com/jbarberia/pssetools

C:\python314\python.exe -m pip install pandas openpyxl PyMuPDF
C:\python314\python.exe -m pip install git+https://github.com/jbarberia/pssetools
```

## 📋 Requisitos

* **Siemens PSS®E** con licencia válida (v33, v34 o v35).
* **Python**: Debe coincidir con el intérprete de tu versión de PSS®E (Python 2.7 o Python 3.x).
* **Librerías externas:** (Instalar vía `pip`)
  * `pandas` (para exportación de resultados a Excel).
  * `openpyxl` (motor de Excel para pandas).
  * `PyMuPDF` (para corrección y recorte de SLDs a PDF).


## ¿Como se usa?

En la termina interactiva del PSSE poner:

```
import pssetools
pssetools.gui()
```
