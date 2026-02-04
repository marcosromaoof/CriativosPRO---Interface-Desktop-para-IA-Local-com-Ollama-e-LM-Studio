import os
import shutil
import glob

def clean_project():
    print("Iniciando limpeza do projeto (Preparacao para Build)...")
    
    # Arquivos a serem removidos
    files_to_remove = [
        "criativospro.db",
        "security.key",
        "backend/criativospro.db", # Caso esteja aqui
        "backend/security.key"
    ]
    
    # Pastas a serem limpas (conteúdo e a própria pasta se possível)
    folders_to_clean = [
        "backend/temp_audio",
        "dist",
        "build",
        "backend/dist",
        "backend/build",
        "frontend/dist",
        "frontend/build",
        "release"
    ]
    
    # Padroes globais para remover recursivamente
    patterns_to_remove = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.spec"
    ]

    base_dir = os.getcwd()

    # 1. Remover Arquivos Especificos
    for file_path in files_to_remove:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f"[REMOVIDO] {file_path}")
            except Exception as e:
                print(f"[ERRO] Falha ao remover {file_path}: {e}")

    # 2. Limpar Conteudo de Pastas
    for folder in folders_to_clean:
        full_path = os.path.join(base_dir, folder)
        if os.path.exists(full_path):
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    print(f"[LIMPO] Conteudo de {folder}")
                except Exception as e:
                    print(f"[ERRO] Falha ao limpar {folder}: {e}")

    # 3. Remover Padroes Recursivos (__pycache__)
    for pattern in patterns_to_remove:
        for match in glob.glob(os.path.join(base_dir, pattern), recursive=True):
            try:
                if os.path.isdir(match):
                    shutil.rmtree(match)
                else:
                    os.remove(match)
                print(f"[REMOVIDO] {match}")
            except Exception as e:
                print(f"[ERRO] Falha ao remover {match}: {e}")

    print("Limpeza concluida com sucesso!")

if __name__ == "__main__":
    clean_project()
