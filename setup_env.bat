@echo off

REM Get the directory path of the script
set "dirpath=%~dp0"
if "%dirpath:~-1%" == "\" set "dirpath=%dirpath:~0,-1%"

REM Check if git is installed
git --version > nul 2>&1
if %errorlevel% NEQ 0 (
    echo:
    echo No git executable found in PATH!
    echo:
    pause
    exit /b 1
)

REM Check if uv is installed
uv --version > nul 2>&1
if %errorlevel% NEQ 0 (
    echo:
    echo No uv executable found in PATH!
    echo Please install uv: https://github.com/astral-sh/uv
    echo:
    pause
    exit /b 1
)

REM Sync dependencies using uv
echo:
echo Syncing dependencies with uv...
uv sync
if %errorlevel% NEQ 0 (
    echo:
    echo Failed to sync dependencies.
    echo:
    pause
    exit /b 1
)

echo:
echo Environment setup completed successfully using uv.
echo:
pause
