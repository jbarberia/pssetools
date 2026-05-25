



function SimulacionesEstaticas {
    param(
        [Parameter(Mandatory=$true)]
        [array]$files,
        [string]$sub = "estudio.sub",
        [string]$mon = "estudio.mon",
        Set-Location $PSScriptRoot
        python .\main.py
        [string]$build = "build",

        [string]$results = "results"
