@echo off
cd C:\Users\jorge.sabattin\proyectos_python\hotel_system

echo Activando entorno virtual...
call venv\Scripts\activate

echo Levantando servidor Django...
python manage.py runserver

pause