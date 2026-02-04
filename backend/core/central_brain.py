import os
import importlib
import asyncio
from core.config import config

class CentralBrain:
    """Gerente de inteligência e descoberta dinâmica de modelos."""
    
    def __init__(self):
        # Resolve o caminho absoluto de core/providers
        # Funciona tanto em Dev (filesystem) quanto Frozen (PyInstaller _MEIPASS)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.providers_dir = os.path.join(base_dir, "providers")
        self.available_models = {} 

    async def scan_providers(self):
        """ Percorre a pasta de provedores e descobre modelos disponíveis. """
        print(f"[CentralBrain] Iniciando varredura em: {self.providers_dir}")
        
        if not os.path.exists(self.providers_dir):
            print(f"[CentralBrain] ERRO: Diretório de provedores não encontrado: {self.providers_dir}")
            return {}

        try:
            # Lista diretórios
            providers = [d for d in os.listdir(self.providers_dir) 
                        if os.path.isdir(os.path.join(self.providers_dir, d)) 
                        and d != "__pycache__" and d != "base"]
        except Exception as e:
            print(f"[CentralBrain] Erro ao listar diretórios: {e}")
            return {}

        for provider in providers:
            try:
                print(f"[CentralBrain] Escaneando provedor: {provider}")
                
                # Importa o brain do provedor dinamicamente
                module_path = f"core.providers.{provider}.brain"
                brain_module = importlib.import_module(module_path)
                
                # Executa a função de criação do cérebro específica do provedor
                if hasattr(brain_module, "create_brain"):
                    # Provedores locais não precisam de chave real
                    is_local = provider in ["ollama", "lmstudio"]
                    api_key = config.get_api_key(provider)
                    
                    if api_key or is_local:
                        try:
                            models = await brain_module.create_brain(api_key or "local")
                            
                            if models is None:
                                print(f"[CentralBrain] AVISO: {provider} retornou None para modelos.")
                                models = []
                                
                            # Sincronizar modelos no banco (adiciona novos, mantém status dos existentes)
                            from core.database import db
                            db.sync_models(provider, models)
                            
                            # Filtrar apenas modelos ativos
                            active_models = db.get_active_models(provider)
                            active_model_names = [m['model_name'] for m in active_models]
                            
                            self.available_models[provider] = active_model_names
                            print(f"[CentralBrain] Provedor '{provider}' carregado com {len(active_model_names)} modelos ativos.")
                        except AttributeError as ae:
                             print(f"[CentralBrain] Erro de Atributo em '{provider}': {ae}")
                             # Isso captura o famigerado NoneType has no attribute...
                        except Exception as inner_e:
                             print(f"[CentralBrain] Erro interno ao carregar '{provider}': {inner_e}")
                             import traceback
                             traceback.print_exc()

                    else:
                        print(f"[CentralBrain] Provedor '{provider}' aguardando configuração de chave.")
                
            except Exception as e:
                print(f"[CentralBrain] Erro GERAL ao escanear provedor '{provider}': {e}")
                import traceback
                traceback.print_exc()

        return self.available_models

    def get_all_models(self):
        """Retorna a lista completa de modelos ativos consolidados."""
        return self.available_models

# Instância global
central_brain = CentralBrain()
