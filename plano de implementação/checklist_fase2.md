# Checklist Fase 2 - Áudio e UX

- [ ] **1. Ajuste de URL de Áudio (Backend)**
    - [ ] Modificar `backend/core/main.py`: `generate_tts` deve usar host dinâmico.

- [ ] **2. Hook de Digitação (Frontend)**
    - [ ] Criar `frontend/src/hooks/useTypewriter.ts`:
        - [ ] Estado `display`.
        - [ ] Lógica `useEffect` que consome `content` e atualiza `display`.
        - [ ] Velocidade variável baseada no tamanho do buffer.

- [ ] **3. Integração com MessageBubble**
    - [ ] Atualizar `frontend/src/components/MessageBubble.tsx`:
        - [ ] Usar `useTypewriter` se for mensagem de bot.
        - [ ] Passar `display` para o renderer de Markdown.

- [ ] **4. Auditoria Final**
    - [ ] Validar correção de áudio.
    - [ ] Validar suavidade do texto.
