from core.providers.lmstudio.provider import Provider

async def create_brain(api_key: str):
    """Inicializa e retorna os modelos do LM Studio."""
    provider = Provider(api_key)
    return await provider.list_models()
