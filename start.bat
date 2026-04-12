echo Creando entorno si no existe...
if not exist venv (
    python -m venv venv
)

@echo off
cd /d C:\Users\jorge.sabattin\proyectos_python\hotel_system

echo ==========================
echo INICIANDO SISTEMA DJANGO
echo ==========================

REM 🔥 Usar Python del entorno SIEMPRE
set PYTHON=venv\Scripts\python.exe

echo.
echo [1] Verificando entorno...
if not exist %PYTHON% (
    echo ERROR: No existe el entorno virtual (venv)
    pause
    exit
)

echo OK

echo.
echo [2] Ejecutando migraciones...
%PYTHON% manage.py makemigrations
%PYTHON% manage.py migrate

echo.
echo [3] Iniciando servidor...
%PYTHON% manage.py runserver

pause