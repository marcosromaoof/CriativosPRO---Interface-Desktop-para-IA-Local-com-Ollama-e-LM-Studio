# 🛠️ Plano de Implementação - Reparos de Auditoria

## 1. Objetivo
Este documento detalha o plano para corrigir as vulnerabilidades de segurança, problemas de performance e inconsistências apontadas no `relatorio_auditoria_achados.md`. O objetivo é elevar a maturidade do sistema para padrões de produção, garantindo estabilidade, segurança e manutenibilidade.

## 2. Estratégia de Execução
As correções serão divididas em 3 fases, priorizando segurança e estabilidade crítica. Cada fase será implementada, revisada e testada antes de avançar.

### ⚠️ Fase 1: Segurança Crítica e Hardening (Prioridade Máxima)
Foco em fechar portas de entrada para ataques e proteger credenciais.
*   **Correção de CORS:** Restringir acesso apenas ao frontend local.
*   **Proteção de Chaves:** Implementar `.gitignore` para o arquivo de chaves e garantir que não seja servido estaticamente (embora `main.py` sirva `temp_audio`, devemos confirmar se `security.key` não está exposto via rota estática acidental).
*   **Validação de Inputs:** Implementar camada de sanitização no `controller.py` para evitar dados malformados ou abusivos antes de chegarem ao banco.

### ⚡ Fase 2: Performance e Estabilidade (Core)
Foco em desbloquear o Event Loop e garantir escalabilidade básica.
*   **Banco de Dados Async:** Refatorar `history_manager.py` para rodar operações SQLite em threads separadas (`asyncio.to_thread`), evitando o bloqueio do servidor durante I/O.
*   **Índices de Banco:** Criar índices para otimizar consultas de histórico e métricas.
*   **Limpeza de Áudio (TTS):** Implementar rotina de limpeza para evitar estouro de disco com arquivos `.wav` temporários.

### 🧹 Fase 3: Qualidade de Código e Robustez (Manutenibilidade)
Foco em reduzir dívida técnica e melhorar a detectabilidade de erros.
*   **Tratamento de Erros:** Adicionar blocos `try/except` robustos nos eventos do SocketIO.
*   **Organização de Imports:** Mover imports de dentro das funções para o topo (onde não criar ciclos).
*   **Logging:** Substituir `print()` críticos por um sistema de lógica estruturado (opcional por agora, focar em `print` estruturado se `logging` for muito complexo para o escopo, mas o relatório pede logging). *Nota: Devido à regra "Zero Improviso" e "Preservação", vamos manter `print` mas padronizar o formato com timestamps, ou implementar um wrapper simples.*

## 3. Detalhamento Técnico das Mudanças

### 3.1. `backend/core/main.py`
*   **Ação:** Alterar `cors_allowed_origins` de `'*'` para lista explícita (`['http://localhost:5173', 'http://127.0.0.1:5173']`).
*   **Ação:** Adicionar `try/except` em todos os handlers `@sio.event`.    
*   **Ação:** Mover imports (`from core...`) para o topo, resolvendo dependências circulares se houver (se houver ciclos, manter local mas documentar, a prioridade é mover o que for seguro).

### 3.2. `backend/core/history_manager.py`
*   **Ação:** Criar métodos privados `_sync` para operações de banco.
*   **Ação:** Reescrever métodos públicos como `async def` que chamam `await asyncio.to_thread(self._sync_method, ...)`.
*   **Risco:** Isso exige alterar as chamadas no `main.py` e `controller.py` para usar `await`.
    *   *Verificação:* `main.py` já chama `history_manager.get_all_sessions()` (sync) dentro de func async. Terá que virar `await history_manager.get_all_sessions()`.
    *   *Impacto Alto:* Refatoração propagada. Necessário cuidado extremo.

### 3.3. `backend/core/database.py`
*   **Ação:** Adicionar comandos SQL `CREATE INDEX IF NOT EXISTS` no método `_init_db`.
*   **Ação:** Adicionar `security.key` ao `.gitignore` (criar arquivo se não existir).

### 3.4. `backend/core/controller.py`
*   **Ação:** Adicionar validação de `session_id` (apenas alfanumérico/hífens, max 64 chars) e `content` (limite razoável ou truncamento seguro).

### 3.5. `backend/core/tts_service.py`
*   **Ação:** Adicionar método `cleanup_old_files()` que deleta arquivos > 24h.
*   **Ação:** Chamar este método na inicialização ou periodicamente.

## 4. Plano de Rollback
*   Backup completo dos arquivos `backend/core/*.py` e do banco `criativospro.db` antes de iniciar.
*   Se o servidor não iniciar, restaurar arquivos originais.

---
**Autor:** Antigravity (Google Deepmind)
**Data:** 02/02/2026
