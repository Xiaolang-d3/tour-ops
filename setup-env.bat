@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
set "CORE_SCRIPT=%SCRIPT_DIR%deploy-core.bat"
set "MODE=%~1"

if not exist "%CORE_SCRIPT%" (
    echo Missing core script: "%CORE_SCRIPT%"
    exit /b 1
)

if not defined MODE set "MODE=setup"

if /I "%MODE%"=="setup" goto :run
if /I "%MODE%"=="bootstrap" goto :run
if /I "%MODE%"=="check" goto :run
if /I "%MODE%"=="install" goto :run
if /I "%MODE%"=="all" (
    echo `setup-env.bat all` has been replaced by `setup-env.bat setup`.
    set "MODE=setup"
    goto :run
)
if /I "%MODE%"=="start" goto :deploy_mode
if /I "%MODE%"=="start-api" goto :deploy_mode
if /I "%MODE%"=="start-web" goto :deploy_mode

echo Usage: setup-env.bat [setup^|bootstrap^|check^|install]
echo Service startup has moved to deploy.bat
exit /b 1

:deploy_mode
echo Service startup has moved to deploy.bat
echo Example: deploy.bat %MODE%
exit /b 1

:run
call "%CORE_SCRIPT%" %MODE%
exit /b %errorlevel%
