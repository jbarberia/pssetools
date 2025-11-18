@ECHO off
SETLOCAL EnableDelayedExpansion

set build=build
set results=results
set estatico=estatico.tsv

if not exist %build% mkdir %build%
if not exist %results% mkdir %results%

for /F "tokens=1-4 skip=1" %%a in (%estatico%) do (
    START "CASO_%%~na" CMD /C estatico "%%a" "%%b" "%%c" "%%d"
)

