# Checklist de Debug e Correção: Tela Branca/Azul (Blank Screen)

O erro de "Tela Azul/Preta" (fundo do Electron sem conteúdo) geralmente indica falha no carregamento dos assets do Frontend.

## 1. Diagnóstico do Caminho (RESOLVIDO)
- [x] **Vite Config `base`**: 
    - **Problema:** O padrão é `/`. Em Electron (`file://`), isso busca na raiz do drive (ex: `C:/assets`).
    - **Correção:** Alterado para `./` em `vite.config.ts`. Isso força caminhos relativos (`./assets/script.js`).

## 2. Diagnóstico de Rotas
- [ ] **Router**:
    - O app atualmente não usa `react-router-dom` explicitamente em `main.tsx`, renderizando `App` direto.
    - **Risco:** Baixo para este projeto, mas se houver navegação futura, usar `HashRouter` é mandatório.

## 3. Diagnóstico de Carregamento (Electron)
- [x] **`main.cjs` Load Logic**:
    - Código atual: `mainWindow.loadFile(path.join(__dirname, 'dist/index.html'));`
    - Está correto, desde que a estrutura de pastas `dist` seja gerada junto ao `main.cjs` ou ajustada no build resource.
    - **Verificação:** Na compilação, `electron-builder` geralmente empacota tudo.

## 4. Diagnóstico de Execução do Backend
- [ ] **Processo Background**:
    - Se o backend cair, o frontend fica esperando eternamente?
    - **Verificação:** O frontend só mostra "Loading..." se esperar o socket?
    - **Ação:** Verificar logs do console (Ctrl+Shift+I no Electron final) se a tela persistir branca.

## 5. Próximos Passos
1. Execute `build_release.bat`.
2. Instale o novo `.exe`.
3. Se funcionar: Sucesso.
4. Se falhar:
    - Abra o app instalado.
    - Aperte `Ctrl+Shift+I` (DevTools).
    - Vá na aba **Console**.
    - Tire 'print' dos erros vermelhos (provavelmente 404 Not Found ou CSP block).

## Resumo das Alterações Feitas
- `vite.config.ts`: Adicionado `base: './'`.
- `index.html`: Título ajustado.
