from core.providers.base_provider import BaseProvider
from openai import AsyncOpenAI

class Provider(BaseProvider):
    """Implementação do provedor Ollama."""
    
    def __init__(self, api_key: str = "none"):
        super().__init__(api_key)
        
        # Busca URL configurada ou usa default
        from core.database import db
        base_url = db.get_setting("base_url_ollama", "http://localhost:11434/v1")
        
        # Garantir que termina com /v1 se o usuário esquecer, mas cuidado para não duplicar
        if not base_url.endswith("/v1"):
             # Algumas libs precisam do /v1, outras não. O OpenAI Client python geralmente anexa endpoints.
             # Mas para Ollama, explicitamente requer /v1 para compatibilidade OpenAI.
             base_url = f"{base_url.rstrip('/')}/v1"

        print(f"[Ollama] Inicializando com URL: {base_url}")
        
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="ollama", # Key dummy
        )

    async def list_models(self):
        try:
            print(f"[Ollama] Listando modelos em {self.client.base_url}")
            response = await self.client.models.list()
            print(f"[Ollama] Modelos encontrados: {len(response.data)}")
            return [model.id for model in response.data]
        except Exception as e:
            print(f"[Ollama] Erro CRÍTICO ao listar modelos: {e}")
            return []

    async def generate_response(self, model: str, messages: list, stream: bool = True):
        try:
            return await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
        except Exception as e:
            print(f"[Ollama] Erro na geração: {e}")
            raise e

    def get_metrics(self, response):
        """Extrai tokens e custo da resposta."""
        # Ollama local não tem custo, apenas uso de tokens se disponível no chunk final
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0.0,
            "latency": 0.0
        }
