import warnings

from .utils import get_config, get_kwargs

# estatico
from .accc_df import accc_df
from .accc_unzip import accc_unzip

# cortocircuito
from .ascc import ascc

# dinamico
from .snp import run as snp
from .dll import run as dll
from .dyn import run as dyn
from .dyn_pp import run as dyn_pp

__all__ = [
    "accc_df",
    "accc_unzip",
    "ascc",
    "snp",
    "dll",
    "dyn",
    "dyn_pp",
]

for name in __all__:
    globals()[name].__module__ = __name__

