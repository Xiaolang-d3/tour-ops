@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions EnableDelayedExpansion

for /F %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"
if defined ESC (
    set "RED=!ESC![91m"
    set "GREEN=!ESC![92m"
    set "YELLOW=!ESC![93m"
    set "CYAN=!ESC![96m"
    set "RESET=!ESC![0m"
) else (
    set "RED="
    set "GREEN="
    set "YELLOW="
    set "CYAN="
    set "RESET="
)

set "ROOT_DIR=%~dp0"
set "API_DIR=%ROOT_DIR%TourOps-api-server"
set "WEB_DIR=%ROOT_DIR%TourOps-web"
set "CONFIG_FILE=%API_DIR%\TourOps\config\config.yaml"
set "ERRORS=0"
set "EXIT_CODE=0"
set "MODE=%~1"
set "PYTHON_CMD="
set "API_SHOULD_START=1"
set "WEB_SHOULD_START=1"

if not defined MODE set "MODE=all"
call :resolve_python
call :banner

if /I "%MODE%"=="check" goto :do_check
if /I "%MODE%"=="install" goto :do_install
if /I "%MODE%"=="start" goto :do_start
if /I "%MODE%"=="start-api" goto :do_start_api
if /I "%MODE%"=="start-web" goto :do_start_web
if /I "%MODE%"=="all" goto :do_all

echo %RED%Unknown command: %MODE%%RESET%
echo Usage: deploy.bat [check^|install^|start^|start-api^|start-web^|all]
set "EXIT_CODE=1"
goto :done

:do_check
call :check_all
goto :done

:do_install
call :install_all
goto :done

:do_start
call :start_all
goto :done

:do_start_api
call :start_backend_only
goto :done

:do_start_web
call :start_frontend_only
goto :done

:do_all
call :check_all
if !ERRORS! gtr 0 (
    echo.
    echo %RED%[FAIL] Environment check failed with !ERRORS! issues.%RESET%
    goto :done
)
call :install_all
if !ERRORS! gtr 0 (
    echo.
    echo %RED%[FAIL] Dependency installation failed with !ERRORS! issues.%RESET%
    goto :done
)
call :start_all
goto :done

:check_all
echo.
echo %CYAN%========== Environment Check ==========%RESET%
call :check_dirs
call :check_config
call :check_node
call :check_python
call :check_pip
call :check_mysql
echo.
if !ERRORS! equ 0 (
    echo %GREEN%[PASS] All environment checks passed.%RESET%
) else (
    echo %RED%[FAIL] Found !ERRORS! issues.%RESET%
)
goto :eof

:check_dirs
if not exist "%API_DIR%" (
    echo %RED%  [X] Missing backend directory: TourOps-api-server\%RESET%
    set /a ERRORS+=1
) else (
    echo %GREEN%  [OK] Backend directory found%RESET%
)
if not exist "%WEB_DIR%" (
    echo %RED%  [X] Missing frontend directory: TourOps-web\%RESET%
    set /a ERRORS+=1
) else (
    echo %GREEN%  [OK] Frontend directory found%RESET%
)
goto :eof

:check_config
if exist "%CONFIG_FILE%" (
    echo %GREEN%  [OK] config.yaml found%RESET%
) else (
    echo %RED%  [X] Missing config file: %CONFIG_FILE%%RESET%
    set /a ERRORS+=1
)
goto :eof

:check_node
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%  [X] Node.js not found. Install from https://nodejs.org/%RESET%
    set /a ERRORS+=1
    goto :eof
)
for /f "usebackq delims=" %%v in (`node -v 2^>nul`) do set "NODE_VER=%%v"
echo %GREEN%  [OK] Node.js !NODE_VER!%RESET%

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%  [X] npm not found%RESET%
    set /a ERRORS+=1
) else (
    for /f "usebackq delims=" %%v in (`npm -v 2^>nul`) do set "NPM_VER=%%v"
    echo %GREEN%  [OK] npm !NPM_VER!%RESET%
)
goto :eof

:check_python
call :resolve_python
if not defined PYTHON_CMD (
    echo %RED%  [X] Python not found in PATH%RESET%
    set /a ERRORS+=1
    goto :eof
)
call :run_python --version > "%TEMP%\tourops_python_check.txt" 2>&1
if !errorlevel! neq 0 (
    echo %RED%  [X] Python launcher found but could not run Python%RESET%
    set /a ERRORS+=1
    goto :eof
)
set /p PY_VER=<"%TEMP%\tourops_python_check.txt"
echo %GREEN%  [OK] !PY_VER!%RESET%
goto :eof

:check_pip
if not defined PYTHON_CMD (
    echo %RED%  [X] pip unavailable until Python is installed%RESET%
    set /a ERRORS+=1
    goto :eof
)
call :run_pip --version > "%TEMP%\tourops_pip_check.txt" 2>&1
if !errorlevel! neq 0 (
    echo %RED%  [X] pip not available for the active Python interpreter%RESET%
    set /a ERRORS+=1
    goto :eof
)
for /f "tokens=2 delims= " %%v in ('type "%TEMP%\tourops_pip_check.txt"') do (
    echo %GREEN%  [OK] pip %%v%RESET%
    goto :eof
)
echo %GREEN%  [OK] pip available%RESET%
goto :eof

:check_mysql
if not exist "%CONFIG_FILE%" (
    echo %YELLOW%  [WARN] Skipping MySQL check because config.yaml is missing%RESET%
    goto :eof
)
if not defined PYTHON_CMD (
    echo %YELLOW%  [WARN] Skipping MySQL check until Python is available%RESET%
    goto :eof
)
call :run_python -c "import yaml,pymysql" >nul 2>&1
if !errorlevel! neq 0 (
    echo %YELLOW%  [WARN] Skipping MySQL check until backend dependencies are installed%RESET%
    goto :eof
)
call :run_python -c "import yaml; c=yaml.safe_load(open(r'%CONFIG_FILE%', encoding='utf-8')); db=c['database']; import pymysql; pymysql.connect(host=db['host'], port=int(db['port']), user=db['user'], password=str(db['password']), database=db['name']); print(f'{db[\"host\"]}:{db[\"port\"]}/{db[\"name\"]}')" > "%TEMP%\tourops_db_check.txt" 2>&1
if !errorlevel! equ 0 (
    set /p DB_INFO=<"%TEMP%\tourops_db_check.txt"
    echo %GREEN%  [OK] MySQL connection succeeded - !DB_INFO!%RESET%
    goto :eof
)
call :run_python -c "import yaml,socket; c=yaml.safe_load(open(r'%CONFIG_FILE%', encoding='utf-8')); db=c['database']; s=socket.create_connection((db['host'], int(db['port'])), 3); s.close(); print(f'{db[\"host\"]}:{db[\"port\"]}')" > "%TEMP%\tourops_db_check.txt" 2>&1
if !errorlevel! equ 0 (
    set /p DB_INFO=<"%TEMP%\tourops_db_check.txt"
    echo %YELLOW%  [WARN] MySQL port reachable but login/database validation failed - !DB_INFO!%RESET%
    goto :eof
)
echo %RED%  [X] MySQL connection failed. Check config.yaml and the MySQL service.%RESET%
set /a ERRORS+=1
goto :eof

:install_all
echo.
echo %CYAN%========== Install Dependencies ==========%RESET%

echo.
echo %CYAN%--- Backend dependencies (pip) ---%RESET%
if not exist "%API_DIR%\requirements.txt" (
    echo %RED%  [X] Missing requirements.txt%RESET%
    set /a ERRORS+=1
    goto :install_frontend
)
if not defined PYTHON_CMD (
    echo %RED%  [X] Cannot install backend dependencies because Python is unavailable%RESET%
    set /a ERRORS+=1
    goto :install_frontend
)
call :run_pip install -r "%API_DIR%\requirements.txt"
if !errorlevel! neq 0 (
    echo %RED%  [X] Backend dependency installation failed%RESET%
    set /a ERRORS+=1
) else (
    echo %GREEN%  [OK] Backend dependency installation finished%RESET%
)

:install_frontend
echo.
echo %CYAN%--- Frontend dependencies (npm) ---%RESET%
if not exist "%WEB_DIR%\package.json" (
    echo %RED%  [X] Missing package.json%RESET%
    set /a ERRORS+=1
    goto :eof
)
pushd "%WEB_DIR%"
npm install
if !errorlevel! neq 0 (
    echo %RED%  [X] Frontend dependency installation failed%RESET%
    set /a ERRORS+=1
) else (
    echo %GREEN%  [OK] Frontend dependency installation finished%RESET%
)
popd
goto :eof

:start_all
echo.
echo %CYAN%========== Start Services ==========%RESET%
set "API_SHOULD_START=1"
set "WEB_SHOULD_START=1"
call :start_backend
call :start_frontend

echo.
echo %CYAN%========== Health Check ==========%RESET%
call :health_check

echo.
if !ERRORS! equ 0 (
    echo %GREEN%========================================%RESET%
    echo %GREEN%  TourOps deployment succeeded.%RESET%
    echo %GREEN%  Frontend: http://localhost:3000%RESET%
    echo %GREEN%  Backend:  http://localhost:8000%RESET%
    echo %GREEN%  API Docs: http://localhost:8000/docs%RESET%
    echo %GREEN%========================================%RESET%
)
goto :eof

:start_backend_only
echo.
echo %CYAN%========== Start Backend ==========%RESET%
set "API_SHOULD_START=1"
set "WEB_SHOULD_START=0"
call :start_backend
if not defined PYTHON_CMD (
    echo %YELLOW%  [WARN] Skipping backend health check because Python is unavailable%RESET%
    goto :eof
)

echo.
echo %CYAN%========== Backend Health Check ==========%RESET%
call :health_check_backend
goto :eof

:start_frontend_only
echo.
echo %CYAN%========== Start Frontend ==========%RESET%
set "API_SHOULD_START=0"
set "WEB_SHOULD_START=1"
call :start_frontend
if not defined PYTHON_CMD (
    echo %YELLOW%  [WARN] Skipping frontend health check because Python is unavailable%RESET%
    goto :eof
)

echo.
echo %CYAN%========== Frontend Health Check ==========%RESET%
call :health_check_frontend
goto :eof

:start_backend

if not defined PYTHON_CMD (
    echo %RED%  [X] Python is required to start the backend%RESET%
    set /a ERRORS+=1
    goto :eof
)

call :check_port 8000
if !errorlevel! equ 1 (
    set "API_SHOULD_START=0"
    echo %YELLOW%  [WARN] Port 8000 is already in use. Skipping backend launch and validating the existing service later.%RESET%
    goto :eof
)

echo.
echo %CYAN%--- Starting FastAPI backend (port 8000) ---%RESET%
pushd "%API_DIR%"
start "TourOps-API" cmd /k "title TourOps-API && %PYTHON_CMD% -m uvicorn TourOps.main:app --reload --host 0.0.0.0 --port 8000"
popd

echo   Waiting for backend startup...
call :wait_for_service "http://localhost:8000/" 30
if !errorlevel! neq 0 (
    echo %RED%  [X] Backend startup timed out%RESET%
    set /a ERRORS+=1
) else (
    echo %GREEN%  [OK] Backend responded on http://localhost:8000%RESET%
)
goto :eof

:start_frontend
call :check_port 3000
if !errorlevel! equ 1 (
    set "WEB_SHOULD_START=0"
    echo %YELLOW%  [WARN] Port 3000 is already in use. Skipping frontend launch and validating the existing service later.%RESET%
    goto :eof
)

echo.
echo %CYAN%--- Starting Vite frontend (port 3000) ---%RESET%
pushd "%WEB_DIR%"
start "TourOps-Web" cmd /k "title TourOps-Web && npm run dev"
popd

echo   Waiting for frontend startup...
call :wait_for_service "http://localhost:3000/" 30
if !errorlevel! neq 0 (
    echo %YELLOW%  [WARN] Frontend may still be compiling. Check the TourOps-Web window.%RESET%
) else (
    echo %GREEN%  [OK] Frontend responded on http://localhost:3000%RESET%
)
goto :eof

:check_port
set "PORT=%~1"
netstat -ano 2>nul | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    exit /b 1
)
exit /b 0

:wait_for_service
set "URL=%~1"
set "TIMEOUT=%~2"
set "WAITED=0"
:wait_loop
if !WAITED! geq !TIMEOUT! exit /b 1
call :run_python -c "import urllib.request; urllib.request.urlopen(r'%URL%', timeout=2)" >nul 2>&1
if !errorlevel! equ 0 exit /b 0
timeout /t 2 /nobreak >nul
set /a WAITED+=2
goto :wait_loop

:health_check
call :health_check_backend
call :health_check_frontend
goto :eof

:health_check_backend
if not defined PYTHON_CMD (
    echo %YELLOW%  [WARN] Skipping backend health check because Python is unavailable%RESET%
    goto :eof
)

call :run_python -c "import urllib.request,json; r=urllib.request.urlopen('http://localhost:8000/', timeout=5); d=json.loads(r.read()); assert d.get('service') == 'TourOps API'" >nul 2>&1
if !errorlevel! equ 0 (
    echo %GREEN%  [OK] Backend API root responded normally%RESET%
) else (
    echo %RED%  [X] Backend API root check failed%RESET%
    set /a ERRORS+=1
)

call :run_python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/openapi.json', timeout=5)" >nul 2>&1
if !errorlevel! equ 0 (
    echo %GREEN%  [OK] OpenAPI schema reachable%RESET%
) else (
    echo %YELLOW%  [WARN] OpenAPI schema not reachable%RESET%
)
goto :eof

:health_check_frontend
if not defined PYTHON_CMD (
    echo %YELLOW%  [WARN] Skipping frontend health check because Python is unavailable%RESET%
    goto :eof
)

call :run_python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/', timeout=5)" >nul 2>&1
if !errorlevel! equ 0 (
    echo %GREEN%  [OK] Frontend page responded normally%RESET%
) else (
    if "!WEB_SHOULD_START!"=="0" (
        echo %RED%  [X] Frontend port was already in use, but the existing service did not respond correctly%RESET%
        set /a ERRORS+=1
    ) else (
        echo %YELLOW%  [WARN] Frontend page did not respond yet; it may still be compiling%RESET%
    )
)

call :run_python -c "import urllib.request,json; r=urllib.request.urlopen('http://localhost:3000/api/v1/openapi.json', timeout=5); json.loads(r.read())" >nul 2>&1
if !errorlevel! equ 0 (
    echo %GREEN%  [OK] Frontend proxy to backend responded normally%RESET%
) else (
    if "!WEB_SHOULD_START!"=="0" (
        echo %RED%  [X] Port 3000 is occupied, but the existing service does not proxy /api to the backend%RESET%
        set /a ERRORS+=1
    ) else (
        echo %YELLOW%  [WARN] Frontend proxy check failed; frontend may still be starting%RESET%
    )
)
goto :eof

:resolve_python
if defined PYTHON_CMD goto :eof
where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :eof
)
where py >nul 2>&1
if %errorlevel% neq 0 goto :eof
py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py -3"
    goto :eof
)
py --version >nul 2>&1
if %errorlevel% equ 0 set "PYTHON_CMD=py"
goto :eof

:run_python
if not defined PYTHON_CMD exit /b 9009
call %PYTHON_CMD% %*
exit /b %errorlevel%

:run_pip
call :run_python -m pip %*
exit /b %errorlevel%

:banner
echo %CYAN%============================================%RESET%
echo %CYAN%   TourOps Deployment Script (Windows Dev)%RESET%
echo %CYAN%============================================%RESET%
goto :eof

:done
echo.
if !ERRORS! gtr 0 set "EXIT_CODE=1"
endlocal & exit /b %EXIT_CODE%
