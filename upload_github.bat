@echo off
TITLE Criativos Pro - Upload para GitHub
SETLOCAL EnableDelayedExpansion

echo ===========================================
echo       CRIATIVOS PRO - GITHUB UPLOAD
echo ===========================================
echo [!] Pressione qualquer tecla para iniciar o processo...
pause >nul

:: Verificar se o Git está instalado
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Git nao encontrado. Instale o Git em https://git-scm.com/
    pause
    exit /b
)

:: Limpeza prévia de arquivos desnecessários
echo [+] Realizando limpeza de arquivos temporarios...
if exist "frontend\dist" rmdir /s /q "frontend\dist"
if exist "backend\__pycache__" rmdir /s /q "backend\__pycache__"
if exist "backend\core\__pycache__" rmdir /s /q "backend\core\__pycache__"
if exist "backend\temp_audio" (
    del /q "backend\temp_audio\*"
)

:: Inicializar Git se necessário
if not exist ".git" (
    echo [+] Inicializando novo repositorio Git...
    git init
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao iniciar Git.
        pause
        exit /b
    )
)

:: Verificar ou Redefinir Remote
git remote get-url origin >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [!] Repositorio remoto atual:
    git remote get-url origin
    set /p reset_remote="[?] Deseja trocar a URL do repositorio? (s/n): "
    if /I "!reset_remote!"=="s" (
        git remote remove origin
        echo [+] Remote removido.
    )
)

:: Se nao tem remote (ou foi removido acima), pede um novo
git remote get-url origin >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] Configurando novo repositorio remoto...
    set /p repo_url="[?] Cole a NOVA URL do GitHub: "
    if "!repo_url!"=="" (
        echo [ERRO] URL necessaria para continuar.
        pause
        exit /b
    )
    git remote add origin "!repo_url!"
)

:: Adicionar arquivos
echo [+] Adicionando arquivos...
git add .

:: Commit
echo [+] Criando commit...
set /p commit_msg="[?] Mensagem do commit (Deixe vazio para padrao): "
if "%commit_msg%"=="" set commit_msg=update: criativospro source code
git commit -m "%commit_msg%" >nul 2>nul
echo [+] Verificando estado dos arquivos...

:: Push
echo [+] Enviando para o GitHub (Main branch)...
git branch -M main
git push -u origin main

:: Verificar erro no Push
if %ERRORLEVEL% EQU 0 goto :SUCCESS

echo.
echo [!] O Push normal falhou.
echo [!] Isso acontece se o GitHub ja tiver arquivos (como README ou LICENSE).
set /p force_p="[?] Deseja FORCAR o envio (sobrescrever o GitHub)? (s/n): "

if /I "!force_p!"=="s" (
    echo [+] Tentando Force Push...
    git push -u origin main --force
    if !ERRORLEVEL! EQU 0 (
        goto :SUCCESS
    ) else (
        echo [ERRO] Falha critica no envio.
    )
) else (
    echo [!] Upload cancelado pelo usuario.
)

goto :END

:SUCCESS
echo.
echo [SUCESSO] Codigo enviado com sucesso!

:END
pause
