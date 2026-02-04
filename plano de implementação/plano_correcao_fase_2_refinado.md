# 🛠️ Plano de Correção e Ajuste - Revisão Fase 2

Este documento detalha as etapas para corrigir falhas de infraestrutura (Piper), lógica (Histórico/Perfil) e UI (Botões), conforme solicitação do usuário.

**Status**: Aguardando Aprovação para Início ✅

---

## 🟥 Fase 1: Identidade e Perfil do Usuário
**Problema**: O modelo não sabe quem é o usuário (Nome, Sexo, etc.), ignorando as configurações salvas.
**Solução**: Injetar dados do perfil no Prompt do Sistema.

- [x] **1.1 Ajuste no Backend (`controller.py`)**
    - [x] Importar perfil via `config.get_user_profile()`.
    - [x] Formatar string de contexto (ex: "User Name: Marcos. User Gender: Male.").
    - [x] Anexar esta string ao `system_prompt` antes de enviar para o provedor.

**Regras Específicas:**
- Obedecer estritamente `@[plano de implementação/regras_projeto.md]`.
- Qualquer dúvida técnica sobre formato dos dados, perguntar ao usuário.

---

## 🟧 Fase 2: Correção Lógica de Histórico
**Problema**: Mensagens "Oi" salvam histórico indevidamente ao abrir o app / "Nova Conversa" não cria sessão limpa.
**Causa**: Frontend está usando ID fixo "default", fazendo o backend reaproveitar sessões antigas e ignorar filtros de "nova sessão".

- [x] **2.1 Geração de ID no Frontend (`App.tsx`)**
    - [x] Implementar gerador de UUID (v4/random) para novas conversas.
    - [x] Ao clicar em "Novo Chat", gerar novo `sessionId` em vez de limpar apenas a lista visual.

- [x] **2.2 Refinamento no Backend (`history_manager.py`)**
    - [x] Garantir que o filtro `_check_smart_persistence` funcione corretamente com IDs únicos (Validado pela lógica existente: ID novo inicia sem registros, filtro aplica na primeira msg).
    - [x] Confirmar exclusão de saudações curtas ("oi", "olá") para sessões novas.

**Regras Específicas:**
- Obedecer estritamente `@[plano de implementação/regras_projeto.md]`.
- Garantir que não haja regressão funcional (o chat deve continuar funcionando).

---

## 🟨 Fase 3: Interface e UX
**Problema**: Botões de ação (Copiar, Ouvir, etc.) somem e dificultam uso.
**Solução**: Remover efeito de hover, deixando ações fixas.

- [x] **3.1 Ajuste no Componente (`MessageBubble.tsx`)**
    - [x] Remover classes `opacity-0` e `group-hover:opacity-100`.
    - [x] Garantir que o layout (Ações Esq / Métricas Dir) se mantenha estável.

**Regras Específicas:**
- Obedecer estritamente `@[plano de implementação/regras_projeto.md]`.

---

## 🟦 Fase 4: Infraestrutura de Áudio (Piper)
**Problema**: "Piper não funciona". Pasta contém código-fonte, não executável.
**Estratégia**: Tentar instalar `piper-tts` via Python (pip). Se falhar, pedir download do binário Windows.

- [x] **4.1 Verificação e Movimentação**
    - [x] Arquivos movidos de `github` para `backend/bin/piper`.
    - [x] Modelo de voz `pt_BR-faber-medium.onnx` localizado.

- [x] **4.2 Instalação e Integração**
    - [x] `pip install piper-tts` realizado com sucesso pelo usuário.
    - [x] `tts_service.py` reescrito para utilizar biblioteca Python `piper` (Opção 1).
    - [x] Integração concluída.

**Regras Específicas:**
- Obedecer estritamente `@[plano de implementação/regras_projeto.md]`.
- Validar caminhos absolutos no Windows.

---

**⚠️ AVISO**: Seguiremos etapa por etapa. Só avançaremos após sua aprovação explícita de cada fase.
