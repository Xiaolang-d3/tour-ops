@echo off
setlocal
call "%~dp0..\deploy.bat" %*
exit /b %errorlevel%
