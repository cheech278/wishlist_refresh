@echo off
setlocal enableextensions enabledelayedexpansion

set PYTHON_VERSION=3.10.0
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe
set PYTHON_INSTALLER=python-%PYTHON_VERSION%-amd64.exe
set SCRIPT_NAME=refresh_wishlist.py
set PIP_REQUIREMENTS=requirements.txt

rem Check if Python is installed
python --version 2>NUL | findstr /B /C:"Python %PYTHON_VERSION%" >NUL
if %errorlevel% == 0 (
    echo Latest version of Python is already installed.
) else (
    rem Download Python installer
    echo Downloading Python %PYTHON_VERSION%...
    powershell -Command "& {Invoke-WebRequest '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}"

    rem Install Python
    echo Installing Python %PYTHON_VERSION%...
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1
    del "%PYTHON_INSTALLER%"
)

pip --version 2>NUL | findstr /B /C:"pip" >NUL
if %errorlevel% == 0 (
    echo Latest version of pip is already installed.
)



pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo pip is already installed on this system.

    rem Check if pip is up-to-date
    pip install --upgrade pip >nul 2>&1
    if %errorlevel% equ 0 (
        echo pip is up-to-date.
    ) else (
        echo Updating pip...
        python -m pip install --upgrade pip >nul 2>&1
        if %errorlevel% equ 0 (
            echo pip has been updated.
        ) else (
            echo Failed to update pip. Please check your internet connection and try again.
        )
    )
) else (
    echo pip is not installed on this system. Installing...
    curl -O https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
    echo pip installation complete.
)



echo Installing dependencies for %SCRIPT_NAME%...
pip install -r %PIP_REQUIREMENTS%




cd /d %~dp0
python "%~dp0\refresh_wishlist.py"
pause