# 🛠️ Plano de Implementação - Fase 2: Correção de Áudio e UX

## 1. Diagnóstico e Contexto
O usuário relata que:
1.  **Áudio Inoperante:** O áudio foi corrigido no backend (headers do wave), mas o frontend ainda não reproduz.
2.  **UX Rápida Demais:** Após o "pensamento" de 1.5s, o texto aparece muito rápido (dump), sendo desagradável.

O diagnóstico técnico indicou:
- Backend: O arquivo `.wav` agora é gerado corretamente.
- Frontend: O clique no botão de áudio dispara `onSpeak`. No `App.tsx`, isso chama `handleRequestAudio`, que emite `generate_tts`.
- Rota: O backend serve `/audio/` mapeado para `backend/temp_audio`.
- O caminho retornado no evento `tts_ready` é `http://127.0.0.1:5000/audio/{filename}`.
- Possível problema: Se o frontend roda em `localhost:5173`, acessar `127.0.0.1:5000` pode ser bloqueado se o browser tratar diferente.
- Possível problema 2: O player `new Audio(url)` é criado mas não gerenciado. Se o browser bloquear autoplay sem interação direta naquele contexto (o clique foi indireto via socket callback), falha.
- **Problema de UX:** O `App.tsx` atualiza o estado `messages` diretamente com o chunk recebido.

## 2. Soluções Propostas

### 🔊 Problema 1: Áudio
**Alteração no Frontend (`MessageBubble.tsx` e `App.tsx`):**
1.  Melhorar o `handleSpeak` no `MessageBubble` para dar feedback visual de "carregando".
2.  Garantir que o objeto `Audio` seja tocado. O browser moderno exige interação do usuário. O clique no botão `Volume2` é a interação. Porém, o áudio toca SOMENTE quando o socket retorna (assíncrono).
    *   *Solução:* O clique deve disparar o pedido, e quando o áudio voltar, o `.play()` deve funcionar se o contexto de áudio não tiver sido suspenso.
    *   *Debug:* Vamos logar erro explícito.

**Alteração no Backend (`main.py`):**
1.  Garantir que a URL retornada seja acessível. Se o usuário estiver acessando via `localhost`, a URL deve ser relativa ou compatível.
2.  Atualmente hardcoded: `f"http://127.0.0.1:5000/audio/{filename}"`. Isso é frágil.
    *   *Melhoria:* Retornar apenas `/audio/{filename}` relativo, e o frontend decidir o host base, OU usar o header `Host` da requisição para construir a URL completa.

### 🍃 Problema 2: Suavização (Typing Effect)
**Estratégia: Buffer de Renderização no Frontend**
Não vamos mexer no backend para "enrolar" a resposta. O frontend deve controlar a exibição.
Criaremos um componente `TypingEffect` ou modificaremos `MessageBubble` para ter um estado interno de `displayedContent`.

**Algoritmo "Suave mas não lento":**
1.  O `MessageBubble` recebe `content` real.
2.  Se `isBot` e for a última mensagem (ou estiver em stream):
    - Um `useEffect` compara `content` real com `displayedContent`.
    - Se `real > displayed`, adiciona caracteres a um ritmo fixo (ex: 20ms/char) OU adaptativo (se a fila for grande, acelera).
    - **Regra do Usuário:** "Sem ser agressivo e sem ser lento demais".
    - *Lógica Adaptativa:* Se `len(buffer) > 50`, delay = 5ms. Se `len(buffer) < 10`, delay = 30ms.

## 3. Checklist de Execução

- [ ] **1. Correção de Áudio (Backend):**
    - [ ] Atualizar `generate_tts` em `main.py` para usar `request.host` na URL, garantindo compatibilidade `127.0.0.1` vs `localhost`.

- [ ] **2. Correção de UX (Frontend):**
    - [ ] Criar Hook personalizado `useTypewriter` em `hooks/useTypewriter.ts`.
    - [ ] Implementar lógica adaptativa de velocidade.
    - [ ] Integrar Hook no `MessageBubble.tsx`.
    - [ ] Remover delay artificial de 1.5s do `App.tsx` se o efeito de digitação já fornecer o feedback visual necessário (ou manter como "warming up"). O usuário pediu para manter o 1.5s ("apos o time de 1.5s..."). Então manteremos o delay inicial.

## 4. Auditoria e Validação
- Testar clique em "Ouvir".
- Verificar efeito de digitação em respostas longas.

---
**Autor:** Antigravity (Google Deepmind)
**Data:** 02/02/2026
