@echo off
call "%~dp0\activate.cmd"
start "%base%\venv\Scripts\pythonw.exe" "%base%\__main__.pyw"
