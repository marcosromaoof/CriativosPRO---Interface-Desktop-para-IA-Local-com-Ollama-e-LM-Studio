@echo off
TITLE CriativosPro - Ambiente de Desenvolvimento

echo ==========================================
echo    CRIATIVOSPRO - START DEV ENVIRONMENT
echo ==========================================

:: 1. Instalar dependências do Python (Backend)
echo [+] Verificando dependencias Python (Backend)...
cd backend
pip install -r requirements.txt
cd ..

:: 2. Iniciar Backend em segundo plano
echo [+] Iniciando Backend em segundo plano...
start /B cmd /c "set PYTHONPATH=%CD%\backend && python backend/core/main.py"

:: 3. Iniciar Frontend (Vite + Electron)
echo [+] Iniciando Frontend...
cd frontend
npm run start

pause
