from core.providers.openrouter.provider import Provider

async def create_brain(api_key: str):
    """
    Função chamada pelo CentralBrain para inicializar o provedor 
    e descobrir os modelos disponíveis.
    """
    provider_instance = Provider(api_key)
    models = await provider_instance.list_models()
    
    # Podemos filtrar modelos indesejados aqui se necessário
    # Por exemplo, retornar apenas os 20 primeiros mais populares
    return models[:20] if models else []
