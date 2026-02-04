# 📘 Manual do Usuário - CriativosPro Desktop (v4.4.21)

Bem-vindo ao **CriativosPro Desktop**, sua central neural de inteligência artificial. Este manual guiará você desde a instalação até o uso avançado dos múltiplos modelos cognitivos disponíveis.

---

## 🚀 1. Instalação e Configuração Inicial

### 1.1 Instalação
1.  Localize o arquivo instalador: `CriativosPro Setup 4.4.21.exe`.
2.  Execute o arquivo. O instalador copiará os arquivos necessários e criará um atalho na sua Área de Trabalho e Menu Iniciar.
3.  Opcionalmente, se preferir não instalar, use a versão `CriativosPro Portable 4.4.21.exe` que roda diretamente de qualquer pasta (ideal para pen drives).

### 1.2 Primeiro Acesso
Ao abrir o aplicativo pela primeira vez:
*   O sistema iniciará o motor neural em segundo plano (pode levar de 5 a 10 segundos).
*   Você verá a tela principal com o "Neural Link" ativo (indicador verde no canto superior direito).

---

## ⚙️ 2. Configurando seus Motores de IA (Providers)

O CriativosPro suporta múltiplos fornecedores de IA. Para configurá-los:

1.  Clique no ícone de **Engrenagem** (⚙️) no canto inferior esquerdo.
2.  Navegue até a aba **Motores Cognitivos** (ícone de Processador/Chip).
3.  Selecione o provedor desejado na lista horizontal:

### 🌐 Provedores Online (Requerem Chave de API)

*   **DeepSeek:** (Padrão) Excelente para raciocínio e código. Insira sua `API Key`.
*   **Groq:** Focado em velocidade extrema.
*   **OpenRouter:** Acesso unificado a Claude, GPT-4, Llama 3, etc.
*   **HuggingFace:** Acesso a modelos open-source hospedados na nuvem.

> **Nota:** As chaves são salvas localmente e criptografadas no seu computador (`%APPDATA%/CriativosPro/`).

### 🏠 Provedores Locais (Privacidade Total - Sem Internet)

O sistema detecta automaticamente se estes softwares estão rodando no seu PC:

*   **Ollama:** Certifique-se de que o Ollama está instalado e rodando (`http://localhost:11434`).
*   **LM Studio:** Certifique-se de iniciar o "Local Server" no LM Studio (`http://localhost:1234`).

Após inserir a chave ou iniciar o servidor local, clique em **"Sincronizar Modelos"**. O sistema listará os modelos disponíveis para uso imediato.

---

## 💬 3. Usando o Chat

### 3.1 Seleção de Modelo
No topo da tela, existem dois seletores principais:
1.  **Engine (Motor):** Escolha o provedor (ex: DeepSeek, Ollama).
2.  **Arquitetura:** Escolha o modelo específico (ex: `deepseek-chat`, `llama3`).

### 3.2 Interação
*   Digite sua mensagem na barra inferior.
*   Use `Shift + Enter` para quebrar linha.
*   Pressione `Enter` ou clique no avião de papel para enviar.

### 3.3 Ferramentas de Mensagem
Ao passar o mouse sobre uma resposta da IA, você verá opções:
*   📋 **Copiar:** Copia o texto para a área de transferência.
*   💾 **Baixar:** Salva o conteúdo em um arquivo de texto `.txt`.
*   🔊 **Ouvir (TTS):** O sistema lê a resposta em voz alta usando síntese neural local (funciona offline).
    *   *Dica:* O botão de áudio fica sempre visível ao lado das respostas do bot.

---

## 🧠 4. Personalização (Cérebro e Prompts)

Na aba **Configurações > Cérebro e Prompts**, você pode definir como a IA deve se comportar:

*   **Instruções Customizadas (Perfil):** Defina seu nome, profissão e preferências (ex: "Sou programador Python, prefira respostas técnicas").
*   **Prompt Geral do Sistema:** A "personalidade" base de todos os modelos.
*   **Prompts Específicos:** Defina comportamentos únicos para modelos locais (Ollama/LM Studio).

---

## ❓ 5. Solução de Problemas Comuns

**"Neural Link" fica vermelho ou desconectado**
*   Aguarde alguns segundos; o motor backend pode estar reiniciando.
*   Verifique se não há outro aplicativo usando a porta `5678`.

**Erro ao Listar Modelos (Ollama/LM Studio)**
*   Verifique se o software (Ollama ou LM Studio) está realmente aberto e com o servidor ativado.
*   Tente clicar em "Sincronizar Modelos" novamente nas configurações.

**Áudio não funciona**
*   Certifique-se de que suas caixas de som estão ligadas.
*   O áudio é gerado localmente; em computadores muito lentos, pode levar alguns segundos para começar a falar.

**O aplicativo não abre ou fecha sozinho**
*   Verifique se o antivírus não bloqueou o executável (adicione como exceção se necessário).
*   Certifique-se de ter extraído todo o conteúdo se estiver usando a versão Portable.

---

**Suporte:** suporte@criativospro.com
**Desenvolvido por:** CriativosPro Inc.
