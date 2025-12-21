@echo off
REM Get the folder where this .bat lives
set "SCRIPT_DIR=%~dp0"

REM Run Python script
python "%SCRIPT_DIR%museum-pull.py"

