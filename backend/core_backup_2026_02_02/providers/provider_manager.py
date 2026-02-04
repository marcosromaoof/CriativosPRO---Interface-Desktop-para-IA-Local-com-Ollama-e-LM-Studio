import importlib
import os
from core.providers.base_provider import BaseProvider

class ProviderManager:
    """Gerencia a carga e instância de diferentes provedores de IA."""
    
    def __init__(self):
        self.providers = {}

    def get_provider(self, provider_name: str, api_key: str, force_reload: bool = False) -> BaseProvider:
        """
        Retorna uma instância do provedor solicitado.
        Implementa cache de instâncias para evitar reinicializações desnecessárias.
        """
        if not force_reload and provider_name in self.providers:
            return self.providers[provider_name]

        try:
            # Importação dinâmica do módulo do provedor
            # Espera-se a estrutura: core/providers/{name}/provider.py
            module_path = f"core.providers.{provider_name}.provider"
            module = importlib.import_module(module_path)
            
            # Busca a classe Provider no módulo importado
            provider_class = getattr(module, "Provider")
            
            if issubclass(provider_class, BaseProvider):
                instance = provider_class(api_key)
                self.providers[provider_name] = instance
                return instance
            else:
                raise TypeError(f"A classe Provider em {module_path} não herda de BaseProvider.")

        except (ImportError, AttributeError, TypeError) as e:
            print(f"[ProviderManager] Erro ao carregar provedor '{provider_name}': {e}")
            return None

# Instância global
provider_manager = ProviderManager()
