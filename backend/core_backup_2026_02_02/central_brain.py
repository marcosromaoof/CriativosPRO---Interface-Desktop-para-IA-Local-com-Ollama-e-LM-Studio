import os
import importlib
import asyncio
from core.config import config

class CentralBrain:
    """Gerente de inteligência e descoberta dinâmica de modelos."""
    
    def __init__(self, providers_dir="backend/core/providers"):
        self.providers_dir = providers_dir
        self.available_models = {} # {provider_name: [model_list]}

    async def scan_providers(self):
        """ Percorre a pasta de provedores e descobre modelos disponíveis. """
        print("[CentralBrain] Iniciando varredura dinâmica de provedores...")
        
        # Lista diretórios em core/providers, ignorando arquivos e a base
        providers = [d for d in os.listdir("backend/core/providers") 
                    if os.path.isdir(os.path.join("backend/core/providers", d)) 
                    and d != "__pycache__" and d != "base"]

        for provider in providers:
            try:
                # Importa o brain do provedor dinamicamente
                module_path = f"core.providers.{provider}.brain"
                brain_module = importlib.import_module(module_path)
                
                # Executa a função de criação do cérebro específica do provedor
                if hasattr(brain_module, "create_brain"):
                    # Provedores locais não precisam de chave real
                    is_local = provider in ["ollama", "lmstudio"]
                    api_key = config.get_api_key(provider)
                    
                    if api_key or is_local:
                        models = await brain_module.create_brain(api_key or "local")
                        
                        # Sincronizar modelos no banco (adiciona novos, mantém status dos existentes)
                        from core.database import db
                        db.sync_models(provider, models)
                        
                        # Filtrar apenas modelos ativos
                        active_models = db.get_active_models(provider)
                        active_model_names = [m['model_name'] for m in active_models]
                        
                        self.available_models[provider] = active_model_names
                        print(f"[CentralBrain] Provedor '{provider}' carregado com {len(active_model_names)} modelos ativos.")
                    else:
                        print(f"[CentralBrain] Provedor '{provider}' aguardando configuração de chave.")
                
            except Exception as e:
                print(f"[CentralBrain] Erro ao escanear provedor '{provider}': {e}")

        return self.available_models

    def get_all_models(self):
        """Retorna a lista completa de modelos ativos consolidados."""
        return self.available_models

# Instância global
central_brain = CentralBrain()
