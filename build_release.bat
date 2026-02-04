@echo off
echo ==========================================
echo      CRIATIVOSPRO - BUILD SYSTEM
echo ==========================================

echo [1/5] Executando limpeza de dados pessoais e cache...
call force_clean.bat

echo [2/5] Verificando dependencias de build...
pip install pyinstaller --quiet

echo [3/5] Compilando CriativosPro Engine (Backend Python)...
if not exist "backend\dist" mkdir "backend\dist"

rem Compila o backend em um executavel unico
pyinstaller --noconfirm --log-level=WARN --onefile --windowed --name "criativospro-engine" --clean --paths "backend" ^
 --hidden-import "engineio.async_drivers.aiohttp" ^
 --hidden-import "core.providers.base_provider" ^
 --hidden-import "core.providers.deepseek.provider" --hidden-import "core.providers.deepseek.brain" ^
 --hidden-import "core.providers.groq.provider" --hidden-import "core.providers.groq.brain" ^
 --hidden-import "core.providers.openrouter.provider" --hidden-import "core.providers.openrouter.brain" ^
 --hidden-import "core.providers.ollama.provider" --hidden-import "core.providers.ollama.brain" ^
 --hidden-import "core.providers.lmstudio.provider" --hidden-import "core.providers.lmstudio.brain" ^
 --hidden-import "core.providers.huggingface.provider" --hidden-import "core.providers.huggingface.brain" ^
 --add-data "backend/core/providers;core/providers" ^
 "backend/core/main.py"

if not exist "dist\criativospro-engine.exe" (
    echo [ERRO CRITICO] O executavel do backend nao foi gerado.
    pause
    exit /b 1
)

rem Move para o local esperado pelo Electron Builder
move /Y "dist\criativospro-engine.exe" "backend\dist\criativospro-engine.exe"
echo [SUCESSO] Engine compilada: backend\dist\criativospro-engine.exe

echo [4/5] Instalando dependencias do Frontend...
cd frontend
call npm install

echo [5/5] Construindo interface e gerando instalador (.exe)...
call npm run dist

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha no build do Electron.
    pause
    exit /b 1
)

echo [6/6] Organizando arquivos finais...
if not exist "release" mkdir "release"

rem Move Setup normal
if exist "frontend\dist\CriativosPro Setup 4.4.21.exe" move /Y "frontend\dist\CriativosPro Setup 4.4.21.exe" "release\"

rem Move Portable (pode ter nomes variados dependendo do builder)
if exist "frontend\dist\CriativosPro Portable 4.4.21.exe" move /Y "frontend\dist\CriativosPro Portable 4.4.21.exe" "release\"

rem Move qualquer outro .exe útil (como fallback)
move /Y "frontend\dist\*.exe" "release\" 2>nul

echo.
echo ==========================================
echo      BUILD FINALIZADO COM SUCESSO!
echo ==========================================
echo Os instaladores estao na pasta: release/
echo Procure por: CriativosPro Setup 4.4.21.exe
echo.
pause
