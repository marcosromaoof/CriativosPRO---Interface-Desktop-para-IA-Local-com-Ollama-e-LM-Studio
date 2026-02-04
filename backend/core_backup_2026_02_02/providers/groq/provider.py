from openai import AsyncOpenAI
from core.providers.base_provider import BaseProvider

class Provider(BaseProvider):
    """Implementação do provedor Groq (Ultra Fast Inference)."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=self.api_key
        )

    async def list_models(self):
        """Busca modelos disponíveis no Groq."""
        try:
            response = await self.client.models.list()
            return [model.id for model in response.data]
        except Exception as e:
            print(f"[Groq] Erro ao listar modelos: {e}")
            return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]

    async def generate_response(self, model: str, messages: list, stream: bool = True):
        """Gera resposta via streaming usando a API do Groq."""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
            return response
        except Exception as e:
            print(f"[Groq] Erro na geração: {e}")
            raise e

    def get_metrics(self, response):
        """Extrai métricas de tokens do Groq."""
        return {
            "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
            "completion_tokens": getattr(response.usage, 'completion_tokens', 0)
        }
