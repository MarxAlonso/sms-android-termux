@echo off
echo ======================================================
echo   Construyendo Panel de Envio de Correos (.exe)
echo ======================================================
echo.

echo [1/3] Instalando dependencias necesarias...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [2/3] Generando ejecutable...
echo (Esto puede tardar un par de minutos)
pyinstaller --noconfirm --onefile --windowed --name "PanelCorreos" --add-data ".env;." main.py

echo.
echo [3/3] Limpiando archivos temporales...
if exist "build" rmdir /s /q "build"
if exist "PanelCorreos.spec" del /q "PanelCorreos.spec"

echo.
echo ======================================================
echo   PROCESO COMPLETADO!
echo.
echo   Tu aplicacion esta lista en la carpeta 'dist'
echo   Archivo: dist\PanelCorreos.exe
echo ======================================================
pause
