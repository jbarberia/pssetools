
dinamico="python -m pssetools.scripts.dinamico"
cfg="config.jsonc"
snp="dinamico/snapshot.snp"
dll="$(ls */*.dll -1 | xargs)"

args="-s $snp --dll $dll --config $cfg"

# listar simulaciones debajo...

eval $dinamico -c dinamico/FC01.cnv -o FC01.out --py flat.py --folder dinamico/FC01 $args &
eval $dinamico -c dinamico/FC02.cnv -o FC02.out --py flat.py --folder dinamico/FC02 $args &

wait
