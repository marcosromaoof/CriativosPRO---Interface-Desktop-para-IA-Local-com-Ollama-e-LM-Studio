# Checklist de Implementação - Configurações via Modal (Opção A)

Este checklist segue estritamente as regras definidas em `regras_projeto.md`. A implementação transformará a tela de configurações em um Modal (Overlay), mantendo o usuário no contexto atual (Chat ou Dashboard).

## 1. Planejamento da Arquitetura (Frontend)
- [ ] **Criar Componente `SettingsModal`**: Será um novo componente encapsulando a lógica visual de modal (backdrop, fechar ao clicar fora, animação de entrada).
- [ ] **Refatorar Estado Global (`App.tsx`)**:
    - [ ] Criar estado `showSettings` (boolean).
    - [ ] Remover ou obsoletar a opção `'settings'` do estado `activeView`. O `activeView` controlará apenas telas principais (Chat, Dashboard).
- [ ] **Ajustar Sidebar**:
    - [ ] O botão "Configurações" não mudará mais a `activeView`, mas sim fará toggle do `showSettings`.
- [ ] **Migrar Conteúdo**:
    - [ ] Mover o conteúdo de `SettingsView` para dentro do `SettingsModal`.

## 2. Etapas de Codificação
### Etapa 2.1: Estrutura do Modal
- [ ] Criar `frontend/src/components/SettingsModal.tsx`.
    - [ ] Implementar backdrop com `backdrop-blur`.
    - [ ] Implementar container centralizado com `animate-in fade-in zoom-in`.
    - [ ] Adicionar botão "Fechar" (X) explícito no topo do modal.
    - [ ] Garantir que o conteúdo seja scrollável se for muito grande (`max-h-[85vh] overflow-y-auto`).

### Etapa 2.2: Integração no App.tsx
- [ ] Adicionar `const [showSettings, setShowSettings] = useState(false);`.
- [ ] Alterar função `SidebarItem` de Configurações para chamar `setShowSettings(true)`.
- [ ] Renderizar `<SettingsModal socket={socketRef.current} onClose={() => setShowSettings(false)} />` condicionalmente (`{showSettings && ...}`) no final do JSX do App, fora do `<main>`.

### Etapa 2.3: Limpeza
- [ ] Remover lógica antiga que renderizava `activeView === 'settings'`.
- [ ] Restaurar visualização dos seletores Engine/Arquitetura (eles haviam sido ocultados condicionalmente, agora estarão sempre visíveis no fundo enquanto o modal está aberto, ou ocultos pelo modal). *Observação: O usuário reclamou da "janela branca". Garantir que o Modal tenha fundo escuro (`bg-[#0a0f1d]`).*

## 3. Validação (Pós-Implementação)
- [ ] Verificar se clicar no botão Configurações abre o modal suavemente.
- [ ] Verificar se o resto da app (Chat) continua visível (borrado) ao fundo.
- [ ] Verificar se fechar o modal retorna exatamente ao estado anterior.
- [ ] Verificar cores do Modal (Fundo Escuro, Texto Claro) para evitar o problema visual anterior.

---
**Aguardando aprovação deste checklist para iniciar a Etapa 2.1.**
