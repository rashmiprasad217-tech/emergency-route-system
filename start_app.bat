@echo off
title Emergency Route System Server
echo Starting Emergency Route System Flask Server...
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    echo Using virtual environment python...
    venv\Scripts\python.exe app.py
) else (
    echo Using system python...
    python app.py
)

pause
