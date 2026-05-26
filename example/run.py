# coding: utf-8
from __future__ import print_function

import glob
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

BUILD = "build"
RESULTS = "results"
CONFIG = "src/config.cfg"
