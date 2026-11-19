# coding: latin-1
import functools


def automatismo(reglas):
    """Automatismo de evaluación de reglas de contingencia."""    
    import psspy
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            # 1. Maniobra topológica
            func(*args, **kwargs)            
            
            # 2. Resolución base
            desconectar_islas()
            psspy.runlastsolution()
            
            # 3. Bucle maestro de evaluación simultánea
            while True:
                actuo_alguno = False                    
                for condicion, accion in reglas:
                    if condicion():
                        actuo_alguno = True
                        accion()                            
                        desconectar_islas()
                        psspy.runlastsolution()
                                        
                # Si ninguna regla actuó, o el caso divergió, terminamos
                if not actuo_alguno or psspy.solved() != 0:
                    break
                    
                    
            return psspy.solved()
        return wrapper
    return decorator


def desconectar_islas():
    import psspy
    ierr, buses = psspy.tree(1, 0)
    while buses != 0:
        ierr, buses = psspy.tree(2, 1)
