import os
import subprocess
from datetime import datetime

# ============================================
#  🚀 SCRIPT AUTOMÁTICO DE DEPLOY PARA GITHUB
# ============================================

def run(cmd):
    """Executa comando e mostra saída em tempo real."""
    print(f"\n👉 Executando: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    return result.returncode == 0


def main():
    print("\n==============================")
    print("🚀 INICIANDO DEPLOY AUTOMÁTICO")
    print("==============================\n")

    # 1. Garantir que estamos na pasta do projeto
    project_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_path)
    print(f"📂 Diretório do projeto: {project_path}")

    # 2. Ativar ambiente virtual automaticamente (Windows)
    venv_activate = os.path.join(project_path, "venv", "Scripts", "activate")
    if os.path.exists(venv_activate):
        print(f"✔ venv detectado: {venv_activate}")
    else:
        print("❌ ERRO: Ambiente virtual não encontrado! Crie com:")
        print("python -m venv venv")
        return

    # 3. Adicionar mudanças
    if not run("git add ."):
        print("❌ Falha no git add")
        return

    # 4. Criar mensagem automática de commit com data/hora
    commit_message = f"Atualizacao automatica {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    if not run(f'git commit -m "{commit_message}"'):
        print("ℹ Nenhuma alteração para commitar.")
        return

    # 5. Enviar para GitHub
    if not run("git push"):
        print("❌ Falha no git push")
        return

    print("\n🎉 DEPLOY REALIZADO COM SUCESSO!")
    print("🌐 Acesse no Streamlit Cloud: (o redeploy inicia automaticamente)")
    print("===============================================")


if __name__ == "__main__":
    main()
