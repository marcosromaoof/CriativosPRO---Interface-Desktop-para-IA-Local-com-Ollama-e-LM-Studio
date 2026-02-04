import asyncio
from core.config import config
from core.database import db
from core.constants import SUPPORTED_PROVIDERS
from core.logger import root_logger as logger

class CentralBrain:
    """Gerente de inteligência para provedores locais de IA."""
    
    def __init__(self):
        self.available_models = {}

    async def scan_providers(self):
        """Escaneia os provedores locais (Ollama e LM Studio) e descobre modelos disponíveis."""
        self.available_models = {}
        logger.info("Iniciando varredura de provedores locais...")
        
        for provider in SUPPORTED_PROVIDERS:
            try:
                logger.info(f"Escaneando provedor: {provider}")
                
                # Importa o brain do provedor
                if provider == "ollama":
                    from core.providers.ollama.brain import create_brain
                elif provider == "lmstudio":
                    from core.providers.lmstudio.brain import create_brain
                else:
                    continue
                
                # Provedores locais não precisam de chave real
                api_key = config.get_api_key(provider) or "local"
                
                try:
                    models = await create_brain(api_key)
                    
                    if models is None:
                        logger.warning(f"{provider} retornou None para modelos.")
                        models = []
                    
                    # Sincronizar modelos no banco
                    db.sync_models(provider, models)
                    
                    # Filtrar apenas modelos ativos
                    active_models = db.get_active_models(provider)
                    active_model_names = [m['model_name'] for m in active_models]
                    
                    self.available_models[provider] = active_model_names
                    logger.info(f"Provedor '{provider}' carregado com {len(active_model_names)} modelos ativos.")
                    
                except Exception as inner_e:
                    logger.error(f"Erro ao carregar '{provider}': {inner_e}")
                    import traceback
                    traceback.print_exc()
                
            except Exception as e:
                logger.error(f"Erro ao escanear provedor '{provider}': {e}")
                import traceback
                traceback.print_exc()

        return self.available_models

    def get_all_models(self):
        """Retorna a lista completa de modelos ativos consolidados."""
        return self.available_models

# Instância global
central_brain = CentralBrain()
