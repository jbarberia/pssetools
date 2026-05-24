



function SimulacionesEstaticas {
    param(
        [Parameter(Mandatory=$true)]
        [array]$files,
        [string]$sub = "estudio.sub",
        [string]$mon = "estudio.mon",
        [string]$con = "estudio.con",
        [string]$log = "log",
        [string]$build = "build",
        [string]$results = "results"
    )

    Write-Host "Corriendo ACCC" -ForegroundColor Cyan

    $files | ForEach-Object -Parallel {
        $base = $_.BaseName
        $log = "$($using:log)\$($base)_estatico.log"
        $build = $using:build
        $results = $using:results
        $id = $base.GetHashCode()

        Write-Progress -Activity "  $($_.BaseName)" -Status "Creando DFX..." -Id $id -PercentComplete 20
        python -m pssetools dfx `
            --sav $_ `
            --sub $using:sub `
            --mon $using:mon `
            --con $using:con `
            --dfx "$build/$base.dfx" `
            > $log

        Write-Progress -Activity "  $($_.BaseName)" -Status "Corriendo ACC..." -Id $id -PercentComplete 40
        python -m pssetools acc `
            --sav $_ `
            --dfx "$build/$base.dfx" `
            --acc "$build/$base.acc" `
            --zipfile "$build/$base.zip" `
            >> $log

        Write-Progress -Activity "  $($_.BaseName)" -Status "Exportando ACC..." -Id $id -PercentComplete 60
        python -m pssetools acc-pp `
            --acc "$build/$base.acc" `
            --frp "$build/$base.frp" `
            --vrp "$build/$base.vrp" `
            >> $log

        Write-Progress -Activity "  $($_.BaseName)" -Status "Descomprimiendo ZIP..." -Id $id -PercentComplete 80
        python -m pssetools acc-unzip `
            --zipfile "$build/$base.zip" `
            --folder  "$results/$base" `
            >> $log

        Write-Progress -Activity "  $($_.BaseName)" -Status "Finalizado" -Id $id -PercentComplete 100
        Start-Sleep -Milliseconds 100
        Write-Host "  ACCC $($_.BaseName)"
    } -ThrottleLimit 4

    Get-ChildItem "$build\*.frp" |
        Import-Csv -Delimiter "`t" |
        Export-Csv "$results\estatico_flujos.tsv" -Delimiter "`t" -NoTypeInformation -UseQuotes AsNeeded

    Get-ChildItem "$build\*.vrp" |
        Import-Csv -Delimiter "`t" |
        Export-Csv "$results\estatico_tensiones.tsv" -Delimiter "`t" -NoTypeInformation -UseQuotes AsNeeded

    Write-Host "ACCC Finalizado" -ForegroundColor Cyan
}


function Cortocircuito {
    param(
        [Parameter(Mandatory=$true)]
        [array]$files,
        [string]$sub = "estudio.sub",
        [string]$log = "log",
        [string]$build = "build",
        [string]$results = "results"
    )

    Write-Host "Corriendo ASCC" -ForegroundColor Cyan

    $files | ForEach-Object -Parallel {
        $base = $_.BaseName
        $log = "$($using:log)\$($base)_cortocircuito.log"
        $build = $using:build
        $results = $using:results
        $id = $base.GetHashCode()
        $scf = Join-Path $build "$($base).scf"

        Write-Host "  ASCC $($_.BaseName)"
        python -m pssetools ascc `
            --sav $_ `
            --sub $using:sub `
            --report $scf `
            > $log

    } -ThrottleLimit 4
    
    Get-ChildItem "$build\*.scf" |
        Import-Csv -Delimiter "`t" |
        Export-Csv "$results\cortocircuito.tsv" -Delimiter "`t" -NoTypeInformation -UseQuotes AsNeeded

    Write-Host "ASCC Finalizado" -ForegroundColor Green
}

function Compila {
    param(
        [Parameter(Mandatory=$true)]
        [array]$sources,
        [string]$file,
        [string]$dll = "lib/usrdll.dll",
        [string]$snp = "snapshot.snp",
        [string]$dyr = "estudio.dyr",
        [string]$idv = "estudio.idv",
        [string]$log = "log",
        [string]$build = "build",
        [string]$results = "results"
    )
    $nombreLog = [System.IO.Path]::GetFileNameWithoutExtension($snp)

    python -m pssetools snp `
        --sav $file `
        --snp $snp `
        --idv $idv `
        --dyr $dyr `
        --cc "$($build)/cc.flx" `
        --ct "$($build)/ct.flx" `
        --sav $file `
        > "$($log)/$($nombreLog).log"

    $sources += "$($build)/cc.flx"
    $sources += "$($build)/ct.flx"

    python2 -m pssetools dll `
        --sources $sources `
        --dll $dll `
        | Tee-Object -FilePath "$($log)/$($nombreLog).log" -Append
    }

function Dinamico {
    param(
        [Parameter(Mandatory=$true)]
        [array]$files,
        [array]$dyn_py,
        [array]$dll,
        [string]$snp,
        [string]$cnv_py = "convload.py",
        [string]$log = "log",
        [string]$build = "build",
        [string]$results = "results"
    )

    Write-Host "Convirtiendo casos" -ForegroundColor Cyan

    $files | ForEach-Object -Parallel {
        $base = $_.BaseName
        $log = Join-Path $using:log "$($base)_conversion.log"
        $cnv = "$($using:build)/$($base).cnv"
        $id = $_.GetHashCode()

        Write-Host "  CNV $($base)"

        python -m pssetools cnv `
        --sav $_ `
        --cnv $cnv `
        --py $using:cnv_py `
        > $log

    } -ThrottleLimit 4
    
    Write-Host "Casos convertidos" -ForegroundColor Green


    Write-Host "Lanzando simulaciones" -ForegroundColor Cyan
    $cnvfiles = Get-ChildItem -Filter "$($build)/*.cnv"
    $simulaciones = foreach ($cnv in $cnvfiles){
        foreach ($py in $dyn_py){
            [PSCustomObject]@{
                name = "$($cnv.BaseName)_$($py.BaseName)"
                cnv = $cnv
                py = $py
            }
        }
    }

    $simulaciones | ForEach-Object -Parallel {
        $log = Join-Path $using:log "$($_.name).log"
        $out = Join-Path $using:results $_.name "$($_.name).outx"
        
        $progId = [math]::Abs($_.name.GetHashCode() % 10000)
        
        Write-Host "  DYN $($_.name)"
        python -m pssetools dyn `
            --cnv $_.cnv `
            --snp $using:snp `
            --out $out `
            --dll $using:dll `
            --py $_.py `
            --no-debug `
            > $log                  
        } -ThrottleLimit 4

    Write-Host "Simulaciones terminadas" -ForegroundColor Green
}

function Limpieza {
    param(
        [string[]]$carpetas = @("build", "log", "results")
    )
    Write-Host "Iniciando Limpieza" -ForegroundColor Yellow

    foreach ($dir in $carpetas) {
        if (Test-Path $dir) {
            Write-Host "Limpiando: $dir..." -ForegroundColor Gray
            Remove-Item -Path "$dir\*" -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "Carpeta $dir no existía, creada de cero." -ForegroundColor DarkGray
        }
    }
    Write-Host "Limpieza completada." -ForegroundColor Green
}

# MAIN -------------------------------------------------------------------------

$savfiles = Get-ChildItem -Filter *.sav
$sub = "estudio.sub"
$mon = "estudio.mon"
$con = "estudio.con"

$idv = "estudio.idv"
$dyr = Get-ChildItem -Filter *.dyr
$sources = Get-ChildItem -Filter lib/*.lib
$dll = Get-ChildItem -Filter lib/*.dll

$convload = "convload_sadi.py"
$simulaciones = Get-ChildItem -Filter flat*.py

$log = "log"
$build = "build"
$results = "results"

Write-Host "1) estatico"
Write-Host "2) cortocircuito"
Write-Host "3) compila"
Write-Host "4) dinámico"
Write-Host "6) limpia todo"
$opt = Read-Host "Seleccione un valor"

switch ($opt) {
    "1" {
        SimulacionesEstaticas `
            -files $savfiles `
            -sub $sub `
            -mon $mon `
            -con $con `
            -log $log `
            -build $build `
            -results $results
    }
    "2" {
        Cortocircuito `
            -files $savfiles `
            -sub $sub `
            -log $log `
            -build $build `
            -results $results
    }
    "3" {
        Compila `
            -file $savfiles[0].Name `
            -dyr $dyr `
            -idv $idv `
            -snp "$($build)/snapshot.snp" `
            -sources $sources `
            -dll "lib/usrdll.dll" `
            -log $log `
            -build $build `
            -results $results `
    }
    "4" {
        Dinamico `
            -file $savfiles `
            -snp "$($build)/snapshot.snp" `
            -dyn_py $simulaciones `
            -cnv_py $convload `
            -dll $dll `
            -log $log `
            -build $build `
            -results $results `
    }
    "6" {
        Limpieza -carpetas @($build, $log ,$results)
        Remove-Item -Path "lib/usrdll.dll" -ErrorAction SilentlyContinue
    }
    Default {Write-Host "Opción inválida"}
}

