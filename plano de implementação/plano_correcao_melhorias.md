# 🎯 Plano de Correção e Melhorias - CriativosPro

## Status: Pronto para Aprovação e Execução

---

## 📊 Resumo Executivo

**Arquivos Auditados**: 8/50+ (16% concluído)  
**Achados Totais**: 15  
**Críticos**: 4 | **Altos**: 3 | **Médios**: 5 | **Baixos**: 3

---

## 🔴 PRIORIDADE CRÍTICA (Executar Imediatamente)

### 1. Operações Síncronas Bloqueando Event Loop
**Problema**: `history_manager.py` e `database.py` executam SQLite de forma síncrona, bloqueando o asyncio.  
**Impacto**: Delay entre mensagens, sistema trava.  
**Solução**:
```python
# Envolver todas as operações de DB em asyncio.to_thread
async def add_message(self, session_id, role, content, metadata=None):
    await asyncio.to_thread(self._add_message_sync, session_id, role, content, metadata)
```
**Arquivos**: `backend/core/history_manager.py`, `backend/core/database.py`  
**Esforço**: Médio (2-3h)

---

### 2. CORS Totalmente Aberto
**Problema**: `cors_allowed_origins='*'` permite qualquer origem.  
**Impacto**: Vulnerável a CSRF.  
**Solução**:
```python
cors_allowed_origins=['http://localhost:5173', 'http://127.0.0.1:5173']
```
**Arquivo**: `backend/core/main.py:12`  
**Esforço**: Pequeno (5min)

---

### 3. Chave de Criptografia em Arquivo Local
**Problema**: `security.key` armazenada em texto plano.  
**Impacto**: Vazamento de API keys.  
**Solução**:
- Adicionar `security.key` ao `.gitignore`
- Documentar regeneração de chave
- (Futuro) Migrar para keyring do SO
**Arquivo**: `backend/core/database.py:6-22`  
**Esforço**: Pequeno (15min)

---

### 4. Falta de Tratamento de Erros em Eventos Socket
**Problema**: Eventos sem try/except podem travar o socket.  
**Impacto**: Cliente fica sem resposta.  
**Solução**:
```python
@sio.event
async def delete_session(sid, data):
    try:
        # código atual
    except Exception as e:
        await sio.emit("error", {"message": str(e)}, to=sid)
```
**Arquivo**: `backend/core/main.py` (múltiplos eventos)  
**Esforço**: Médio (1h)

---

## 🟠 PRIORIDADE ALTA (Executar Esta Semana)

### 5. Memory Leak - Arquivos de Áudio Não Limpos
**Problema**: `temp_audio/` acumula arquivos indefinidamente (16 já existentes).  
**Impacto**: Disco cheio após uso prolongado.  
**Solução**:
- Criar job de limpeza automática (arquivos > 24h)
- Limitar a 100 arquivos (FIFO)
**Arquivo**: `backend/core/tts_service.py` + novo script  
**Esforço**: Pequeno (30min)

---

### 6. Falta de Índices no Banco de Dados
**Problema**: Queries em `history` e `metrics` sem índices.  
**Impacto**: Lentidão com histórico grande.  
**Solução**:
```sql
CREATE INDEX IF NOT EXISTS idx_history_session ON history(session_id);
CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_session ON metrics(session_id);
```
**Arquivo**: `backend/core/database.py:24-124`  
**Esforço**: Pequeno (15min)

---

### 7. Validação de Inputs
**Problema**: Dados do frontend não são validados antes de inserir no DB.  
**Impacto**: Possível SQL injection ou dados corrompidos.  
**Solução**:
- Adicionar validação de tipos e tamanhos em `controller.py`
- Sanitizar strings antes de salvar
**Arquivo**: `backend/core/controller.py:15-28`  
**Esforço**: Médio (1h)

---

## 🟡 PRIORIDADE MÉDIA (Melhorias de UX)

### 8. Animações no Menu de Configurações
**Problema**: Botões de tab sem animações (conforme imagens fornecidas).  
**Impacto**: UX menos polida.  
**Solução**:
```tsx
// Adicionar transitions e hover effects
className="... transition-all duration-300 hover:scale-105"
```
**Arquivo**: `frontend/src/components/SettingsView.tsx:295-308`  
**Esforço**: Pequeno (30min)

---

### 9. Botão "SALVAR ALTERAÇÕES" Sem Feedback Visual Adequado
**Problema**: Feedback existe mas pode ser melhorado com toast notification.  
**Impacto**: Usuário não tem certeza se salvou.  
**Solução**:
- Adicionar toast/notification library (react-hot-toast)
- Ou criar componente de notificação customizado
**Arquivo**: `frontend/src/components/SettingsView.tsx:606-636`  
**Esforço**: Médio (1h)

---

### 10. Seletores de Engine/Modelo Muito Básicos
**Problema**: Dropdown nativo sem estilo (conforme imagens).  
**Impacto**: Aparência genérica.  
**Solução**:
- Criar componente customizado de dropdown
- Adicionar ícones para cada provedor
- Animações de abertura/fechamento
**Arquivo**: `frontend/src/App.tsx:293-327`  
**Esforço**: Grande (2-3h)

---

### 11. Falta de Loading States
**Problema**: Sem skeleton loaders ao trocar views.  
**Impacto**: Flashes de conteúdo vazio.  
**Solução**:
- Adicionar skeleton components
- Fade in/out transitions
**Arquivo**: `frontend/src/App.tsx:338-358`  
**Esforço**: Médio (1h)

---

### 12. Falta de Animações nos Botões Globais
**Problema**: Botões sem hover effects ou ripple.  
**Impacto**: Interface estática.  
**Solução**:
```css
.button:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(59,130,246,0.3); }
.button:active { transform: scale(0.95); }
```
**Arquivo**: `frontend/src/index.css` + componentes  
**Esforço**: Pequeno (30min)

---

## 🟢 PRIORIDADE BAIXA (Manutenibilidade)

### 13. Imports Dentro de Funções
**Problema**: Imports repetidos dentro de event handlers.  
**Impacto**: Código menos legível.  
**Solução**: Mover todos os imports para o topo do arquivo.  
**Arquivo**: `backend/core/main.py`  
**Esforço**: Pequeno (15min)

---

### 14. Falta de Logging Estruturado
**Problema**: Uso de `print()` ao invés de `logging`.  
**Impacto**: Difícil debugar em produção.  
**Solução**:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Mensagem")
```
**Arquivo**: Todos os arquivos backend  
**Esforço**: Médio (2h)

---

### 15. Console.logs Esquecidos
**Problema**: Múltiplos `console.log` no código de produção.  
**Impacto**: Logs poluídos no navegador.  
**Solução**: Remover ou envolver em `if (process.env.NODE_ENV === 'development')`.  
**Arquivo**: `frontend/src/components/SettingsView.tsx` (linhas 46, 68, 75, 82, etc)  
**Esforço**: Pequeno (15min)

---

## 📅 Roadmap de Implementação

### Fase 1: Correções Críticas (Hoje)
- [ ] CORS fix
- [ ] Chave de criptografia no .gitignore
- [ ] Try/catch em eventos socket
- [ ] Operações assíncronas no DB (início)

### Fase 2: Performance e Segurança (Esta Semana)
- [ ] Finalizar operações assíncronas
- [ ] Índices no banco
- [ ] Limpeza de arquivos TTS
- [ ] Validação de inputs

### Fase 3: Melhorias de UX (Próxima Semana)
- [ ] Animações no menu de configurações
- [ ] Melhorar botão de salvar
- [ ] Customizar seletores de modelo
- [ ] Loading states e transitions

### Fase 4: Polimento (Futuro)
- [ ] Logging estruturado
- [ ] Remover console.logs
- [ ] Refatorar imports
- [ ] Documentação completa

---

## 🎨 Melhorias Específicas de UI (Baseado nas Imagens)

### Menu de Configurações:
1. **Tabs Laterais**: Adicionar animação de slide ao trocar
2. **Botão "SALVAR"**: 
   - Ripple effect ao clicar
   - Toast notification ao salvar
   - Pulse animation durante "saving"
3. **Seletores de Provedor**: Adicionar ícones e cores específicas
4. **Toggle Switches**: Já estão bons, manter

### Seletores de Engine/Modelo (Tela Principal):
1. **Dropdown Customizado**:
   - Substituir `<select>` nativo
   - Adicionar ícones (🧠 para cada engine)
   - Animação de abertura suave
   - Highlight no hover
2. **Labels**: Manter "ENGINE" e "ARQUITETURA" mas com micro-animações

---

## ✅ Critérios de Aceitação

Cada correção deve:
- [ ] Passar em testes manuais
- [ ] Não quebrar funcionalidades existentes
- [ ] Seguir padrões de código do projeto
- [ ] Ser documentada no commit

---

**Próximo Passo**: Aprovação do usuário para iniciar Fase 1.
