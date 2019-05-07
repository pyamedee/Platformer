@echo off
call "%~dp0\commands\activate.cmd"
"%base%\venv\Scripts\python.exe" "%base%\__main__.pyw" --debug
