from core.database import db

class Config:
    """Gerenciador central de configurações e estados do sistema."""
    
    @staticmethod
    def get_api_key(provider):
        return db.get_setting(f"api_key_{provider}")

    @staticmethod
    def set_api_key(provider, key):
        db.set_setting(f"api_key_{provider}", key, encrypt=True)

    @staticmethod
    def get_theme():
        return db.get_setting("theme", "night-blue")

    @staticmethod
    def is_first_run():
        return db.get_setting("first_run", "true") == "true"

    @staticmethod
    def complete_first_run():
        db.set_setting("first_run", "false")

    # Estados dinâmicos (não persistentes obrigatoriamente aqui, ou via DB)
    @staticmethod
    def get_active_model():
        return db.get_setting("active_model", "gpt-3.5-turbo") # Default inicial

    @staticmethod
    def set_active_model(model_id):
        db.set_setting("active_model", model_id)
    
    # === Delegação para Gerenciamento de Modelos (Fase 2) ===
    
    @staticmethod
    def sync_models(provider, models_list):
        return db.sync_models(provider, models_list)
    
    @staticmethod
    def get_active_models(provider=None):
        return db.get_active_models(provider)
    
    @staticmethod
    def get_all_models(provider=None):
        return db.get_all_models(provider)
    
    @staticmethod
    def toggle_model(provider, model_name, is_active):
        return db.toggle_model(provider, model_name, is_active)
    
    @staticmethod
    def toggle_provider(provider, is_active):
        return db.toggle_provider(provider, is_active)
    
    # === Delegação para Gerenciamento de Prompts (Fase 2) ===
    
    @staticmethod
    def get_prompt(prompt_type):
        return db.get_prompt(prompt_type)
    
    @staticmethod
    def save_prompt(prompt_type, content):
        return db.save_prompt(prompt_type, content)
    
    @staticmethod
    def get_all_prompts():
        return db.get_all_prompts()
    
    # === Delegação para Gerenciamento de Perfil (Fase 2) ===
    
    @staticmethod
    def get_user_profile():
        return db.get_user_profile()
    
    @staticmethod
    def save_user_profile(profile_data):
        return db.save_user_profile(profile_data)

config = Config()
