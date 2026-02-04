# Plano de Correção Definitiva de Carregamento de Provedores (PyInstaller)

O sistema apresenta falhas consistentes de "Driver não carregado" para todos os provedores (DeepSeek, Ollama, etc.) na versão compilada (`.exe`), embora funcione em ambiente de desenvolvimento.

**Causa Raiz Identificada:**
O PyInstaller, por padrão, não detecta importações dinâmicas feitas via `importlib.import_module("string_calculada")`. Como os provedores são carregados dinamicamente com base nos nomes das pastas, seus módulos (`provider.py`, `brain.py`) não são incluídos no pacote final do Python, gerando `ModuleNotFoundError` que é capturado e tratado como falha genérica de carregamento.

Este plano visa corrigir isso explicitamente, seguindo as regras de engenharia robusta (sem gambiarras).

## Etapas de Implementação

1.  **Auditoria e Diagnóstico (Concluído)**
    - Verificado logs: Erro "Falha ao carregar driver".
    - Verificado código `provider_manager.py`: Usa `importlib`.
    - Verificado build anterior: Não possui `--hidden-import` para os provedores.

2.  **Preparação do Build (Ação Imediata)**
    - [ ] Modificar `build_release.bat` para incluir `--hidden-import` explícito para todos os módulos de provedores conhecidos.
    - [ ] Lista de Módulos:
        - `core.providers.deepseek.provider` / `.brain`
        - `core.providers.groq.provider` / `.brain`
        - `core.providers.openrouter.provider` / `.brain`
        - `core.providers.ollama.provider` / `.brain`
        - `core.providers.lmstudio.provider` / `.brain`
        - `core.providers.huggingface.provider` / `.brain`
        - `core.providers.base_provider` (já deve estar, mas garantir)

3.  **Melhoria de Robustez (Código)**
    - [ ] Alterar `provider_manager.py` para logar o erro exato (`traceback`) no console, facilitando diagnósticos futuros se novos provedores forem adicionados e falharem.

4.  **Compilação e Validação**
    - [ ] Executar `force_clean.bat`.
    - [ ] Executar `build_release.bat`.
    - [ ] Validar funcionamento do executável final.

## Check-list de Execução
- [ ] Atualizar `provider_manager.py` com melhores logs.
- [ ] Atualizar `build_release.bat` com todos os imports ocultos.
- [ ] Compilar.
