import subprocess
import sys
import os

def clone_repo(repo_url):
    try:
        print(f"\n📥 Clonando repositório:")
        print(repo_url)
        print("\n⏳ Progresso:\n")

        process = subprocess.Popen(
            ["git", "clone", "--progress", repo_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Mostra saída em tempo real (progresso)
        for line in process.stdout:
            print(line, end="")

        process.wait()

        if process.returncode == 0:
            print("\n✅ Clone concluído com sucesso!")
        else:
            print("\n❌ Erro ao clonar o repositório.")

    except FileNotFoundError:
        print("❌ Git não encontrado. Instale o Git e adicione ao PATH.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    print("=== GitHub Repository Downloader ===")
    repo_url = input("🔗 Informe a URL do repositório GitHub: ").strip()

    if not repo_url:
        print("❌ URL inválida.")
        sys.exit(1)

    clone_repo(repo_url)
