from core.providers.groq.provider import Provider

async def create_brain(api_key: str):
    """Inicializa o cérebro do Groq e retorna modelos disponíveis."""
    provider_instance = Provider(api_key)
    models = await provider_instance.list_models()
    return models
