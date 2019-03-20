@echo off
call "%~dp0\venv\Scripts\activate.bat"
set "PYTHONPATH=%~dp0;%PYTHONPATH"
"%~dp0\venv\Scripts\python.exe" "%~dp0\Scripts\level_reader.pyw" "%~dp0\" %1
call "%~dp0\venv\Scripts\deactivate.bat"
