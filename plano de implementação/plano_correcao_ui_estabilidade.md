# 🛠️ Plano de Correção: UI e Estabilidade

Este plano aborda a correção da interface de exclusão (Modal) e investigação do travamento na função "Novo Chat".

## 🟥 Fase 1: Modal de Confirmação (UI Premium)
**Problema**: Uso de `window.confirm` nativo quebra a identidade visual ("janela do windows").
**Solução**: Implementar modal customizado com design system (Glassmorphism).

- [x] **1.1 Adicionar Estado no App (`App.tsx`)**
    - [x] `showDeleteModal` (boolean) e `sessionToDelete` (string | null).
    - [x] Adicionar handlers `openDeleteModal(id)` e `confirmDelete()`.

- [x] **1.2 Criar Componente Inline `DeleteConfirmationModal`**
    - [x] Estilo: `fixed inset-0`, fundo `backdrop-blur` e `bg-black/50`.
    - [x] Conteúdo: "Excluir conversa?", botões "Cancelar" (Ghost) e "Excluir" (Red).

- [x] **1.3 Integrar na Sidebar**
    - [x] Alterar botão de lixeira para chamar `openDeleteModal`.

## 🟧 Fase 2: Estabilidade "Novo Chat"
**Problema**: Relato de travamento ao criar novo chat.
**Hipótese**: Conflito de renderização ou estado ao limpar mensagens.

- [x] **2.1 Refatoração do Handler `startNewChat`**
    - [x] Encapsular lógica em função dedicada `handleNewChat` (fora do JSX).
    - [x] Adicionar pequeno delay ou `requestAnimationFrame` se necessário para garantir ciclo de renderização limpo.
    - [x] Verificar se `generateSessionId` está performático.

---
**Regras de Execução:**
- Seguir estritamente `@[plano de implementação/regras_projeto.md]`.
- Uma fase por vez com aprovação.
