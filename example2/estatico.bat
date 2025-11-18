@echo off
REM estatico.bat
REM Parameters: %1=SAV, %2=SUB, %3=MON, %4=CON
SETLOCAL EnableDelayedExpansion

set "build_dir=build"
set "results_dir=results"

REM Extract basename from the first argument (%1)
set "basename=%~n1"

echo Starting process for: %basename%

python -m pssetools.dfx ^
    --sav %1 ^
    --sub %2 ^
    --mon %3 ^
    --con %4 ^
    --dfx %build_dir%\%basename%.dfx

python -m pssetools.acc ^
    --sav %1 ^
    --acc %build_dir%\%basename%.acc ^
    --dfx %build_dir%\%basename%.dfx ^
    --zipfile %results_dir%\%basename%.zip

python -m pssetools.arrbox.contingency_pp ^
    --acc %build_dir%\%basename%.acc ^
    --frp %results_dir%\%basename%.frp ^
    --vrp %results_dir%\%basename%.vrp

echo Finished processing: %basename%
ENDLOCAL
