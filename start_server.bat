@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%
set FLASK_APP=main.py
set FLASK_ENV=development

:start
python -m uvicorn main:app --host 127.0.0.1 --port 8081 --log-level debug --no-access-log
if %ERRORLEVEL% NEQ 0 (
    echo Server failed to start. Trying next port...
    goto start
)
pause 