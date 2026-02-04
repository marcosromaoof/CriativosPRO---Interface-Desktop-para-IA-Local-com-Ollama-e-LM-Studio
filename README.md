# Criativos Pro - Sistema Neural de Inteligência Artificial

![Criativos Pro Banner](https://img.shields.io/badge/Criativos--Pro-Powered%20by%20AI-blue?style=for-the-badge&logo=openai)
![Status](https://img.shields.io/badge/Status-Desenvolvimento-green?style=for-the-badge)

O **Criativos Pro** é uma interface desktop de elite projetada para transformar a interação com Modelos de Linguagem de Larga Escala (LLMs) locais em uma experiência premium, rápida e focada em privacidade.

## ✨ Diferenciais do Sistema

* **⚡ Latência Zero (Interface)**: Respostas renderizadas com efeitos visuais de alta performance que acompanham o raciocínio da IA em tempo real.
* **🎙️ Voz Neural Piper**: Narração de texto integrada usando tecnologia Piper TTS local (totalmente offline).
* **🧠 Foco Local & Privado**: Suporte nativo para **Ollama** e **LM Studio**. Seus dados nunca saem da sua máquina.
* **📊 Dashboard de Performance**: Acompanhe consumo de tokens, velocidade (TPS) e latência de cada geração.
* **📁 Smart History**: Gerenciamento inteligente de sessões com salvamento automático baseado na relevância do conteúdo.

## 🛠️ Requisitos do Sistema

Antes de iniciar, certifique-se de ter instalado:

1. **[Node.js (LTS)](https://nodejs.org/)**: Motor para a interface gráfica.
2. **[Python 3.10 ou superior](https://www.python.org/)**: Motor para o cérebro (backend) do sistema.
3. **Motores de IA (Recomendado pelo menos um)**:
    * [Ollama](https://ollama.com/) (Rodando na porta padrão 11434).
    * [LM Studio](https://lmstudio.ai/) (Com servidor local ativado na porta 1234).

## 🚀 Como Executar

O Criativos Pro possui um sistema de inicialização unificado que cuida de tudo para você.

1. **Clone o repositório:**

    ```bash
    git clone https://github.com/SEU-USUARIO/nome-do-repositorio.git
    cd criativospro-2.0
    ```

2. **Inicie o sistema:**

    ```bash
    python setup.py
    ```

> **O que o `setup.py` faz?**
>
> * Verifica se o Node.js e Python estão instalados.
> * Instala automaticamente todas as dependências do Backend (PIP).
> * Instala automaticamente as dependências da Interface (NPM).
> * Inicia o Backend e a Interface simultaneamente.

## ⚙️ Configuração

Ao abrir o sistema, acesse o menu de **Configurações** para:

* Selecionar entre Ollama ou LM Studio.
* Sincronizar seus modelos locais.
* Configurar Prompts de Sistema para personalizar o comportamento da IA.
* Editar seu perfil de usuário para respostas mais personalizadas.

## 🤝 Contribuição

Este é um projeto de alta performance. Sinta-se à vontade para abrir Issues ou enviar Pull Requests para melhorias na renderização, novos drivers de áudio ou otimizações de banco de dados.

---
Desenvolvido por **Criativos Pro Inc**.
