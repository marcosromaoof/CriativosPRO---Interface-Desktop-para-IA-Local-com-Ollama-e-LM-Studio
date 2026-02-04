# Plano de Diagnóstico e Correção - Problema de Áudio 0 KB

## 1. Hipótese
O comando `voice.synthesize(text, wav_file)` da biblioteca `piper` pode não estar escrevendo corretamente no objeto `wave` quando este já foi inicializado com `setnchannels` etc, OU pode estar ocorrendo uma exceção silenciosa dentro da biblioteca C++ (subjacente ao piper-python) que não está sendo capturada pelo Python wrapper, resultando em um arquivo aberto (`wb`) mas vazio.

Outra possibilidade é que a versão do `piper-tts` instalada espere um nome de arquivo (string) em `synthesize()` em vez de um objeto de arquivo aberto, ou vice-versa, dependendo da versão. 
Na documentação do projeto original (rhasspy/piper), a função `synthesize` geralmente aceita um iterador de áudio raw (PCM) se chamada de certa forma, ou escreve num arquivo wav se outra. O wrapper python `piper-tts` (se for o oficial) tem:
```python
def synthesize(self, text: str, wav_file: wave.Wave_write, **kwargs)
```
Isso **deveria** funcionar. SE o arquivo está ficando vazio, talvez o texto esteja chegando vazio?

## 2. Testes de Diagnóstico
Vou criar o script `scripts/debug_tts_deep.py` para testar 3 cenários isolados:

1.  **Cenário A:** Usar o método atual (`wave.open` + `synthesize`).
2.  **Cenário B:** Usar `synthesize_stream_raw` (se existir) e escrever os bytes manualmente.
3.  **Cenário C:** Verificar se a limpeza do texto (`_clean_text`) não está removendo tudo.

## 3. Ação Corretiva
Se o Cenário A falhar (arquivo 0 bytes) e o B funcionar, mudaremos a implementação em `tts_service.py` para usar raw stream.

## 4. Auditoria de Regras
Este plano segue a regra "Zero Improviso" ao isolar o problema antes de tentar corrigir cegamente.
