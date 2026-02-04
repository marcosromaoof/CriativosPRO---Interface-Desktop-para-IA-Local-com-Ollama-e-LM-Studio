# 🕵️ Plano de Auditoria e Otimização de Performance

Este documento define o roteiro para investigar e corrigir os problemas relatados de "delay", "lentidão" e "renderização brusca" no chat.

## 🛑 Problemas Relatados
1.  **Lentidão no Envio**: Delay significativo entre envio e resposta (segunda mensagem).
2.  **Renderização Brusca**: Bot "surge" com a mensagem pronta ou em blocos grandes, perdendo o efeito de digitação suave.
3.  **Interface Lenta**: App trava ou engasga durante a geração.

## 📋 Roteiro de Auditoria (Leitura Completa)

### 1. Frontend (`frontend/src`)
- [ ] **`App.tsx`**:
    - Analisar o listener `socket.on('chat_chunk')`.
    - Verificar a complexidade da atualização de estado `setMessages`. Arrays grandes sendo copiados a cada token travam o React.
    - Verificar uso de `useEffect` que roda a cada atualização de mensagem.
- [ ] **`components/MessageBubble.tsx`**:
    - Verificar se o componente está re-renderizando o Markdown inteiro a cada caractere novo. Isso é extremamente custoso (O(N)).
    - Verificar uso de `React.memo`.

### 2. Backend (`backend/core`)
- [ ] **`controller.py`**:
    - Verificar se o loop de streaming tem `await asyncio.sleep(0)` para ceder controle.
    - Verificar se operações de banco (`HistoryManager`) estão dentro do loop de streaming bloqueando o fluxo.
- [ ] **`history_manager.py`**:
    - Verificar se queries SQL estão rodando no thread principal (bloqueando o async loop).
- [ ] **`main.py`**:
    - Verificar configuração do `AsyncServer` e integração com `aiohttp`.

## 🚀 Plano de Correção (Hipótese)

Se confirmadas as suspeitas na auditoria, as prováveis correções (Fases Futuras) serão:

1.  **Frontend Otimizado**:
    - Usar `useRef` para buffer de texto ou atualizar apenas a última mensagem sem recriar todo o array `messages`.
    - Implementar `memo` no `MessageBubble` para evitar re-render de mensagens antigas.
    - Usar `throttle` ou `buffer` no socket listener para atualizar a UI a cada Xms (ex: 50ms) em vez de cada token (ex: 5ms), reduzindo renders em 90%.

2.  **Backend Non-Blocking**:
    - Mover gravações de log/histórico para background tasks (não bloquear a resposta).
    - Garantir streaming fluido.

---
**Próximo Passo**: Aprovação deste plano para iniciar a Leitura dos Arquivos.
