# Plano de Correção UX - Controle de Áudio

## 1. Problemas Relatados
1.  Botão "Parar" continua ativo após o fim do áudio.
2.  Clicar em "Parar" reinicia o áudio em vez de parar.
3.  Iniciar um novo áudio não para o anterior (sobreposição).

## 2. Diagnóstico Técnico (`MessageBubble.tsx` e `App.tsx`)
O problema fundamental é que o gerenciamento do objeto `Audio` está descentralizado ou incompleto.

*   No `App.tsx`:
    *   O evento `tts_ready` cria um `new Audio(url)` e dá play.
    *   Não há referência guardada desse objeto `Audio` para poder chamar `.pause()` ou monitorar o evento `onended`.
    *   Cada vez que o socket envia `tts_ready`, um novo objeto isolado é criado, permitindo sobreposição.

*   No `MessageBubble.tsx`:
    *   O estado `isPlaying` é puramente local e alterna apenas com o clique (`handleSpeak` faz `setIsPlaying(!isPlaying)`).
    *   Ele não *sabe* quando o áudio realmente terminou (pois o `App.tsx` que toca não avisa).
    *   Ele chama `onSpeak` (que vai para `App.tsx` -> `socket.emit`), então o "Parar" na verdade pede para gerar de novo se a lógica não diferenciar Stop de Play.

## 3. Solução Proposta

### Centralizar o Player de Áudio (Singleton Pattern no App)
Precisamos que apenas UM áudio toque por vez e que o estado seja sincronizado.

1.  **Criar Contexto ou Ref Global de Áudio no `App.tsx`**:
    *   Manter uma ref `audioRef = useRef<HTMLAudioElement | null>(null)`.
    *   Manter um estado `playingMessageId` para saber *qual* mensagem está tocando.

2.  **Lógica `playAudio` no `App.tsx`**:
    *   Se já estiver tocando: `audioRef.current.pause()`.
    *   Ao receber `tts_ready`:
        *   Criar ou reutilizar Audio.
        *   Adicionar listener `onended` para resetar o estado `playingMessageId`.
        *   Tocar.

3.  **Lógica `stopAudio`**:
    *   Método para parar explicitamente.

4.  **Integração com `MessageBubble`**:
    *   O `MessageBubble` não deve ter estado `isPlaying` isolado. Ele deve receber `isPlaying` via props do pai (`App.tsx`), baseado no ID da mensagem (índice).
    *   O callback `onSpeak` deve virar `onToggleAudio`.

## 4. Plano de Execução

- [ ] **Passo 1: Refatorar `App.tsx`**
    - [ ] Adicionar `currentAudio` (ref) e `playingIndex` (state).
    - [ ] Criar função `handleToggleAudio(index, text)`.
        - [ ] Se `index == playingIndex`: Parar áudio.
        - [ ] Se `index != playingIndex`: Parar anterior e solicitar novo (socket).
    - [ ] Atualizar listener `tts_ready` para tocar e setar `onended` que limpa `playingIndex`.

- [ ] **Passo 2: Refatorar `MessageBubble.tsx`**
    - [ ] Remover state `isPlaying` interno.
    - [ ] Receber prop `isPlaying` do pai.
    - [ ] Atualizar ícone baseado na prop.

- [ ] **Passo 3: Testar**
    - [ ] Tocar áudio 1.
    - [ ] Tocar áudio 2 (deve parar o 1).
    - [ ] Parar áudio 1 (deve parar e resetar ícone).
    - [ ] Deixar acabar (deve resetar ícone).

## 5. Auditoria de Regras
Esta abordagem resolve a inconsistência de estado (front vs som real) e a sobreposição, seguindo as boas práticas de "Single Source of Truth" para o estado da UI.
