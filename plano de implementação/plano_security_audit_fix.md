# Plano de Correção de Vulnerabilidades (NPM Audit)

## 1. Análise de Vulnerabilidades
O relatório `npm audit` identificou 10 vulnerabilidades (1 moderada, 9 altas), centradas em duas dependências principais:
1.  **Electron**: Vulnerabilidade de *ASAR Integrity Bypass*. Afeta versões `<35.7.5`.
    -   Atual: `^33.2.1`.
    -   Recomendação NPM: Atualizar para versão 40 (Breaking Change).
2.  **Tar (via Electron-Builder)**: Vulnerabilidade de *Arbitrary File Overwrite*.
    -   Afeta dependências aninhadas de `electron-builder`.
    -   Recomendação NPM: Atualizar `electron-builder` (Breaking Change).

## 2. Estratégia de Correção (Segurança vs Estabilidade)
Seguindo as regras de "Preservação do Sistema", atualizações de versão maior (Major) em frameworks como Electron são arriscadas e podem quebrar a aplicação (APIs mudam).
**Abordagem:**
1.  **Tentativa Conservadora:** Atualizar para as versões mais recentes *dentro* das faixas compatíveis (Minor/Patch) para ver se há backports de segurança.
2.  **Atualização Controlada:** Se a conservadora falhar, forçar atualização para versões estáveis mais recentes que corrijam o problema, mas testando a compilação.

*Nota:* O Electron frequentemente lança patches de segurança para versões anteriores. Se a v33 tiver sido abandonada, teremos que subir para v34/35.

## 3. Checklist de Execução

- [ ] **Passo 1: Atualização Conservadora**
    - [ ] Executar `npm update electron electron-builder`.
    - [ ] Executar `npm audit` para verificar se reduziu.

- [ ] **Passo 2: Correção Forçada (Se necessário)**
    - [ ] Se persistir, executar `npm audit fix` (sem force primeiro).
    - [ ] Se ainda crítico, atualizar manualmente `electron` para a versão estável mais próxima recomendada (ex: v35) e `electron-builder`.
    - [ ] Comando: `npm install electron@latest electron-builder@latest --save-dev`.

- [ ] **Passo 3: Auditoria Pós-Correção**
    - [ ] Verificar se o app inicia (`npm run dev`).
    - [ ] Verificar se o app Electron abre (`npm run electron` - se possível testar).

## 4. Aprovação
Este plano visa mitigar riscos de segurança sem reescrever código da aplicação.
