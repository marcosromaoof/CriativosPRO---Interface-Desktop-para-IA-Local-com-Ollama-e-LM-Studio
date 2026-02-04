# Plano de Correção: Glitches de Texto (Typewriter Effect)

## 1. Problema Identificado
O usuário relata "erros de gramática" no texto exibido, apesar do áudio/conteúdo original estar correto.
**Diagnóstico:** O hook `useTypewriter` utiliza concatenação incremental (`prev + char`). Isso é frágil. Se houver condições de corrida (race conditions), re-renderizações inesperadas ou falhas no ciclo do React, caracteres podem ser duplicados, trocados ou omitidos na visualização, criando palavras erradas visualmente (ex: "casa" vira "ccasa" ou "csa").

## 2. Solução Técnica
Refatorar `frontend/src/hooks/useTypewriter.ts` para usar **Slicing** (fatiamento) em vez de acumulação.

### Abordagem Atual (Frágil):
```typescript
setDisplayedText(prev => prev + char) // Depende do estado anterior estar perfeito
```

### Nova Abordagem (Robusta):
```typescript
setDisplayedText(text.slice(0, currentIndex)) // Deriva sempre do texto original (Fonte da Verdade)
```
Isso garante que o texto exibido seja SEMPRE um subconjunto exato do texto real vindo do backend. Se o índice pular ou travar, no próximo quadro ele se autocorrige, jamais exibindo caracteres "inventados" ou fora de ordem.

## 3. Checklist de Execução
- [ ] **Editar `useTypewriter.ts`**:
    - [ ] Mudar lógica de atualização de estado.
    - [ ] Remover dependência cíclica de `displayedText` no `useEffect` (que causa renders excessivos).
    - [ ] Otimizar performance do timer.

## 4. Auditoria
Essa mudança é puramente de lógica de apresentação no Frontend. Não afeta o Backend nem o TTS. Resolve o problema visual garantindo integridade dos dados 1:1 com o que foi gerado.
