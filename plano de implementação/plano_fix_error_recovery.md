# Plano de Correção: Recuperação de Erros (FSM Travada)

## 1. Problema Identificado
O usuário relatou que após um erro de API (ex: erro 402 do OpenRouter), o sistema travou.
- **Sintoma:** Input desabilitado ("travado"), impossível digitar ou iniciar novo chat.
- **Log:** `[Controller] Sistema ocupado (ERROR). Ignorando mensagem.`
- **Causa Raiz:** A Máquina de Estados (FSM) entra em estado `ERROR` e **não retorna** para `IDLE`. O código atual do Controller impede explicitamente o reset para `IDLE` se o estado for `ERROR` no bloco `finally`.

## 2. Diagnóstico Técnico
### Backend (`controller.py`)
No método `handle_message`:
```python
except Exception as e:
    fsm.change_to(SystemState.ERROR)
    await self.sio.emit("error", ...)
finally:
    # O CULPADO: Se estiver em ERROR, ele NÃO volta pra IDLE
    if not fsm.current_state == SystemState.ERROR:
        fsm.change_to(SystemState.IDLE)
```
Isso faz com que erros de geração (como falta de créditos ou modelo inválido) travem o backend permanentemente até reinício.

### Frontend (`App.tsx`)
O frontend seta `status` para `ERROR` quando recebe o evento. O input tem `disabled={status !== 'IDLE'}`. Como o backend não manda sinal de "concluído" ou "idle" após o erro, o front também fica travado.

## 3. Solução Proposta

### No Backend
Erros de geração (API, validação) são **transitórios**. O sistema deve:
1.  Capturar o erro.
2.  Notificar o cliente.
3.  **Retornar imediatamente ao estado `IDLE`** para permitir novas tentativas.
4.  O estado `ERROR` persistente deve ser reservado apenas para falhas críticas de infraestrutura (ex: falha de conexão com DB que impeça qualquer operação), e mesmo assim, deve haver um mecanismo de reset. Para erros de LLM, o reset deve ser automático.

### No Frontend
Ao receber um evento `error`:
1.  Exibir a mensagem (já implementado).
2.  Forçar o status local de volta para `IDLE` (ou garantir que o backend envie um evento que cause isso).

## 4. Checklist de Execução

- [ ] **1. Corrigir `backend/core/controller.py`**
    - [ ] Remover a verificação condicional no `finally`.
    - [ ] Garantir que `fsm.change_to(SystemState.IDLE)` seja chamado sempre ao final do processamento, sucesso ou falha.

- [ ] **2. Corrigir `frontend/src/App.tsx`**
    - [ ] No listener `socket.on('error')`, adicionar `setStatus('IDLE')` após processar o erro, para garantir destravamento da UI imediatamente.

- [ ] **3. Validação**
    - [ ] Simular um erro (ex: usar modelo inválido ou simular exceção).
    - [ ] Verificar se FSM volta para IDLE.
    - [ ] Verificar se input destrava para nova tentativa.

## 5. Auditoria
Esta alteração segue a regra de "Preservação e Análise" pois corrige um bug de fluxo lógico (deadlock de estado) sem alterar a estrutura da FSM em si.
