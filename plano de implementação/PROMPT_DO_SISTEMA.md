# 📄 PRONT DO SISTEMA: CriativosPro - Documentação Técnica e de Engenharia Reversa

Este documento é o guia definitivo e exaustivo do **CriativosPro**, uma plataforma de Inteligência Artificial de nível industrial projetada exclusivamente para ambiente **Desktop**. Aqui, cada linha de código, cada estrutura de pasta e cada decisão de design é explicada sem omissões ou resumos.

---

## 🏗️ 1. NATUREZA E TECNOLOGIA DO SISTEMA

O **CriativosPro** não é uma aplicação web. É um software **Desktop Nativo** construído sobre uma arquitetura híbrida de alto desempenho:
- **Linguagem de Backend:** Python 3.12+ (Focado em processamento, IA, segurança e I/O de arquivos).
- **Linguagem de Frontend:** TypeScript / JavaScript (React 19 + Electron).
- **Protocolo de Comunicação:** WebSockets de alta fidelidade (Socket.IO) para latência zero e streaming fluido.

---

## 📁 2. ESTRUTURA COMPLETA DE PASTAS E ARQUIVOS

### 2.1 Raiz do Projeto
- `criativospro.db`: Banco de dados principal (Configurações, Usuário, Histórico).
- `licenses.db`: Banco de dados isolado para validação de licenças e proteção antipirataria.
- `security.key`: Chave mestra de 256 bits gerada no primeiro boot para criptografia de dados sensíveis.
- `start_dev.bat`: Script de inicialização do ambiente de desenvolvimento (Inicia Backend e Frontend simultaneamente).
- `PROMPT_DO_SISTEMA.md`: Este documento de referência.

### 2.2 Core (O Motor Python)
Localizado em `/core/`, este é o cérebro lógico do software.

- **`main.py`**: O regente do sistema. Configura o servidor `aiohttp` e o `AsyncServer` do Socket.IO. Gerencia o startup paralelo dos provedores e os eventos globais de conexão.
- **`controller.py`**: A peça mais vital. Atua como o intermediário mestre. Quando uma mensagem chega, ele coordena a FSM, o histórico, o envio para a IA e a posterior geração de áudio (TTS).
- **`central_brain.py`**: Gerenciador de inteligência. Implementa um sistema de roteamento que permite trocar de modelo instantaneamente sem perder a sessão.
- **`database.py`**: Camada de persistência. Contém a lógica de criptografia AES para chaves de API e métodos otimizados de inserção/leitura.
- **`config.py`**: Repositório central de estados. Gerencia o que está ativado, o que está oculto e as preferências do usuário.
- **`history_manager.py`**: Gerente de memórias. Organiza conversas em sessões e gerencia o "context window" enviado para as IAs.
- **`fsm.py`**: Máquina de Estados Finita. Controla se o bot está `IDLE`, `PROCESSING`, `SPEAKING` ou em `ERROR`, garantindo que a interface reaja corretamente ao status do backend.
- **`title_generator.py`**: Serviço inteligente que resume a conversa em um título curto após a segunda interação do usuário.

### 2.3 Fornecedores de IA (`/core/providers/`)
Sistema modular de integração de LLMs.
- `base_provider.py`: Define a interface abstrata que todos os provedores DEVEM seguir.
- `provider_manager.py`: Fábrica de instâncias. É responsável pelo **Isolamento de Erros** (se um provedor falha, os outros permanecem intactos).
- Subpastas: `deepseek/`, `groq/`, `openrouter/`, `ollama/`, `lmstudio/`, `huggingface/`. Cada uma contém seu próprio `provider.py` (comunicação de baixo nível) e `brain.py` (lógica de alto nível).

---

## 🎨 3. DESIGN E EXPERIÊNCIA DO USUÁRIO (DESIGNER)

O design segue o conceito **Night Blue Glassmorphism**, criado para longas horas de uso sem fadiga ocular, transmitindo modernidade e potência.

### 3.1 Elementos Visuais
- **Paleta de Cores:** Deep Navy (#0a0f1e), Emerald Green para sucessos, Electric Blue para sistema e Crimson Red para erros.
- **Texturas:** Uso extensivo de `backdrop-filter: blur(20px)` e bordas semitransparentes (`rgba(255,255,255,0.05)`).
- **Tipografia:** Família de fontes *Inter* ou *Outfit* para máxima legibilidade e visual premium.

### 3.2 Estrutura de Mensagens
- **Usuário:** Balão alinhado à direita, cor sólida ou gradiente sutil, foco no conteúdo.
- **Sistemas/Bot:** Alinhado à esquerda, sem fundo ou com fundo ultra-traslúcido.
- **Organização:** Cada mensagem possui um avatar identificador e um timestamp sutil.

---

## ⚙️ 4. FUNCIONALIDADES DETALHADAS E LÓGICA INTERNA

### 4.1 Descoberta e Registro de Modelos
O sistema não possui uma lista estática de modelos. Ele implementa um **Sistema de Varredura Dinâmica**:
1. Ao inicializar, o `CentralBrain` percorre a pasta `core/providers`.
2. Para cada pasta, ele importa o `brain.py` e executa a função `create_brain`.
3. O provedor então faz uma chamada `list_models()` (seja local ou via API) para descobrir quais modelos estão disponíveis NAQUELA chave de API ou NQUELE hardware local.
4. O resultado é sincronizado com o frontend via evento `models_data`.

### 4.2 Ativação e Desativação de Modelos
No menu de configurações, o usuário pode escolher quais modelos deseja que apareçam no seletor principal.
- **Lógica:** O backend salva uma lista JSON em `settings.db` na chave `provider.enabled_models`.
- Quando o usuário abre o chat, o sistema filtra a lista total de modelos contra esta lista de habilitados.

### 4.3 Sistema de Métricas (O Triângulo de Performance)
Durante o streaming de cada resposta, o `Controller` monitora três variáveis críticas:
1. **Total de Tokens (TK):** Soma o `prompt_tokens` (enviado) + `completion_tokens` (gerado). Se a API for incompatível, o sistema conta caracteres e divide por 3 (estimativa precisa).
2. **Tokens por Segundo (TPS):** O sistema marca o tempo do primeiro chunk e do último. A fórmula é `Tokens Gerados / Segundos Decorridos`. Isso mede a velocidade pura da IA.
3. **Tempo Decorrido (⏱️):** Cronômetro exato desde o clique de enviar até o encerramento do socket.

### 4.4 Seleção de Provedor e Modelo
- **Provedor:** Define a "estrada" (ex: OpenRouter).
- **Modelo:** Define o "veículo" (ex: Gemini 2.0).
A seleção é persistente. Se você fechar o app no Groq/Llama-8B, ele abrirá exatamente lá no próximo boot.

### 4.5 Síntese de Voz Local (Piper TTS)
O sistema usa o motor **Piper** para emitir som sem depender de APIs pagas (como Google ou Azure).
- **Arquivos:** Localizados em `bin/piper/`.
- **Lógica de Silenciamento:** O texto é limpo de tags markdown e XML antes de ir para o Piper para evitar que o robô "leia" asteriscos ou colchetes.
- **Ajuste Fino:** O sistema configura `noise_scale` e `length_scale` para garantir uma voz humana e sem chiados metálicos.

---

## 🛠️ 5. INTEGRAÇÕES E BIBLIOTECAS (STACK COMPLETA)

### 5.1 Backend (Pip e Integrações)
- `aiohttp`: Motor principal para o servidor web e requisições HTTP assíncronas.
- `python-socketio`: Gerencia os canais de comunicação com o frontend.
- `openai (v1.12.0)`: Usada como ponte de comunicação para provedores compatíveis (Groq, DeepSeek, OpenRouter).
- `edge-tts`: Fallback para vozes na nuvem de alta qualidade.
- `cryptography (Fernet)`: Garante que, se alguém roubar seu banco de dados, não poderá ler suas API Keys.
- `sqlite3`: O gerenciador de dados padrão, escolhido pela robustez em sistemas desktop.

### 5.2 Frontend (Node e Electron)
- `electron`: Transforma o código web em uma aplicação `.exe` para Windows.
- `vite`: O bundler que compila o TypeScript e o React em milissegundos.
- `react-markdown`: Parser que transforma o texto da IA em tabelas, listas e blocos de código formatados.
- `lucide-react`: Fornece todos os ícones vetoriais da interface.
- `tailwindcss`: Motor de estilização que permite o design Glassmorphism sem sobrecarregar o renderizador.

---

## 🔄 6. CICLO DE VIDA DE UMA MENSAGEM (O PIPELINE)

1. **Captura:** O usuário pressiona Enter. O Frontend dispara um evento `send_message`.
2. **Registro:** O `HistoryManager` grava o prompt no DB. O `Controller` altera a FSM para `PROCESSING`.
3. **Contexto:** O `OpenAIAdapter` formata as últimas 10 conversas para que a IA tenha memória.
4. **Streaming:** O Provedor abre uma conexão long-lived. Cada pedaço de texto é emitido instantaneamente para o usuário.
5. **Finalização:** A resposta é salva. O `TitleGenerator` entra em cena se for a primeira mensagem.
6. **Métricas:** Os badges de TK, TPS e Tempo aparecem no rodapé da mensagem assim que o streaming termina.
7. **Áudio:** Se o ícone de som estiver ativo, o `TTSService` converte o texto final em ondas sonoras via Piper e toca no alto-falante do usuário.

---

Este PRONT DO SISTEMA é a autoridade máxima sobre a implementação do CriativosPro. Qualquer modificação futura deve respeitar estas definições de arquitetura e isolamento.
