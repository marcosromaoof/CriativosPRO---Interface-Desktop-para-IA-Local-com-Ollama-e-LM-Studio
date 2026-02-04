# 🛠️ Plano de Refinamento: Histórico e Persistência

Este plano aborda a implementação do carregamento de sessões antigas e a correção definitiva da persistência de mensagens irrelevantes.

## 🟥 Fase 1: Carregamento de Sessões
**Problema**: Clicar na sessão na sidebar não faz nada. Backend não tem rota para buscar mensagens.
**Solução**: Implementar pipeline completo de carregamento.

- [x] **1.1 Backend - HistoryManager**
    - [x] Criar método `get_full_history(session_id)`: Retorna todas as mensagens ordenadas (sem limite de contexto).

- [x] **1.2 Backend - Socket Event**
    - [x] Criar evento `load_session` em `main.py`.
    - [x] Retornar payload: `{'session_id': id, 'messages': [...]}`.

- [x] **1.3 Frontend - Integração**
    - [x] Implementar `handleLoadSession(id)` no `App.tsx`.
        - [x] Limpar estado atual? Ou transição suave?
        - [x] Atualizar `messages` e `currentSessionId`.
    - [x] Conectar handler ao botão da Sidebar.

- [x] **1.4 Correção: Carregamento Inicial (`App.tsx`)**
    - [x] Adicionar `socket.emit('get_sessions')` no evento `connect` ou no `useEffect` de inicialização para garantir que a sidebar carregue ao abrir o app.

## 🟧 Fase 2: Correção de Persistência ("Oi")
**Problema**: Mensagens curtas estão criando sessões na sidebar indevidamente.
**Causa**: O Controller força a criação de título/sessão na primeira mensagem, ignorando filtros do HistoryManager.

- [x] **2.1 Ajuste no Controller (`controller.py`)**
    - [x] Remover chamada direta para `set_session_title` na primeira mensagem.
    - [x] Delegar a decisão de persistência ao `HistoryManager` (usando `is_session_persistent`).
    - [x] Só gerar título se a sessão *realmente* for persistida (retorno do HistoryManager ou verificação prévia).

---
**Regras de Execução:**
- Seguir estritamente `@[plano de implementação/regras_projeto.md]`.
- Uma fase por vez com aprovação.
