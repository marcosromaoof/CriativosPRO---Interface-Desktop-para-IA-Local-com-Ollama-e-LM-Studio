from core.providers.base_provider import BaseProvider
from openai import AsyncOpenAI

class Provider(BaseProvider):
    """Implementação do provedor HuggingFace Inference API."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = AsyncOpenAI(
            base_url="https://api-inference.huggingface.co/v1/",
            api_key=self.api_key,
        )

    async def list_models(self):
        # HuggingFace tem milhares de modelos, costumamos definir os que queremos suportar
        return ["mistralai/Mistral-7B-v0.1", "google/gemma-7b"]

    async def generate_response(self, model: str, messages: list, stream: bool = True):
        try:
            return await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
        except Exception as e:
            print(f"[HuggingFace] Erro na geração: {e}")
            raise e
