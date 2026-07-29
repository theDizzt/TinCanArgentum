@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".env" (
    if exist ".env.example" (
        copy /y ".env.example" ".env" >nul
        echo [SETUP REQUIRED] Created .env from .env.example.
        echo Fill in the API keys and bot token, then run this file again.
    ) else (
        echo [ERROR] Could not find .env or .env.example.
    )
    pause
    exit /b 1
)

set "JAVA_VERSION="
for /f "tokens=3" %%V in ('reg query "HKLM\SOFTWARE\JavaSoft\JDK" /v CurrentVersion 2^>nul ^| find "CurrentVersion"') do set "JAVA_VERSION=%%V"
if defined JAVA_VERSION (
    for /f "tokens=2,*" %%A in ('reg query "HKLM\SOFTWARE\JavaSoft\JDK\%JAVA_VERSION%" /v JavaHome 2^>nul ^| find "JavaHome"') do (
        if "%%A"=="REG_SZ" set "JAVA_HOME=%%B"
    )
)

if not exist "%JAVA_HOME%\bin\java.exe" (
    if exist "C:\Program Files\Java\jdk-21\bin\java.exe" (
        set "JAVA_HOME=C:\Program Files\Java\jdk-21"
    ) else if exist "C:\Program Files\Java\jdk-17\bin\java.exe" (
        set "JAVA_HOME=C:\Program Files\Java\jdk-17"
    ) else (
        echo [ERROR] Java 9 or later was not found.
        echo Install a current JDK, such as Java 17 or Java 21.
        echo https://learn.microsoft.com/java/openjdk/download
        pause
        exit /b 1
    )
)

set "PATH=%JAVA_HOME%\bin;%PATH%"
echo Using Java from: "%JAVA_HOME%"

set "PYTHON_EXE="
set "PYTHON_ARGS="
set "BASE_PYTHON_EXE="
set "BASE_PYTHON_ARGS="

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] < (3, 13) else 1)" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] The existing .venv does not use Python 3.10, 3.11, or 3.12.
        echo Remove .venv and run this file again with a supported Python installed.
        pause
        exit /b 1
    )
    set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"
    goto python_found
)

where py >nul 2>&1
if not errorlevel 1 (
    py -3.10 --version >nul 2>&1
    if not errorlevel 1 (
        set "BASE_PYTHON_EXE=py"
        set "BASE_PYTHON_ARGS=-3.10"
        goto base_python_found
    )
    py -3.11 --version >nul 2>&1
    if not errorlevel 1 (
        set "BASE_PYTHON_EXE=py"
        set "BASE_PYTHON_ARGS=-3.11"
        goto base_python_found
    )
    py -3.12 --version >nul 2>&1
    if not errorlevel 1 (
        set "BASE_PYTHON_EXE=py"
        set "BASE_PYTHON_ARGS=-3.12"
        goto base_python_found
    )
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "BASE_PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto base_python_found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "BASE_PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto base_python_found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set "BASE_PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto base_python_found
)

where python >nul 2>&1
if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] < (3, 13) else 1)" >nul 2>&1
    if not errorlevel 1 (
        set "BASE_PYTHON_EXE=python"
        goto base_python_found
    )
)

echo [ERROR] Python 3.10, 3.11, or 3.12 was not found.
echo Install a supported 64-bit Python version and run this file again.
pause
exit /b 1

:base_python_found
if /i "%~1"=="--check" (
    echo Ready to create .venv with: "%BASE_PYTHON_EXE%" %BASE_PYTHON_ARGS%
    exit /b 0
)

echo Creating an isolated Python environment in .venv...
"%BASE_PYTHON_EXE%" %BASE_PYTHON_ARGS% -m venv ".venv"
if errorlevel 1 (
    echo [ERROR] Failed to create .venv.
    pause
    exit /b 1
)
set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"

:python_found
if /i "%~1"=="--check" (
    echo Ready to run with: "%PYTHON_EXE%" %PYTHON_ARGS%
    exit /b 0
)

"%PYTHON_EXE%" %PYTHON_ARGS% -c "import discord, dotenv, flask, flask_compress, gevent, konlpy, korean_lunar_calendar, numpy, openai, openpyxl, PIL, pydantic, nacl, yaml, requests, tqdm" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    "%PYTHON_EXE%" %PYTHON_ARGS% -m pip install -r requirements-windows.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Package installation failed.
        pause
        exit /b 1
    )
)

echo Starting TinCanArgentum...
"%PYTHON_EXE%" %PYTHON_ARGS% -u main.py
set "BOT_EXIT_CODE=%ERRORLEVEL%"

if not "%BOT_EXIT_CODE%"=="0" (
    echo.
    echo The bot exited with error code %BOT_EXIT_CODE%.
    pause
)

exit /b %BOT_EXIT_CODE%
