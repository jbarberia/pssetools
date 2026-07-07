estatico="python -m pssetools.scripts.estatico"
cases="$(ls *.sav -1 | xargs)"

# listar simulaciones debajo...
eval $estatico -c $cases --folder estatico $args --config config.jsonc

