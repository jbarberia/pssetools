# PSS/E Simulation Runner - PowerShell Script
# This script provides an interactive menu to run simulations with different configurations
# Usage: .\run_simulations.ps1

param(
    [string]$Config = "",
    [switch]$Validate,
    [switch]$DryRun,
    [switch]$Interactive,
    [switch]$Help
)

# Function to print colored text
function Write-Title {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan -BackgroundColor Black
    Write-Host $Text.PadRight(80).Substring(0, 80) -ForegroundColor Cyan -BackgroundColor Black
    Write-Host ("=" * 80) -ForegroundColor Cyan -BackgroundColor Black
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "[OK] $Text" -ForegroundColor Green
}

function Write-Info {
    param([string]$Text)
    Write-Host "[*] $Text" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Text)
    Write-Host "[!] $Text" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Text)
    Write-Host "[ERROR] $Text" -ForegroundColor Red
}

# Show help
if ($Help) {
    Write-Title "PSS/E Simulation Runner - PowerShell"
    Write-Host "Usage: .\run_simulations.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Config <file>    Use specific configuration file"
    Write-Host "  -Validate         Validate configuration without running"
    Write-Host "  -DryRun          Show commands but don't execute"
    Write-Host "  -Interactive     Ask before each simulation"
    Write-Host "  -Help            Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run_simulations.ps1"
    Write-Host "  .\run_simulations.ps1 -Config config_accc_parallel.yml"
    Write-Host "  .\run_simulations.ps1 -Config config.yaml -DryRun"
    exit 0
}

# Main execution
Write-Title "PSS/E Simulation Runner - Interactive Menu"

# Check Python availability
try {
    python --version 2>&1 | Out-Null
} catch {
    Write-Error "Python is not installed or not in PATH"
    Write-Host "Please install Python and add it to your system PATH"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check pssetools installation
python -m pssetools --help 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Warning "pssetools not found. Installing..."
    pip install -e . 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install pssetools"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# If no config specified, show menu
if ([string]::IsNullOrEmpty($Config)) {
    Write-Info "Available configurations:"
    Write-Host ""
    
    $configs = @()
    $index = 1
    
    # Discover available configs
    @("config_accc_parallel.yml", "config_parallel_full.yml", "config.yaml", "config_accc.yml", "config_dynamic.yml") | ForEach-Object {
        if (Test-Path $_) {
            $configs += $_
            $display = switch ($_) {
                "config_accc_parallel.yml" { "ACCC Parallel (2 workers)" }
                "config_parallel_full.yml" { "Full Parallel Mixed Studies (4 workers)" }
                "config.yaml" { "Default (config.yaml)" }
                "config_accc.yml" { "ACCC Sequential" }
                "config_dynamic.yml" { "Dynamic Sequential" }
                default { $_ }
            }
            Write-Host "  [$index] $display"
            $index++
        }
    }
    
    Write-Host "  [0] Exit"
    Write-Host ""
    
    $choice = Read-Host "Select configuration (0-$($configs.Count))"
    
    if ($choice -eq "0") {
        Write-Host "Exiting..."
        exit 0
    }
    
    $choiceNum = [int]$choice
    if ($choiceNum -lt 1 -or $choiceNum -gt $configs.Count) {
        Write-Error "Invalid selection"
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    $Config = $configs[$choiceNum - 1]
} else {
    if (-not (Test-Path $Config)) {
        Write-Error "Configuration file not found: $Config"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Success "Selected: $Config"
Write-Host ""

# Ask for execution mode if not specified via parameters
if (-not $Validate -and -not $DryRun -and -not $Interactive) {
    Write-Info "Execution Mode:"
    Write-Host "  [1] Validate only (check configuration without running)"
    Write-Host "  [2] Dry run (show commands but don't execute)"
    Write-Host "  [3] Normal execution"
    Write-Host "  [4] Interactive (ask before each simulation)"
    Write-Host ""
    
    $mode = Read-Host "Select mode (1-4) [3]"
    if ([string]::IsNullOrEmpty($mode)) { $mode = "3" }
    
    switch ($mode) {
        "1" { $Validate = $true; Write-Host "Mode: Validation only" }
        "2" { $DryRun = $true; Write-Host "Mode: Dry run (no execution)" }
        "3" { Write-Host "Mode: Normal execution" }
        "4" { $Interactive = $true; Write-Host "Mode: Interactive (will ask for each)" }
        default { Write-Host "Mode: Normal execution" }
    }
}

Write-Host ""
Write-Info "Running simulation..."
Write-Host ""

# Build command arguments
$args_list = @("sim-runner", "--config", $Config)
if ($Validate) { $args_list += "--validate" }
if ($DryRun) { $args_list += "--dry-run" }
if ($Interactive) { $args_list += "--interactive" }

# Run the simulation
python -m pssetools @args_list

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Success "Simulation completed successfully"
    $exitCode = 0
} else {
    Write-Host ""
    Write-Error "Simulation execution failed"
    $exitCode = 1
}

Write-Host ""
Write-Host "Finished at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Read-Host "Press Enter to exit"
exit $exitCode
