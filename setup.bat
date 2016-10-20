@echo off
set TOYDIR=%~dp0
echo Setting PATH and PYTHONPATH environment variables relative to %TOYDIR%
set PATH=%TOYDIR%bin;%PATH%
set PYTHONPATH=%TOYDIR%;%PYTHONPATH%
