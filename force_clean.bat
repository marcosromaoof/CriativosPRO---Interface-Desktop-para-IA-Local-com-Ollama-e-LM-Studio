@echo off
echo [LIMPEZA FORCADA] Iniciando remocao de artefatos de build...

rem Matar processos que podem travar arquivos
taskkill /F /IM "criativospro-engine.exe" >nul 2>&1
taskkill /F /IM "electron.exe" >nul 2>&1
taskkill /F /IM "node.exe" >nul 2>&1

rem Aguardar liberação
timeout /t 2 /nobreak >nul

rem Limpar pastas de build do Electron
if exist "frontend\dist" rd /s /q "frontend\dist"
if exist "frontend\build" rd /s /q "frontend\build"
if exist "frontend\release" rd /s /q "frontend\release"

rem Limpar pastas de build do Backend (PyInstaller)
if exist "backend\dist" rd /s /q "backend\dist"
if exist "backend\build" rd /s /q "backend\build"
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"

rem Limpar arquivos de especificacao
if exist "*.spec" del /f /q "*.spec"
if exist "backend\*.spec" del /f /q "backend\*.spec"

rem Limpar caches Python de forma recursiva
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

rem Limpar banco de dados local e chaves
if exist "criativospro.db" del /f /q "criativospro.db"
if exist "security.key" del /f /q "security.key"
if exist "backend\criativospro.db" del /f /q "backend\criativospro.db"
if exist "backend\security.key" del /f /q "backend\security.key"

echo [LIMPEZA FORCADA] Concluida.
