from __future__ import print_function
from . import psspy
from . import get_config
from . import pss_activity
import zipfile
import tempfile
import os
import re
import io


def _extract_zip_file(zip_file_path):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir


def _get_contingencies(working_folder):
    with io.open(os.path.join(working_folder, "Names.phy"), encoding="latin-1") as f:
        file_content = f.read()
    strings = re.findall(r"[^\x00-\x1F\x7F-\xFF]+", file_content)[1:]
    contingency_identificator = [
        (label, isv.strip()) for label, isv in zip(strings[::2], strings[1::2])
    ]
    return contingency_identificator


@pss_activity
def run(zipfile, folder, **kwargs):
    if not os.path.isdir(folder):
        os.makedirs(folder)

    working_folder = _extract_zip_file(zipfile)
    contingencies = _get_contingencies(working_folder)

    psspy.case(os.path.join(working_folder, "InitCase.sav"))
    psspy.save(os.path.join(folder, "BASE CASE.sav"))

    for colabel, coid in contingencies:
        psspy.case(os.path.join(working_folder, "InitCase.sav"))
        ierr = psspy.getcontingencysavedcase(zipfile.encode("utf-8"), coid)
        psspy.save(os.path.join(folder, colabel))

    return 0
