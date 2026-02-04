from openai import AsyncOpenAI
from core.providers.base_provider import BaseProvider

class Provider(BaseProvider):
    """Implementação do provedor DeepSeek."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            self.client = AsyncOpenAI(
                base_url="https://api.deepseek.com",
                api_key=self.api_key or "sk-placeholder" # Evita erro de init se key for None/Empty
            )
        except Exception as e:
            print(f"[DeepSeek] Falha ao iniciar cliente: {e}")
            self.client = None # Explicitamente None, tratado no list_models


    async def list_models(self):
        """Lista os modelos oficiais disponíveis no DeepSeek."""
        if not self.client or self.api_key in [None, "", "none"]:
             # Sem chave, não tenta conectar, retorna lista padrão
             return ["deepseek-chat", "deepseek-reasoner"]

        try:
            response = await self.client.models.list()
            return [model.id for model in response.data]
        except Exception as e:
             # Erro de conexão ou auth
            print(f"[DeepSeek] Erro ao listar modelos (usando fallback): {e}")
            return ["deepseek-chat", "deepseek-reasoner"]
        except Exception as e:
            print(f"[DeepSeek] Erro ao listar modelos: {e}")
            # Fallback para os modelos conhecidos se a listagem falhar
            return ["deepseek-chat", "deepseek-reasoner"]

    async def generate_response(self, model: str, messages: list, stream: bool = True):
        """Gera resposta via streaming usando a API do DeepSeek."""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
            return response
        except Exception as e:
            print(f"[DeepSeek] Erro na geração: {e}")
            raise e

    def get_metrics(self, response):
        """Extrai métricas de uso do DeepSeek."""
        return {
            "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
            "completion_tokens": getattr(response.usage, 'completion_tokens', 0)
        }
