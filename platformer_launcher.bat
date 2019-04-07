@echo off
call "%~dp0\venv\Scripts\activate.bat"
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
start "%~dp0\venv\Scripts\pythonw.exe" "%~dp0\__main__.pyw"
call "%~dp0\venv\Scripts\deactivate.bat"
