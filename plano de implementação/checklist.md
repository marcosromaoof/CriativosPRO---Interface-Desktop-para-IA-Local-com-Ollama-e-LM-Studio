# ✅ Checklist de Implementação: CriativosPro Desktop

Este arquivo acompanha o progresso do desenvolvimento, fase por fase. Marque com `[x]` conforme os itens forem completados.

---

## 📅 Fase 1: Configuração do Ambiente e Estrutura Inicial
- [x] **1.1 Estrutura de Diretórios**
    - [x] Criar `/backend/core` (Backend)
    - [x] Criar `/backend/core/providers`
    - [x] Criar `/bin/piper`
    - [x] Criar `/frontend` (Pasta do Electron/React)
- [x] **1.2 Configuração do Backend (Python)**
    - [x] Criar `requirements.txt` (`aiohttp`, `python-socketio`, `openai`, `edge-tts`, `cryptography`)
    - [x] Configurar ambiente virtual (`venv`) - *Opcional/Automático*
- [x] **1.3 Configuração do Frontend (Node/Electron)**
    - [x] Inicializar projeto Vite + React + TypeScript
    - [x] Instalar `electron`, `electron-builder`
    - [x] Instalar dependências UI (`react-markdown`, `lucide-react`, `socket.io-client`, `tailwindcss`)
    - [x] Configurar `tailwind.config.js` (Paleta "Night Blue")
- [x] **1.4 Scripts**
    - [x] Criar `start_dev.bat` para boot simultâneo

## 🧠 Fase 2: Implementação do Core (Backend Python)
- [x] **2.1 Camada de Dados**
    - [x] Implementar `database.py` (conexão SQLite)
    - [x] Criar tabelas: `settings`, `history`, `licenses`
    - [x] Implementar criptografia AES para chaves de API
- [x] **2.2 Gerenciamento de Estado**
    - [x] Implementar `fsm.py` (Máquina de Estados: IDLE, PROCESSING, SPEAKING)
    - [x] Implementar `history_manager.py` (Context Window)
- [x] **2.3 Motor Principal**
    - [x] Implementar `main.py` (Server Setup)
    - [x] Implementar `controller.py` (Event Loop & Socket Events)

## 🎨 Fase 3: Frontend e Design System
- [x] **3.1 Fundação Visual (`index.css`)**
    - [x] Definir tokens de cores (Deep Navy, Emerald Green, etc.)
    - [x] Classes utilitárias (Glassmorphism)
- [x] **3.2 App Shell**
    - [x] Criar Sidebar (Navegação/Histórico)
    - [x] Criar Layout Principal
    - [x] Configurar Janela Frameless do Electron
- [x] **3.3 Componentes de Chat**
    - [x] `MessageBubble` (Renderização Markdown)
    - [x] Badges de métricas (TK/s, Tempo)

## 🔌 Fase 4: Integração de Provedores de IA
- [x] **4.1 Arquitetura Base**
    - [x] `base_provider.py` (Interface)
    - [x] `provider_manager.py` (Factory)
- [x] **4.2 Scanner de Modelos**
    - [x] `central_brain.py` (Descoberta Dinâmica)
    - [x] Sincronização Backend -> Frontend
- [x] **4.3 Provedores Iniciais**
    - [x] Implementar `openrouter/`
    - [x] Implementar `deepseek/`
    - [x] Implementar `groq/`

## 🗣️ Fase 5: Áudio e TTS (Piper)
- [x] **5.1 Backend Áudio**
    - [x] Implementar `tts_service.py` (Piper wrapper)
    - [x] Lógica de limpeza de texto (Regex)
    - [x] Integrar TTS no Ciclo do Controller
- [x] **5.2 Frontend Áudio**
    - [x] Player de áudio (Socket integration)
    - [x] Controles (Play/Pause/Mute)
    - [x] Servidor de arquivos estáticos para áudio (.wav)

## 🚀 Fase 6: Polimento e Finalização
- [x] **6.1 Features Extras**
    - [x] `title_generator.py` (Resumo automático de conversa)
    - [x] Tela de Settings (Gerenciamento de Chaves de API)
- [x] **6.2 Testes Finais**
    - [x] Validação de Fluxo Completo (E2E)
    - [x] Persistência de Dados (API Keys Criptografadas)
