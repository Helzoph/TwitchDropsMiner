@echo off

REM Get the directory path of the script
set "dirpath=%~dp0"
if "%dirpath:~-1%" == "\" set "dirpath=%dirpath:~0,-1%"

REM Run PyInstaller using uv run
echo Building with uv run pyinstaller...
uv run pyinstaller "%dirpath%\build.spec"
if errorlevel 1 (
    echo:
    echo PyInstaller build failed.
    echo:
    if not "%~1"=="--nopause" pause
    exit /b 1
)

echo:
echo Build completed successfully.
echo:
if not "%~1"=="--nopause" pause
