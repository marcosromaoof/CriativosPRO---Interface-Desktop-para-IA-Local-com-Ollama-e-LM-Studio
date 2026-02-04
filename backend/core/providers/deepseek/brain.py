from core.providers.deepseek.provider import Provider

async def create_brain(api_key: str):
    """Inicializa o provedor DeepSeek e retorna seus modelos."""
    provider_instance = Provider(api_key)
    models = await provider_instance.list_models()
    return models
