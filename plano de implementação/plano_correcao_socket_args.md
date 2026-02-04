# 🛠️ Plano de Correção: Argumentos Socket.IO

Este plano visa corrigir o erro de `TypeError` causado pela falta de argumentos opcionais nos handlers de eventos do Socket.IO no backend.

## 🛑 Diagnóstico
**Erro**: `TypeError: get_sessions() missing 1 required positional argument: 'data'`
**Causa**: O evento `get_sessions` é emitido pelo frontend sem payload. O handler no backend exige o argumento `data`.
**Impacto**: O evento falha e gera stack trace no console, impedindo o carregamento da lista.

## 📋 Checklist de Alterações

- [x] **1. Correção no Backend (`main.py`)**
    - [x] Alterar assinatura de `get_sessions(sid, data)` para `get_sessions(sid, data=None)`.
    - [x] Alterar assinatura de `get_models(sid, data)` para `get_models(sid, data=None)` (Prevenção).
    - [x] Auditar outros eventos sem payload (`connect`, `disconnect` já estão ok).

## 🚀 Execução

1.  **Edição**: Modificar `backend/core/main.py`.
2.  **Validação**: Verificar se o erro desaparece do console ao recarregar o frontend.

---
**Status**: Aguardando Aprovação.
