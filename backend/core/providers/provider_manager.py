from core.providers.base_provider import BaseProvider
from core.providers.ollama.provider import Provider as OllamaProvider
from core.providers.lmstudio.provider import Provider as LMStudioProvider
from core.logger import root_logger as logger

class ProviderManager:
    """Gerencia os provedores de IA locais (Ollama e LM Studio)."""
    
    def __init__(self):
        self.providers = {}

    def get_provider(self, provider_name: str, api_key: str, force_reload: bool = False) -> BaseProvider:
        """
        Retorna uma instância do provedor solicitado.
        Suporta apenas: ollama, lmstudio
        """
        if not force_reload and provider_name in self.providers:
            return self.providers[provider_name]

        try:
            if provider_name == 'ollama':
                instance = OllamaProvider(api_key)
            elif provider_name == 'lmstudio':
                instance = LMStudioProvider(api_key)
            else:
                logger.warning(f"Provedor '{provider_name}' não suportado.")
                return None
            
            self.providers[provider_name] = instance
            return instance

        except Exception as e:
            logger.error(f"Erro ao carregar provedor '{provider_name}': {e}")
            import traceback
            traceback.print_exc()
            return None

# Instância global
provider_manager = ProviderManager()
