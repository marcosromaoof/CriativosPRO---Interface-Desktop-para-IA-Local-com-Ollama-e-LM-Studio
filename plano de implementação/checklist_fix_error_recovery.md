# Checklist de Implementação - Recuperação de Erros

Este checklist visa destravar o sistema após erros de API, conforme analisado no `plano_fix_error_recovery.md`.

## 1. Backend (`controller.py`)
- [ ] **Editar `handle_message`**:
    - [ ] Localizar bloco `finally`.
    - [ ] Remover a condição `if not fsm.current_state == SystemState.ERROR`.
    - [ ] Forçar `fsm.change_to(SystemState.IDLE)` incondicionalmente (desde que não esteja em um estado de desligamento do sistema, o que não se aplica aqui).

## 2. Frontend (`App.tsx`)
- [ ] **Editar listener `socket.on('error')`**:
    - [ ] Adicionar `setStatus('IDLE')` após a atualização das mensagens.
    - [ ] Isso garante que, visualmente, o campo de input seja reabilitado imediatamente.

## 3. Teste
- [ ] Verificar se após um erro, o sistema envia "Mudança de estado: ERROR -> IDLE" no log.
- [ ] Tentar enviar nova mensagem.

---
**Aguardando execução imediata das correções visto que é um bug bloqueante.**
