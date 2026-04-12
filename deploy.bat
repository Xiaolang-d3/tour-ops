@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
set "CORE_SCRIPT=%SCRIPT_DIR%deploy-core.bat"
set "MODE=%~1"

if not exist "%CORE_SCRIPT%" (
    echo Missing core script: "%CORE_SCRIPT%"
    exit /b 1
)

if not defined MODE set "MODE=start"

if /I "%MODE%"=="start" goto :run
if /I "%MODE%"=="start-api" goto :run
if /I "%MODE%"=="start-web" goto :run
if /I "%MODE%"=="all" (
    echo `deploy.bat all` no longer prepares the environment.
    echo Run `setup-env.bat` first, then run `deploy.bat`.
    exit /b 1
)
if /I "%MODE%"=="bootstrap" goto :env_mode
if /I "%MODE%"=="check" goto :env_mode
if /I "%MODE%"=="install" goto :env_mode
if /I "%MODE%"=="setup" goto :env_mode

echo Usage: deploy.bat [start^|start-api^|start-web]
echo Environment preparation has moved to setup-env.bat
exit /b 1

:env_mode
echo Environment preparation has moved to setup-env.bat
echo Example: setup-env.bat %MODE%
exit /b 1

:run
call "%CORE_SCRIPT%" %MODE%
exit /b %errorlevel%
