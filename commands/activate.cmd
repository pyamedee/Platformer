@echo off
set "path2scripts=%~dp0\..\venv\Scripts"
set "PATH=%~dp0;%path2scripts%;%PATH%"
set "base=%~dp0\.."
call %~dp0\..\venv\Scripts\activate.bat