# Checklist de Implementação - Code Block com Syntax Highlight

## 1. Instalação e Configuração
- [x] Verificar `package.json` (biblioteca ausente).
- [ ] Instalar `react-syntax-highlighter` (em progresso).

## 2. Componente `CodeBlock.tsx`
- [ ] Criar novo arquivo em `src/components/CodeBlock.tsx`.
- [ ] Importar `Prism` como `SyntaxHighlighter` do `react-syntax-highlighter`.
- [ ] Importar tema (ex: `vscDarkPlus` ou `atomDark`).
- [ ] Adicionar lógica de cópia para clipboard com feedback (`useState` 'copied').
- [ ] Estrutura:
    ```
    <div className="rounded-lg overflow-hidden border border-white/10 ...">
       <header className="flex justify-between ... bg-white/5 ...">
          <span>{language}</span>
          <button onClick={copy}>Copiar</button>
       </header>
       <SyntaxHighlighter ...>{code}</SyntaxHighlighter>
    </div>
    ```

## 3. Integração (`MessageBubble.tsx`)
- [ ] Alterar `ReactMarkdown` components:
    - [ ] Remover renderizadores antigos de `code` e `pre`.
    - [ ] Adicionar lógica para remover quebra de linha final do código.
    - [ ] Passar `match` de regex para extrair a linguagem da classe `language-xxx`.

## 4. Validação
- [ ] Verificar se o código não quebra o layout.
- [ ] Testar botão de copiar.
- [ ] Verificar coloração de sintaxe em Python, JS e HTML.
