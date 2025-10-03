from . import psspy
from . import argument_parser

_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()

def run(sav, snp, dyr, cc, ct, **kwargs):
    psspy.case(sav)
    
    # genero el primer dyr
    if len(dyr) == 0:
        raise ValueError("No hay *.dyr a cargar")
    psspy.dyre_new([1,1,1,1], dyr[0], cc, ct, "")

    with open(cc, "r") as conec: cc_lines = conec.readlines()
    with open(ct, "r") as conet: ct_lines = conet.readlines()

    # genero los dyr restantes
    tmp_cc = cc.replace(".flx", "_tmp.flx")
    tmp_ct = ct.replace(".flx", "_tmp.flx")
    for dyr in dyr[1:]:
        psspy.dyre_add([_i,_i,_i,_i], dyr, tmp_cc, tmp_ct)
        
        with open(tmp_cc, "r") as conec: tmp_cc_lines = conec.readlines()
        with open(tmp_ct, "r") as conet: tmp_ct_lines = conet.readlines()

        # Inserta nuevas lineas en los archivos CC y CT
        for line in tmp_cc_lines:
            if not line.startswith("C"):
                cc_lines.insert(-3, line)                
               
        for line in tmp_ct_lines:
            if not line.startswith("C") and not "IF (.NOT. IFLAG) GO TO 9000" in line:
                ct_lines.insert(-6, line)
                    
        # limpia los archivos temporales    
        os.remove(tmp_cc)
        os.remove(tmp_ct)
        
    with open(cc, "w") as conec: conec.writelines(cc_lines)
    with open(ct, "w") as conet: conet.writelines(ct_lines)
                
    # guardo el snapshot pero antes ajusto opciones
    # todo estas opciones deberian estar en otro lado
    psspy.set_netfrq(1)
    psspy.set_osscan(1,0)
    psspy.set_genang_3(1, 180.0,0.0,0)    
    if psspy.busexs(2620) == 0:    
        psspy.set_relang(1,2620,'1')
    psspy.dynamics_solution_param_2([_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f, 0.002,_f,_f,_f,_f,_f])
    ierr = psspy.snap(sfile=snp)
    assert ierr == 0
        

if __name__ == "__main__":
    args_specs = {
        "sav": {"type": str},
        "snp": {"type": str}, 
        "cc":  {"type": str}, 
        "ct":  {"type": str}, 
        "dyr": {"nargs": "*", "type": str}
    }
    args = argument_parser(args_specs)
    run(**args)
    
    # TODO guardo que solo leo un unico valor de dyr