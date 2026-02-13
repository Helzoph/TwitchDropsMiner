@echo off
cls
set dirpath=%~dp0
if "%dirpath:~-1%" == "\" set dirpath=%dirpath:~0,-1%

set /p "choice=Start with a console? (y/n) "
set /p "headless=Run in headless mode? (y/n) "

set "ARGS="
if "%headless%"=="y" (
    set "ARGS=--headless"
)

if "%choice%"=="y" (
    uv run python "%dirpath%\main.py" %ARGS%
) else (
    start "TwitchDropsMiner" uv run pythonw "%dirpath%\main.py" %ARGS%
)
pause
