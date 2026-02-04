# Auditoria e Correção Profunda: Stop Generation Inoperante

## 1. Análise de Causa Raiz
O mecanismo de "Parar" não funciona porque a tarefa que o sistema cancela (`self._current_task`) refere-se apenas à **inicialização** da conexão com a IA, e não ao processo de geração completo.

### Código Atual (Defeituoso):
```python
# handle_message
self._current_task = asyncio.create_task(
    provider.generate_response(...) # Retorna o stream, a task acaba AQUI.
)
response_stream = await self._current_task 

# O loop abaixo roda "solto", sem estar atrelado a _current_task
async for chunk in response_stream:
    # ...
```
Quando o usuário clica em Parar, cancelamos `_current_task`, mas ela já terminou faz tempo. O loop continua rodando até o fim da resposta.

## 2. Solução Técnica (Encapsulamento de Task)
Precisamos encapsular **todo o ciclo de vida** da geração em uma única Task assíncrona.

### Nova Arquitetura (`controller.py`):
1.  Criar método `_process_generation(self, session_id, sid, ...)`:
    *   Contém toda a lógica pesada: chamar provider, loop de chunks, salvar no banco, chamar TTS.
2.  Atualizar `handle_message`:
    *   Apenas prepara os dados.
    *   Inicia a task: `self._current_task = asyncio.create_task(self._process_generation(...))`
    *   Não usa `await` nela (apenas `add_done_callback` para tratamento de erros finais se necessário).

Dessa forma, `self._current_task.cancel()` encerrará imediatamente o `_process_generation`, interrompendo o loop `async for` onde quer que esteja.

## 3. Investigação TTS (Lentidão)
O atraso no áudio deve-se ao "Cold Start" do `piper.exe` a cada frase.
*   **Melhoria Segura:** Como o usuário reclamou da "demora para começar", o problema principal pode ser a falta de **Feedback Visual**.
*   **Ação:** Adicionar estado de `loading` no botão de áudio no Frontend.
*   **Ação Backend:** Confirmar se não há bloqueios síncronos excessivos antes do `subprocess`.

## 4. Checklist de Execução

- [ ] **Refatorar `backend/core/controller.py`**
    - [ ] Extrair lógica de geração para método `_process_message_flow`.
    - [ ] Atualizar `handle_message` para disparar esse método como Task background.
    - [ ] Garantir tratamento de `CancelledError` dentro do novo método.

- [ ] **Frontend `App.tsx` / `MessageBubble.tsx`**
    - [ ] Adicionar prop `isAudioLoading` ao MessageBubble.
    - [ ] Mostrar spinner no ícone de volume enquanto espera o evento `tts_ready`.

## 5. Aprovação
Esta mudança arquitetural no Controller é mandatória para que a função "Parar" funcione de verdade em streams longos.
