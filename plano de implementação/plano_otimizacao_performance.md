# 🚀 Plano de Otimização de Performance

Este plano corrige os problemas de lentidão, travamento e delay relatados, identificados durante a auditoria.

## 🛑 Diagnósticos
1.  **Frontend (Crítico)**: O componente `MessageBubble` não utiliza `React.memo`. A cada novo token recebido, **todas** as mensagens anteriores são re-renderizadas e o Markdown é reprocessado, causando travamento exponencial (O(N*T)).
2.  **Backend**: Operações de banco de dados (`sqlite3`) estão sendo executadas de forma síncrona na thread principal, podendo causar pequenos bloqueios entre mensagens.

## 📋 Checklist de Alterações

### 🟧 Fase 1: Otimização Frontend (Prioridade Máxima)
- [x] **1.1 Memoização de Componentes (`MessageBubble.tsx`)**
    - [x] Implementar `React.memo` no export do `MessageBubble`.
    - [x] Criar função de comparação `arePropsEqual` (opcional, mas recomendado para ignorar mudanças irrelevantes).
- [x] **1.2 Estabilização de Props (`App.tsx`)**
    - [x] Garantir que funções passadas como props (`handleRequestAudio`, etc.) sejam estáveis (usar `useCallback`).

- [x] **1.3 UX: Thinking Indicator (`App.tsx` / `MessageBubble.tsx`)**
    - [x] Mostrar bolha do bot com animação "..." imediatamente após envio do usuário.
    - [x] Adicionar delay artificial de 1.5s antes de começar a renderizar o texto real (acumular chunks em buffer durante esse tempo ou usar setTimeout).
    - [x] Criar visual "..." animado e elegante.

### 🟦 Fase 2: Otimização Backend (Secundário)
- [ ] **2.1 Banco de Dados Não-Bloqueante (`history_manager.py`)**
    - [ ] Envolver chamadas SQL pesadas em `asyncio.to_thread` para não travar o loop de eventos do Socket.IO.

## 🚀 Impacto Esperado
- **Fluidez**: O texto deve aparecer suavemente, sem trancos.
- **Velocidade**: O app não deve mais travar em conversas longas.
- **Responsividade**: A segunda mensagem deve ser processada imediatamente.

---
**Status**: Aguardando Aprovação.
