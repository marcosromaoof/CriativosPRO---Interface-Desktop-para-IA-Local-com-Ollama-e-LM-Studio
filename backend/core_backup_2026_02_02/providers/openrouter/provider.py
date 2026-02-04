from openai import AsyncOpenAI
from core.providers.base_provider import BaseProvider

class Provider(BaseProvider):
    """Implementação do provedor OpenRouter."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "https://criativospro.com", # Identificador para OpenRouter
                "X-Title": "CriativosPro Desktop",
            }
        )

    async def list_models(self):
        """Busca a lista de modelos disponíveis no OpenRouter."""
        try:
            # Nota: No OpenRouter, costumamos filtrar ou retornar os principais
            # por simplicidade técnica nesta fase inicial.
            response = await self.client.models.list()
            return [model.id for model in response.data]
        except Exception as e:
            print(f"[OpenRouter] Erro ao listar modelos: {e}")
            return []

    async def generate_response(self, model: str, messages: list, stream: bool = True):
        """Gera resposta via streaming usando a API do OpenRouter."""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
            return response
        except Exception as e:
            print(f"[OpenRouter] Erro na geração: {e}")
            raise e

    def get_metrics(self, response):
        """
        Extrai métricas. 
        Nota: No streaming, métricas de tokens costumam vir no último chunk 
        ou precisam ser estimadas.
        """
        # Implementação específica de extração de tokens do OpenRouter
        return {
            "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
            "completion_tokens": getattr(response.usage, 'completion_tokens', 0)
        }
