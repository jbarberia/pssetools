

savfiles=$(ls *.sav)
dinamico="flat1.py flat2.py"

dyr=gyr_24_v34_1.dyr
convload=convload_sadi.py

sub=test.sub
mon=test.mon
con=test.con


log="log"
build="build"
results="results"

mkdir -p $build $log $results

if [ -z "$1" ]; then # INTERFAZ si esta vacio el pedido ------------------------
    echo "Elegí una opción:"
    echo "1) estatico"
    echo "2) compila"
    echo "3) dinamico"
    echo "4) clean"
    echo "5) clean dinamico"
    read -p "Ingrese opción: " opt

    case "$opt" in
        1) set -- "estatico" ;;
        2) set -- "compila" ;;
        3) set -- "dinamico" ;;
        4) set -- "clean" ;;
        5) set -- "clean_dinamico" ;;
        *) echo "Opción inválida"; exit 1 ;;
    esac
fi

if [ "$1" = "estatico" ]; then # ESTATICO --------------------------------------
    for sav in $savfiles
    do
        echo creando dfx para $sav ...
        (python -m pssetools.dfx \
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
        (python -m pssetools.acc \
        --sav $sav \
        --dfx $build/"${sav%.sav}".dfx \
        --acc $build/"${sav%.sav}".acc \
        --zip $build/"${sav%.sav}".zip) >> $log/"${sav%.sav}"_estatico.log &
    done
    wait

    for sav in $savfiles
    do
        echo exportando resultados de acc para $sav ...
        (python -m pssetools.arrbox.contingency_pp \
        --acc $build/"${sav%.sav}".acc \
        --frp $build/"${sav%.sav}".frp \
        --vrp $build/"${sav%.sav}".vrp) >> $log/"${sav%.sav}"_estatico.log &
    done
    wait

    awk 'FNR==1 && NR!=1 {next} {print}' $build/*.frp > $results/estatico_flujos.csv
    awk 'FNR==1 && NR!=1 {next} {print}' $build/*.vrp > $results/estatico_tensiones.csv


elif [ "$1" = "compila" ]; then # COMPILA --------------------------------------
    echo creando snapshot ...
    (python -m pssetools.snp \
        --sav $savfiles \
        --snp $build/snapshot.snp \
        --dyr $dyr \
        --cc $build/cc.flx \
        --ct $build/ct.flx ) | tee $log/compilacion.log        

    echo compilando ...
    (python2 -m pssetools.dll \
        --sources $build/cc.flx $build/ct.flx $(ls lib/*.lib) \
        --dll lib/usrdll.dll) | tee -a $log/compilacion.log        


elif [ "$1" = "dinamico" ]; then # DINAMICO -------------------------------------
    
    for sav in $savfiles
    do
        echo convirtiendo $sav a cnv ...
        (python -m pssetools.cnv \
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
            (python -u -m pssetools.dyn \
                --cnv $build/"${sav%.sav}".cnv \
                --snp $build/snapshot.snp \
                --out $results/"${sav%.sav}"-"${py%.py}"/"${sav%.sav}"-"${py%.py}".out \
                --dll $(ls lib/*.dll) \
                --py $py \
                --no-debug \
                ) >> $log/"${sav%.sav}"-"${py%.py}".pdv &

            running=$((running+1))
            if [ "$running" -ge "$MAXJOBS" ]; then
                wait -n          # Espera a que termine 1 proceso
                running=$((running-1))
            fi
        done
    done
    wait
    read -p "Presione enter para finalizar ..."

elif [ "$1" = "clean" ]; then # Limpiar todo
    rm -rf $log $build $results
    rm -f lib/usrdll.dll
    read -p "Presione enter para finalizar ..."

elif [ "$1" = "clean_dinamico" ]; then # Limpiar solo dinamico
    rm -rf $log/*.pdv $build/*.cnv $results/*/ 
    read -p "Presione enter para finalizar ..."   
fi


