@echo off
REM PSS/E Simulation Runner - Windows Batch Script
REM This script provides an interactive menu to run simulations with different configurations
REM Usage: run_simulations.bat [options]

setlocal enabledelayedexpansion

REM Define color codes using ANSI escape sequences
set "ESC=[0m"
set "BOLD=[1m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "CYAN=[96m"
set "RED=[91m"

REM Title
cls
echo.
echo !CYAN!================================================================================!ESC!
echo !CYAN!                   PSS/E SIMULATION RUNNER - Interactive Menu                   !ESC!
echo !CYAN!================================================================================!ESC!
echo.

REM Check if Python and pssetools are available
python --version >nul 2>&1
if errorlevel 1 (
    echo !RED![ERROR] Python is not installed or not in PATH!ESC!
    echo Please install Python and add it to your system PATH
    pause
    exit /b 1
)

REM Check if pssetools is installed
python -m pssetools --help >nul 2>&1
if errorlevel 1 (
    echo !YELLOW![!] pssetools not found. Installing...!ESC!
    pip install -e .
    if errorlevel 1 (
        echo !RED![ERROR] Failed to install pssetools!ESC!
        pause
        exit /b 1
    )
)

REM Available configurations
echo !CYAN![*] Available configurations:!ESC!
echo.

REM Count available configs
set /a config_count=0
if exist "config_accc_parallel.yml" (
    set /a config_count+=1
    set "config_!config_count!=config_accc_parallel.yml"
    echo   [!config_count!] ACCC Parallel (2 workers)
)

if exist "config_parallel_full.yml" (
    set /a config_count+=1
    set "config_!config_count!=config_parallel_full.yml"
    echo   [!config_count!] Full Parallel Mixed Studies (4 workers)
)

if exist "config.yaml" (
    set /a config_count+=1
    set "config_!config_count!=config.yaml"
    echo   [!config_count!] Default (config.yaml)
)

if exist "config_accc.yml" (
    set /a config_count+=1
    set "config_!config_count!=config_accc.yml"
    echo   [!config_count!] ACCC Sequential
)

if exist "config_dynamic.yml" (
    set /a config_count+=1
    set "config_!config_count!=config_dynamic.yml"
    echo   [!config_count!] Dynamic Sequential
)

echo   [0] Exit
echo.

REM Get user choice
set /p choice="Select configuration (0-%config_count%): "

if "%choice%"=="0" (
    echo Exiting...
    exit /b 0
)

REM Validate choice
if "%choice%" gtr "%config_count%" (
    echo !RED![ERROR] Invalid selection!ESC!
    timeout /t 2
    goto :EOF
)

REM Get selected config
set "selected_config=!config_%choice%!"
if not defined selected_config (
    echo !RED![ERROR] Configuration not found!ESC!
    timeout /t 2
    goto :EOF
)

echo.
echo !GREEN![OK] Selected: !selected_config!!ESC!
echo.

REM Ask for execution mode
echo !CYAN![*] Execution Mode:!ESC!
echo   [1] Validate only (check configuration without running)
echo   [2] Dry run (show commands but don't execute)
echo   [3] Normal execution
echo   [4] Interactive (ask before each simulation)
echo.

set /p exec_mode="Select mode (1-4) [3]: "
if "%exec_mode%"=="" set exec_mode=3

set "extra_args="
if "%exec_mode%"=="1" (
    set "extra_args=--validate"
    echo Mode: Validation only
) else if "%exec_mode%"=="2" (
    set "extra_args=--dry-run"
    echo Mode: Dry run (no execution)
) else if "%exec_mode%"=="3" (
    echo Mode: Normal execution
) else if "%exec_mode%"=="4" (
    set "extra_args=--interactive"
    echo Mode: Interactive (will ask for each)
) else (
    echo !YELLOW![!] Invalid mode, using normal execution!ESC!
)

echo.
echo !CYAN![*] Running simulation...!ESC!
echo.

REM Run the simulation
python -m pssetools sim-runner --config "!selected_config!" !extra_args!

if errorlevel 1 (
    echo.
    echo !RED![ERROR] Simulation execution failed!ESC!
    set /a exit_code=1
) else (
    echo.
    echo !GREEN![OK] Simulation completed successfully!ESC!
    set /a exit_code=0
)

echo.
echo Finished at: %date% %time%
pause
exit /b !exit_code!
