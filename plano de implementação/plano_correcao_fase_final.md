# 📋 Checklist de Correção e Implementação Final
Este documento detalha as etapas necessárias para corrigir as funcionalidades faltantes e alinhar o sistema aos requisitos do usuário.

**Status Atual**: Auditoria Realizada. Aguardando Aprovação.

---

## 🟥 Fase 1: Interface e Ações da Mensagem
**Objetivo**: Implementar botões de ação e corrigir layout do `MessageBubble`.

- [x] **1.1 Layout do Rodapé (`MessageBubble.tsx`)**
    - [x] Reorganizar rodapé com Flexbox: Métricas à esquerda, Ações à direita. (Ajustado: Ações Esq, Métricas Dir)
    - [x] Garantir que ações só apareçam em mensagens do Assistente (Bot), exceto "Copiar" e "Excluir" que podem ser para ambos.

- [x] **1.2 Botões de Ação**
    - [x] Implementar Botão **Ouvir** (Ícone `Volume2`): Emite evento para backend gerar áudio.
    - [x] Implementar Botão **Copiar** (Ícone `Copy`): Copia conteúdo para clipboard com feedback visual.
    - [x] Implementar Botão **Excluir** (Ícone `Trash2`): Remove mensagem visualmente e do histórico.
    - [x] Implementar Botão **Reenviar** (Ícone `RefreshCw`): Apenas para última mensagem do bot.
    - [x] Implementar Botão **Download** (Ícone `Download`): Salva conteúdo como .txt ou .md.

---

## 🟧 Fase 2: Lógica de Histórico Inteligente
**Objetivo**: Corrigir persistência e implementar regras de negócio para salvar sessões.

- [x] **2.1 Correção de Persistência (`history_manager.py`)**
    - [x] Garantir que a tabela `sessions` seja populada corretamente não apenas ao definir título, mas ao criar sessão válida.
    - [x] Corrigir bug onde histórico desaparece ao reiniciar a aplicação.

- [x] **2.2 Regras de Filtragem ("Smart History")**
    - [x] Modificar `add_message`: Implementar verificação de comprimento (> 250 caracteres).
    - [x] Implementar lista negra de saudações (ex: "oi", "ola", "bom dia") para não iniciar persistência.
    - [x] Lógica: Uma sessão só é salva na lista de "Recentes" se tiver pelo menos uma mensagem qualificada.

- [x] **2.3 Geração de Títulos**
    - [x] Criar gatilho: Ao atingir a primeira mensagem > 250 chars, chamar LLM (modelo rápido ou regra) para gerar título resumido (estilo ChatGPT). (Simulado com 5 primeiras palavras por enquanto)
    - [x] Atualizar título no banco de dados.

---

## 🟨 Fase 3: Sistema de Áudio (TTS)
**Objetivo**: Conectar frontend ao Piper TTS backend.

- [x] **3.1 Backend (`main.py` + `tts_service.py`)**
    - [x] Criar evento socket `tts_generate`: Recebe texto ID, chama Piper.
    - [x] Retornar URL do áudio gerado para o frontend tocar.
    - [x] Validação: Verificar se modelo no `bin/piper` é PT-BR (WAV/ONNX).

- [x] **3.2 Frontend Integration**
    - [x] Gerenciar estado de "Tocando" no `MessageBubble`.
    - [x] Adicionar elemento `<audio>` oculto ou visível para playback.

---

## 🟦 Fase 4: Gestão de Histórico (UI Lateral)
**Objetivo**: Permitir exclusão de conversas antigas.

- [x] **4.1 Botão de Exclusão na Sidebar**
    - [x] Adicionar ícone de lixeira (Trash) ao lado de cada item na lista de sessões recentes.
    - [x] Implementar evento de exclusão no backend (`delete_session`).
    - [x] Atualizar lista em tempo real.

---
**🛑 PONTO DE PARADA**: Não iniciar implementação sem aprovação explícita deste plano.
**Regras**: Seguir estritamente `@[plano de implementação/regras_projeto.md]`.
