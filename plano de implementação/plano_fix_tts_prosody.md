# Plano de Melhoria: Prosódia e Ritmo do Áudio (TTS)

## 1. Problema Identificado
O áudio gerado pelo `piper.exe` está "corrido", ignorando pausas naturais de vírgulas, pontos e parágrafos. A fala parece uma sentença única e contínua.
**Causa Principal:** O pré-processamento `_clean_text` substitui quebras de linha (`\n`) por espaços simples e não preserva a estrutura, fazendo com que "Título\nConteúdo" vire "Título Conteúdo" para o TTS, que lê sem pausa. Além disso, a simples presença de pontuação às vezes não é suficiente se a velocidade do modelo for alta ou se a frase for muito longa.

## 2. Diagnóstico Técnico
No `tts_service.py`:
```python
# 6. Normalizar espaços (remove duplos e trim)
text = " ".join(text.split()) # ISSO REMOVE TODAS AS QUEBRAS DE LINHA!
```
Ao fazer `text.split()`, removemos `\n` e `\r`. Sem quebras de linha ou pausas explícitas, o Piper lê direto.

## 3. Solução Proposta

### Estratégia de "Prosódia Artificial"
Vamos injetar pausas explícitas que o Piper entenda. Geralmente, `.` gera uma pausa média e `,` uma pausa curta. Quebras de parágrafo deveriam ser pausas longas.

1.  **Pré-processamento Inteligente:**
    *   Substituir Markdown Headers (`# Título`) por `Título...` (pausa forçada).
    *   Substituir Listas (`- Item`) por `Item.`.
    *   Substituir Quebras de Linha Duplas (`\n\n` - Parágrafos) por `...` ou uma combinação que force silêncio.
    *   Substituir Quebras Simples (`\n`) por vírgula ou espaço (depende do contexto, mas `.` é mais seguro para evitar leitura corrida).

2.  **Ajuste no Regex:**
    *   Não remover indiscriminadamente `*` e `#` antes de tratar seu significado semântico (títulos/listas).
    *   Primeiro converter estrutura markdown em pontuação, DEPOIS limpar os caracteres.

### Novo Fluxo de Limpeza:
1.  Headers (`# Texto`) -> `Texto.`
2.  Bold/Italic (`*Texto*`) -> `Texto` (ênfase dificilmente aplicável no piper simples, melhor remover).
3.  Listas (`- Texto`) -> `Texto.`
4.  Novas Linhas (`\n`) -> Substituir por `. ` (Ponto e espaço). Isso força o TTS a respirar a cada linha quebrada.

## 4. Checklist de Execução

- [ ] **Editar `tts_service.py`**:
    - [ ] Refazer `_clean_text`.
    - [ ] Etapa 1: Substituir `\n+` (múltiplos enters) por `. ` (ponto final fake).
    - [ ] Etapa 2: Substituir `:` por `: ` (garantir espaço).
    - [ ] Etapa 3: Aplicar Whitelist (mas preservando os pontos que acabamos de inserir).

## 5. Auditoria
Essa alteração visa melhorar a **experiência auditiva**. Não altera o texto visual exibido no chat, apenas o input enviado para o gerador de áudio.
