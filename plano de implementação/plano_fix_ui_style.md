# Auditoria de Estilo e UI

## 1. Análise do `tailwind.config.js`
- **Problema encontrado:** A cor `navy-950` é usada intensivamente no código (`App.tsx`), mas **não está definida** no arquivo de configuração! Apenas `navy-900` e `navy-800` existem.
- **Consequência:** `bg-navy-950` é interpretado como ausente (ou transparente/inválido), fazendo com que o navegador use o fallback padrão (branco) nas opções do `<select>`.
- **Ação:** Adicionar `950: '#050811'` (que corresponde ao bg-main usado em outros lugares) à paleta `navy`.

## 2. Análise do Menu de Configurações
- **Problema:** Os seletores de "Engine" e "Arquitetura" (Header) permanecem visíveis quando o usuário navega para "Configurações", criando uma interface desnecessariamente poluída e confusa ("overlapping" visual de intenções).
- **Consequência:** O usuário vê controles que não se aplicam à tela de configurações.
- **Ação:** Envolver a seção dos seletores no `App.tsx` em uma condicional `{activeView === 'chat' && (...)}`.

## 3. Plano de Correção

- [ ] **1. Corrigir Tailwind Config**
    - [ ] Adicionar `950: '#050811'` em `frontend/tailwind.config.js`.
    - [ ] Adicionar `electric-blue` (como alias de `#3b82f6` ou similar) se necessário, mas já parece estar lá, porem o uso inline `text-electric-blue` requer que a classe exista corretamente. (No config está dentro de um objeto? Linha 17 `electric-blue: { 500: ... }`. Então a classe deve ser `text-electric-blue-500` se for usar a cor, ou `text-electric-blue` se a cor for string direta. Vamos ajustar para string direta para facilitar: `'electric-blue': '#3b82f6'`).

- [ ] **2. Ajustar `App.tsx` (Header)**
    - [ ] Ocultar seletores se `activeView !== 'chat'`.

- [ ] **3. Hard-fix no CSS do Select**
    - [ ] Mesmo com a cor corrigida, `<option>` styling é chato. Vamos forçar `style={{ backgroundColor: '#050811', color: 'white' }}` nas options para garantir compatibilidade cross-browser imediata sem depender do rebuild do tailwind classes on-the-fly (que as vezes falha no HMR se a classe não existia antes).

## 4. Checklist de Validação
- [ ] Dropdown Engine deve ter fundo escuro.
- [ ] Dropdown Arquitetura deve ter fundo escuro.
- [ ] Tela de Configurações deve ter Header limpo (apenas status neural link ou título).
