# Plano de Correção: TTS (Caracteres Especiais) e Formatação de Texto

## 1. Problemas Identificados
1.  **TTS (Áudio):** O sistema está lendo caracteres especiais do Markdown (ex: `*`, `#`, `_`) e possivelmente emojis/códigos, tornando o áudio sujo ou confuso.
2.  **Formatação Visual (Chat):** O texto gerado aparece "mal organizado", sem quebra de linhas, parágrafos ou títulos visíveis.

## 2. Diagnóstico Técnico
### 2.1. TTS Service (`tts_service.py`)
A função `_clean_text` atual remove apenas alguns padrões de markdown, mas deixa passar muitos símbolos e não filtra emojis ou caracteres não-imprimíveis que confundem o `piper.exe`.

### 2.2. Visualização (`MessageBubble.tsx`)
O componente `ReactMarkdown` está customizando a tag `<p>` (parágrafo) com a classe `mb-0` (margem inferior zero).
-   **Consequência:** Parágrafos consecutivos grudam uns nos outros, criando uma "parede de texto" impossível de ler.
-   **Títulos:** O plugin `tailwindcss-typography` (`prose`) geralmente lida bem com títulos, mas verifica-se se estão sendo inibidos.

## 3. Solução Proposta

### Tarefa 1: Refatorar Limpeza de Texto p/ TTS (Backend)
Atualizar `_clean_text` em `tts_service.py` para uma abordagem de "Lista Branca" (Whitelist).
-   **Permitir:** Letras (incluindo acentos PT-BR), números, pontuação básica (`.,!?;:`), aspas e hífen.
-   **Remover:** Todo o resto (emojis, símbolos matemáticos complexos, markdown residual).
-   **Estratégia:**
    1.  Remover Blocos de Código e Links.
    2.  Substituir símbolos markdown comuns por espaço.
    3.  Aplicar Regex de Whitelist.

### Tarefa 2: Corrigir Estilo CSS do Chat (Frontend)
Editar `MessageBubble.tsx`:
-   Alterar o componente customizado `p` para ter `mb-4` (espaçamento padrão de parágrafo) em vez de `mb-0`.
-   Garantir que estilos de títulos (`h1`, `h2`, `h3`) estejam visíveis (adicionar custom components se o `prose` falhar).

## 4. Checklist de Execução

- [ ] **Passo 1: Melhorar `tts_service.py`**
    - [ ] Atualizar método `_clean_text` com regex robusto para PT-BR.
    - [ ] Testar se remove emojis e `*` usados para negrito.

- [ ] **Passo 2: Ajustar `MessageBubble.tsx`**
    - [ ] Mudar style do `p` para `mb-3` ou `mb-4`.
    - [ ] Adicionar estilos explícitos para `h1, h2, h3` para garantir hierarquia visual (texto maior e negrito).
    - [ ] Adicionar estilo para lista `ul/ol` (padding-left).

- [ ] **Passo 3: Validação**
    - [ ] Gerar áudio e ouvir se limpo.
    - [ ] Verificar visualmente uma resposta longa no chat.

## 5. Auditoria
As mudanças respeitam a arquitetura existente, apenas aprimorando a lógica de tratamento de dados e estilos CSS. Nenhuma nova dependência será adicionada.
