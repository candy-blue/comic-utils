@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "BOOTSTRAP_PYTHON="
set "BUILD_VENV=%SCRIPT_DIR%.build-venv"
set "BUILD_PYTHON=%BUILD_VENV%\Scripts\python.exe"
set "PYI_WORKPATH=%SCRIPT_DIR%.pyinstaller-build"

call python --version >nul 2>&1
if not errorlevel 1 (
    set "BOOTSTRAP_PYTHON=python"
)

if not defined BOOTSTRAP_PYTHON (
    call py -3 --version >nul 2>&1
    if not errorlevel 1 (
        set "BOOTSTRAP_PYTHON=py -3"
    )
)

if not defined BOOTSTRAP_PYTHON (
    echo [ERROR] Python not found in PATH.
    echo Install Python 3.10+ and make sure the "python" or "py" command is available.
    exit /b 1
)

if exist "%BUILD_PYTHON%" (
    call "%BUILD_PYTHON%" --version >nul 2>&1
    if errorlevel 1 (
        echo Existing build venv is invalid. Recreating...
        rmdir /s /q "%BUILD_VENV%"
    )
)

if not exist "%BUILD_PYTHON%" (
    echo Creating build environment...
    call %BOOTSTRAP_PYTHON% -m venv "%BUILD_VENV%"
    if errorlevel 1 (
        echo [ERROR] Failed to create build virtual environment.
        exit /b 1
    )
)

echo Using build Python: %BUILD_PYTHON%
echo Installing dependencies...
call "%BUILD_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    exit /b 1
)

if exist "%PYI_WORKPATH%" (
    rmdir /s /q "%PYI_WORKPATH%"
)

echo Building EXE...
call "%BUILD_PYTHON%" -m PyInstaller --clean --noconfirm --workpath "%PYI_WORKPATH%" comic-utils.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    exit /b 1
)

echo Done!
echo Executable is in the dist folder.
exit /b 0
