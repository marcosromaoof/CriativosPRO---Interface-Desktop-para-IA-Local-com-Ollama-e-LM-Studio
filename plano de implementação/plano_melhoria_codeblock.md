# Auditoria de UI - Melhorias em Blocos de Código

## 1. Problemas Identificados
Conforme imagem enviada e solicitação do usuário:
1.  **Falta do botão "Copiar":** O bloco de código existe, mas não possui um botão dedicado para copiar *apenas o código* (o botão de copiar geral copia a mensagem toda).
2.  **Sintaxe Monocromática:** O código está sendo exibido todo em verde (`#text-emerald-400`), sem syntax highlighting (cores variadas para variáveis, funções, strings, etc).

## 2. Diagnóstico Técnico (`MessageBubble.tsx`)
Atualmente, a renderização do markdown para a tag `code` e `pre` é feita de forma manual e simplista:

```tsx
code: ({ children }) => <code className="bg-black/30 ... text-emerald-400 ...">{children}</code>
```

Isso força *todo* o conteúdo do código a ter a cor `text-emerald-400`, anulando qualquer highlight. Além disso, o componente `pre` é apenas um container estilizado, sem lógica de cabeçalho ou botões.

## 3. Solução Proposta

### Implementar Syntax Highlighting
Utilizar a biblioteca `react-syntax-highlighter` (se já instalada ou se puder adicionar, caso contrário, implementar uma solução CSS mais inteligente ou verificar se o highlight já está presente e só está sendo sobrescrito).
*Obs: O usuário pediu para não improvisar. Vamos verificar se `react-syntax-highlighter` já está no `package.json`. Se não, usaremos uma abordagem CSS via classes geradas pelo markdown parser ou uma implementação leve.*
*Verificação:* O projeto já usa `react-markdown`. Geralmente ele não estiliza sozinho.

### Melhorar o Bloco de Código (`pre`)
Transformar o renderizador da tag `pre` em um componente rico:
1.  **Header:** Barra superior com a linguagem (ex: "python") e o botão de Copiar.
2.  **Conteúdo:** O código em si, com coloração adequada.

## 4. Plano de Implementação

- [ ] **Passo 1: Verificar Dependências**
    - [ ] Checar `package.json` por `react-syntax-highlighter` ou similar.
    - [ ] Se não existir, adicionar via `npm install` (padrão de mercado para React).

- [ ] **Passo 2: Criar Componente `CodeBlock`**
    - [ ] Criar novo componente `frontend/src/components/CodeBlock.tsx`.
    - [ ] Receber `language` e `children` (código).
    - [ ] Implementar botão de copiar com feedback visual (Check).
    - [ ] Implementar Highlight (estilo 'dracula' ou 'atom-dark').

- [ ] **Passo 3: Integrar no `MessageBubble.tsx`**
    - [ ] Substituir o render `pre/code` atual pelo novo `CodeBlock`.
    - [ ] Detectar a linguagem vinda do markdown (`code({node, inline, className, children})`).

## 5. Auditoria de Regras
- Código novo será modular (`CodeBlock.tsx`).
- Resolve a demanda visual (cores) e funcional (copiar).
- Segue hierarquia de arquivos frontend.

*Nota:* Se não puder instalar novas libs (regra de zero improviso/preservação), serei obrigado a fazer um parser simples ou usar cores estáticas melhores, mas o padrão correto é usar uma lib dedicada para highlight. Assumirei que instalar `react-syntax-highlighter` é permitido para atender "cores variadas".
