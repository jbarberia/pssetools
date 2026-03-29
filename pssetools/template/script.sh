# pssetools
# Copyright (C) 2026 Barberia Juan Luis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v3.0 or later.
# See the LICENSE file for details.

savfiles=$(ls *.sav)
sub=estudio.sub
mon=estudio.mon
con=estudio.con

dyr=$(ls *.dyr)
convload=convload.py
dinamico=$(ls dyn_*.py)

log="log"
build="build"
results="results"

if [ -z "$1" ]; then # INTERFAZ si esta vacio el pedido ------------------------
    echo "Elegí una opción:"
    echo "1) estatico"
    echo "2) cortocircuito"
    echo "3) compila"
    echo "4) dinamico"
    echo "5) limpiar solo dinamico"
    echo "6) limpiar todo"
    read -p "Ingrese opción: " opt

    case "$opt" in
        1) set -- "estatico" ;;
        2) set -- "cortocircuito" ;;
        3) set -- "compila" ;;
        4) set -- "dinamico" ;;
        5) set -- "clean_dinamico" ;;
        6) set -- "clean" ;;
        *) echo "Opción inválida"; exit 1 ;;
    esac
fi

if [ "$1" = "estatico" ]; then # ESTATICO --------------------------------------
    for sav in $savfiles
    do
        echo creando dfx para $sav ...
        (python -m pssetools dfx \
        --sav $sav \
        --sub $sub \
        --mon $mon \
        --con $con \
        --dfx $build/"${sav%.sav}".dfx) > $log/"${sav%.sav}"_estatico.log &        
    done
    wait

    for sav in $savfiles
    do
        echo corriendo acc para $sav ...
        (python -m pssetools acc \
        --sav $sav \
        --dfx $build/"${sav%.sav}".dfx \
        --acc $build/"${sav%.sav}".acc \
        --zip $build/"${sav%.sav}".zip) >> $log/"${sav%.sav}"_estatico.log &
    done
    wait

    for sav in $savfiles
    do
        echo exportando resultados de acc para $sav ...
        (python -m pssetools arrbox.contingency_pp \
        --acc $build/"${sav%.sav}".acc \
        --frp $build/"${sav%.sav}".frp \
        --vrp $build/"${sav%.sav}".vrp) >> $log/"${sav%.sav}"_estatico.log &
    done
    wait

    awk 'FNR==1 && NR!=1 {next} {print}' $build/*.frp > $results/estatico_flujos.tsv
    awk 'FNR==1 && NR!=1 {next} {print}' $build/*.vrp > $results/estatico_tensiones.tsv
    read -p "Presione enter para finalizar ..."


elif [ "$1" = "cortocircuito" ]; then # CORTOCIRCUITO --------------------------
    for sav in $savfiles
    do
        echo corriendo cortocircuito para $sav ...
        (python -m pssetools ascc \
        --report $build/"${sav%.sav}".scf \
        --sav $sav \
        --sub $sub ) > $log/"${sav%.sav}"_cortocircuito.log &
    done
    wait

    awk 'FNR==1 && NR!=1 {next} {print}' $build/*.scf > $results/cortocircuito.tsv
    read -p "Presione enter para finalizar ..."


elif [ "$1" = "compila" ]; then # COMPILA --------------------------------------
    echo creando snapshot ...
    (python -m pssetools snp \
        --sav $savfiles \
        --snp $build/snapshot.snp \
        --dyr $dyr \
        --cc $build/cc.flx \
        --ct $build/ct.flx ) | tee $log/compilacion.log        

    echo compilando ...
    (python2 -m pssetools dll \
        --sources $build/cc.flx $build/ct.flx $(ls lib/*.lib) \
        --dll lib/usrdll.dll) | tee -a $log/compilacion.log        
    read -p "Presione enter para finalizar ..."


elif [ "$1" = "dinamico" ]; then # DINAMICO -------------------------------------
    for sav in $savfiles
    do
        echo convirtiendo $sav a cnv ...
        (python -m pssetools cnv \
        --sav $sav \
        --cnv $build/"${sav%.sav}".cnv \
        --py $convload) >> $log/"${sav%.sav}"_a_cnv.log &
    done
    wait

    MAXJOBS=4   # <<< ajustá acá
    running=0
    for sav in $savfiles
    do
        for py in $dinamico
        do
            echo lanzando simulacion $results/"${sav%.sav}"-"${py%.py}" ...
            (python -u -m pssetools dyn \
                --cnv $build/"${sav%.sav}".cnv \
                --snp $build/snapshot.snp \
                --out $results/"${sav%.sav}"-"${py%.py}"/"${sav%.sav}"-"${py%.py}".out \
                --dll $(ls lib/*.dll) \
                --py $py \
                --no-debug \
                ) >> $log/"${sav%.sav}"-"${py%.py}".pdv &

            running=$((running+1))
            if [ "$running" -ge "$MAXJOBS" ]; then
                wait -n # Espera a que termine 1 proceso
                running=$((running-1))
            fi
        done
    done
    wait
    read -p "Presione enter para finalizar ..."


elif [ "$1" = "clean_dinamico" ]; then # Limpiar solo dinamico
    rm -rf $log/*.pdv $build/*.cnv $results/*/
    read -p "Presione enter para finalizar ..."


elif [ "$1" = "clean" ]; then # Limpiar todo
    rm -rf $log $build $results
    rm -f lib/usrdll.dll
    read -p "Presione enter para finalizar ..."
fi
