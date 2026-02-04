import os
import subprocess
import sys
import threading
import time
import shutil

# --- Configurações de Caminhos ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
PIPER_DIR = os.path.join(BACKEND_DIR, "bin", "piper")
PYTHON_EXE = sys.executable

def print_banner():
    banner = """
===========================================================
      CRIATIVOS PRO - SISTEMA DE CONFIGURAÇÃO E START
===========================================================
    """
    print(banner)

def run_command(command, cwd=None, env=None, shell=True):
    """Executa um comando e retorna se teve sucesso."""
    try:
        subprocess.run(command, cwd=cwd, env=env, shell=shell, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERRO] Falha ao executar: {' '.join(command) if isinstance(command, list) else command}")
        print(f"       Código de erro: {e.returncode}")
        return False

def check_requirements():
    print("\n[1/4] Verificando requisitos fundamentais...")
    
    # 1. Verificar NPM
    print("[-] Verificando Node.js/NPM...")
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, check=True, shell=True, text=True)
        print(f"[OK] NPM Versão {result.stdout.strip()} detectada.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n[ERRO CRÍTICO] NPM não encontrado!")
        print("      O Node.js é essencial para a interface gráfica.")
        print("      Por favor, baixe em: https://nodejs.org/")
        input("\nPressione Enter para sair...")
        sys.exit(1)

    # 2. Verificar Pasta de Áudio Temp
    audio_temp = os.path.join(BACKEND_DIR, "temp_audio")
    if not os.path.exists(audio_temp):
        print("[-] Criando pasta de áudio temporário...")
        os.makedirs(audio_temp)

def install_dependencies():
    print("\n[2/4] Instalando dependências do projeto...")

    # 1. Backend Python
    print("\n[+] Atualizando dependências Python (PIP)...")
    req_file = os.path.join(BACKEND_DIR, "requirements.txt")
    if os.path.exists(req_file):
        if not run_command([PYTHON_EXE, "-m", "pip", "install", "-r", "requirements.txt"], cwd=BACKEND_DIR):
            print("[AVISO] Algumas dependências Python podem ter falhado ao instalar.")
    else:
        print("[ERRO] Arquivo backend/requirements.txt não encontrado!")

    # 2. Frontend Node.js
    print("\n[+] Instalando dependências da Interface (NPM)...")
    print("    Isso pode levar alguns minutos na primeira vez...")
    
    # Sempre rodamos npm install para garantir que tudo esteja sincronizado
    if not run_command(["npm", "install"], cwd=FRONTEND_DIR):
        print("\n[ERRO] Falha ao instalar dependências do NPM.")
        print("       Verifique sua conexão com a internet.")
        input("\nPressione Enter para sair...")
        sys.exit(1)
    print("[OK] Dependências do frontend prontas.")

def check_engine():
    print("\n[3/4] Verificando Motor de Voz (Piper)...")
    piper_exe = os.path.join(PIPER_DIR, "piper.exe" if os.name == 'nt' else "piper")
    model_file = os.path.join(PIPER_DIR, "pt_BR-faber-medium.onnx")

    if not os.path.exists(piper_exe) or not os.path.exists(model_file):
        print("[AVISO] Motor de voz Piper ou modelo de voz não encontrado.")
        print(f"        Caminho esperado: {PIPER_DIR}")
        print("        A aplicação funcionará, mas sem narração de voz.")
    else:
        print("[OK] Motor de voz detectado e pronto.")

def launch():
    print("\n[4/4] Iniciando Criativos Pro...")
    
    # Configurar ambiente do Backend
    env = os.environ.copy()
    env["PYTHONPATH"] = BACKEND_DIR
    main_py = os.path.join(BACKEND_DIR, "core", "main.py")

    # Iniciar processos
    print("[+] Lançando Cérebro (Backend)...")
    backend_proc = subprocess.Popen([PYTHON_EXE, main_py], cwd=PROJECT_ROOT, env=env)
    
    print("[+] Lançando Interface (Frontend)...")
    # No Windows usamos shell=True para o npm
    frontend_proc = subprocess.Popen(["npm", "run", "start"], cwd=FRONTEND_DIR, shell=True)

    print("\n===========================================================")
    print("      SISTEMA ONLINE! BOAS CRIAÇÕES!")
    print("      Pressione CTRL+C neste terminal para encerrar.")
    print("===========================================================\n")

    try:
        while True:
            if backend_proc.poll() is not None:
                print("[!] O Backend parou de responder.")
                break
            if frontend_proc.poll() is not None:
                print("[!] A Interface foi fechada.")
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[!] Encerrando processos...")
    finally:
        # Tentar matar tudo de forma limpa
        if backend_proc: backend_proc.terminate()
        if frontend_proc:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(frontend_proc.pid)], capture_output=True)
            else:
                frontend_proc.terminate()
        print("[!] Criativos Pro encerrado.")

if __name__ == "__main__":
    print_banner()
    check_requirements()
    install_dependencies()
    check_engine()
    launch()
