from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """Interface abstrata obrigatória para todos os provedores de IA."""
    
    @abstractmethod
    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def list_models(self):
        """Retorna uma lista de modelos disponíveis para este provedor."""
        pass

    @abstractmethod
    async def generate_response(self, model: str, messages: list, stream: bool = True):
        """
        Gera uma resposta da IA.
        Deve retornar um gerador assíncrono se stream=True.
        """
        pass

    @abstractmethod
    def get_metrics(self, response):
        """Extrai tokens, latência e outras métricas da resposta da API."""
        pass
