import os

def create_snapshot(sav, snp, dyr, cc, ct, **kwargs):
    """
    Creates a PSS/E snapshot (.snp) by merging multiple dynamic files.

    Loads .dyr files, generates and merges CONEC/CONET source files (.flx),
    and configures dynamic simulation parameters before saving the snapshot.

    Args:
        sav (str): Input PSS/E case file (.sav).
        snp (str): Output snapshot file (.snp).
        dyr (list of str): List of dynamic data files (.dyr).
        cc (str): Path for the CONEC (.flx) source file to be generated.
        ct (str): Path for the CONET (.flx) source file to be generated.
        **kwargs: Additional keyword arguments.

    Returns:
        int: The PSS/E activity return code (ierr from saving the snapshot).

    Raises:
        ValueError: If no .dyr files are provided.
    """    
    import psspy
    psspy.psseinit()

    psspy.case(sav)

    _i = psspy.getdefaultint()
    _f = psspy.getdefaultreal()
    _s = psspy.getdefaultchar()

    # genero el primer dyr
    if len(dyr) == 0:
        raise ValueError("No hay *.dyr a cargar")
    psspy.dyre_new([1,1,1,1], dyr[0], cc, ct, "")

    with open(cc, "r") as conec: cc_lines = conec.readlines()
    with open(ct, "r") as conet: ct_lines = conet.readlines()

    # genero los dyr restantes
    tmp_cc = cc.replace(".flx", "_tmp.flx")
    tmp_ct = ct.replace(".flx", "_tmp.flx")

    for dyr_file in dyr[1:]:
        psspy.dyre_add([_i,_i,_i,_i], dyr_file, tmp_cc, tmp_ct)
        
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
        if os.path.exists(tmp_cc): os.remove(tmp_cc)
        if os.path.exists(tmp_ct): os.remove(tmp_ct)
        
    with open(cc, "w") as conec: conec.writelines(cc_lines)
    with open(ct, "w") as conet: conet.writelines(ct_lines)
                   
    # guarda archivo
    ierr = psspy.snap(sfile=snp)
    return ierr
