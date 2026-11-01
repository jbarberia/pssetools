import psse34
import psspy
from pssetools.utils.ras import automatismo

_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()


def _condicion():
    ierr, pu = psspy.busdat(4, "PU")
    return pu <= 0.92

def _accion():
    psspy.load_chng_5(4,'1',intgar1=0, realar1=_f, realar2=_f)


automatismos = [
    (_condicion, _accion)
]

def base():
    "CASO-BASE"
    pass


@automatismo(automatismos)
def BRANCH_RAMA_B():
    "F/S RAMA-B"
    psspy.branch_chng_3(1,3,'1', intgar1=0)

@automatismo(automatismos)
def BRANCH_RAMA_A():
    "F/S RAMA-A"
    psspy.branch_chng_3(1,2,'1', intgar1=0)

