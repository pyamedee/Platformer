@echo off
call "%~dp0\venv\Scripts\activate.bat"
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
"%~dp0\venv\Scripts\python.exe" "%~dp0\__main__.pyw" --debug
call "%~dp0\venv\Scripts\deactivate.bat"
