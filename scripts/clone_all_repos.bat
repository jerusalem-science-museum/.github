@echo off
REM Batch file to run clone_all_repos.ps1 PowerShell script
REM Usage: clone_all_repos.bat [target_dir] [org_name]

setlocal

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%clone_all_repos.ps1"

REM Check if PowerShell script exists
if not exist "%PS_SCRIPT%" (
    echo Error: Cannot find clone_all_repos.ps1 at %PS_SCRIPT%
    pause
    exit /b 1
)

REM Execute PowerShell script with bypass execution policy
REM Pass any arguments to the PowerShell script
powershell.exe -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Script execution failed.
    pause
)

endlocal

