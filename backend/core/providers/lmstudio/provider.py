from core.providers.base_provider import BaseProvider
from openai import AsyncOpenAI

class Provider(BaseProvider):
    """Implementação do provedor LM Studio."""
    
    def __init__(self, api_key: str = "none"):
        super().__init__(api_key)
        
        # Busca URL configurada ou usa default
        from core.database import db
        base_url = db.get_setting("base_url_lmstudio", "http://localhost:1234/v1")

        # Garantir que termina com /v1
        if not base_url.endswith("/v1"):
             base_url = f"{base_url.rstrip('/')}/v1"
        
        print(f"[LMStudio] Inicializando com URL: {base_url}")
        
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="lm-studio",
        )

    async def list_models(self):
        try:
            print(f"[LMStudio] Listando modelos em {self.client.base_url}")
            response = await self.client.models.list()
            print(f"[LMStudio] Modelos encontrados: {len(response.data)}")
            return [model.id for model in response.data]
        except Exception as e:
            print(f"[LMStudio] Erro CRÍTICO ao listar modelos: {e}")
            # LM Studio as vezes não responde bem ao list, retornamos default se falhar
            return ["lm-studio-model"]

    async def generate_response(self, model: str, messages: list, stream: bool = True):
        try:
            return await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
        except Exception as e:
            print(f"[LMStudio] Erro na geração: {e}")
            raise e

    def get_metrics(self, response):
        """Extrai tokens e custo da resposta."""
        # LM Studio local não tem custo
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0.0,
            "latency": 0.0
        }
