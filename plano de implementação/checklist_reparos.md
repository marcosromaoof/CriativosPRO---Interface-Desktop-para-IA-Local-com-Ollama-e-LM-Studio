# ✅ Checklist de Reparos - Auditoria Fase 1

Este checklist deve ser seguido rigorosamente para garantir que todas as correções sejam aplicadas e validadas.

## 🏁 Pré-Requisitos
- [ ] 1. Fazer backup da pasta `backend/core` para `backend/core_backup_2026_02_02`.
- [ ] 2. Fazer backup do banco de dados `criativospro.db`.
- [ ] 3. Criar arquivo `.gitignore` na raiz (se não existir) e adicionar `security.key`.

## 🛡️ Fase 1: Segurança (Hardening)
- [ ] 4. Editar `backend/core/main.py`: Restringir CORS para `localhost` e `127.0.0.1`.
- [ ] 5. Editar `backend/core/controller.py`: Implementar validação de `session_id` (regex `^[a-zA-Z0-9_-]+$`) e limite de tamanho.
- [ ] 6. Teste Manual: Tentar conectar via origem não autorizada (opcional) ou verificar se frontend local continua funcionando.

## ⚡ Fase 2: Performance (Async & DB)
- [ ] 7. Editar `backend/core/database.py`: Adicionar criação de índices para `history` e `metrics`.
- [ ] 8. Editar `backend/core/history_manager.py`:
    - [ ] Refatorar `add_message` para Async.
    - [ ] Refatorar `get_context` para Async.
    - [ ] Refatorar `get_all_sessions` para Async.
    - [ ] Refatorar `load_session` (get_full_history) para Async.
- [ ] 9. Atualizar chamadas no `backend/core/main.py`:
    - [ ] Adicionar `await` em `history_manager.add_message` (se houver).
    - [ ] Adicionar `await` em `history_manager.get_all_sessions`.
    - [ ] Adicionar `await` em `history_manager.get_full_history`.
- [ ] 10. Atualizar chamadas no `backend/core/controller.py`:
    - [ ] Adicionar `await` em `history_manager.add_message`.
    - [ ] Adicionar `await` em `history_manager.get_context`.
- [ ] 11. Teste Manual: Verificar se o chat carrega histórico e envia mensagens sem travar.

## 🧹 Fase 3: Manutenção e Limpeza
- [ ] 12. Editar `backend/core/tts_service.py`: Implementar `cleanup_temp_files`.
- [ ] 13. Editar `backend/core/main.py`:
    - [ ] Mover imports para o topo (onde seguro).
    - [ ] Envolver handlers em `try/except` genérico.
- [ ] 14. Validação Final: Rodar servidor, trocar mensagens, gerar áudio, verificar logs.

## 🚀 Pós-Implementação
- [ ] Audit Final: Verificar se algum arquivo temporário sobrou.
- [ ] Atualizar `relatorio_auditoria_achados.md` marcando itens como "Corrigido".
