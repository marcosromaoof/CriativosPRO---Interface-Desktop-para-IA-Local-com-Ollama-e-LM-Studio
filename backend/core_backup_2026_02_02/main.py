import socketio
from aiohttp import web
from core.controller import Controller
from core.fsm import fsm
from core.central_brain import central_brain
import asyncio
import os

from core.config import config

# 1. Configuração do Socket.IO
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# 2. Garantir diretório de áudio e servir como estático
AUDIO_DIR = os.path.join(os.getcwd(), "backend", "temp_audio")
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Serve a pasta /audio para o frontend acessar os .wav
app.router.add_static('/audio/', path=AUDIO_DIR, name='audio')

# 3. Instanciar Controller
controller = Controller(sio)

# --- Eventos do Socket ---

@sio.event
async def connect(sid, environ):
    print(f"[Socket] Cliente conectado: {sid}")
    
    # 1. Enviar status e modelos
    await sio.emit("system_status", {"status": fsm.current_state.value}, to=sid)
    await sio.emit("models_data", {"providers": central_brain.get_all_models()}, to=sid)
    
    # 2. Enviar chaves de API salvas (ofuscadas para segurança)
    saved_keys = {
        "openrouter": config.get_api_key("openrouter") or "",
        "deepseek": config.get_api_key("deepseek") or "",
        "groq": config.get_api_key("groq") or ""
    }
    await sio.emit("load_api_keys", saved_keys, to=sid)

@sio.event
async def disconnect(sid):
    print(f"[Socket] Cliente desconectado: {sid}")

@sio.event
async def save_api_keys(sid, data):
    """Persiste as chaves de API no banco de dados."""
    for provider, key in data.items():
        if key:
            config.set_api_key(provider, key)
    
    # Após salvar as chaves, re-escanear modelos se necessário
    await central_brain.scan_providers()
    await sio.emit("models_data", {"providers": central_brain.get_all_models()}, to=sid)
    await sio.emit("keys_saved", {"status": "success"}, to=sid)

@sio.event
async def get_sessions(sid, data=None):
    """Retorna a lista de todas as sessões de chat."""
    from core.history_manager import history_manager
    sessions = history_manager.get_all_sessions()
    await sio.emit("sessions_list", {"sessions": sessions}, to=sid)

@sio.event
async def delete_session(sid, data):
    """Exclui uma sessão específica."""
    session_id = data.get('session_id')
    if session_id:
        from core.history_manager import history_manager
        history_manager.clear_session(session_id)
        # Retorna lista atualizada
        sessions = history_manager.get_all_sessions()
        await sio.emit("sessions_list", {"sessions": sessions}, to=sid)

@sio.event
async def load_session(sid, data):
    """Carrega o histórico de uma sessão."""
    session_id = data.get('session_id')
    if session_id:
        from core.history_manager import history_manager
        messages = history_manager.get_full_history(session_id)
        await sio.emit("session_loaded", {
            "session_id": session_id,
            "messages": messages
        }, to=sid)

@sio.event
async def send_message(sid, data):
    await controller.handle_message(sid, data)

@sio.event
async def stop_generation(sid, data):
    await controller.stop_generation(sid)

@sio.event
async def get_models(sid, data=None):
    models = await central_brain.scan_providers()
    await sio.emit("models_data", {"providers": models}, to=sid)

# --- Mudança de Estado ---
@sio.event
async def sync_provider_models(sid, data):
    """Sincroniza modelos de um provedor específico via API."""
    provider_name = data.get('provider')
    if not provider_name:
        await sio.emit("sync_error", {"message": "Provedor não especificado"}, to=sid)
        return
    
    try:
        # Buscar modelos do provedor
        from core.providers.provider_manager import provider_manager
        
        # Provedores locais não precisam de API Key
        is_local = provider_name.lower() in ['ollama', 'lmstudio']
        api_key = config.get_api_key(provider_name) or "none"
        
        if not is_local and api_key == "none":
            await sio.emit("sync_error", {"message": f"API Key não configurada para {provider_name}"}, to=sid)
            return
        
        provider = provider_manager.get_provider(provider_name, api_key, force_reload=True)
        models = await provider.list_models()
        
        if not models:
            await sio.emit("sync_error", {"message": f"Nenhum modelo encontrado para {provider_name}. Verifique se o servidor está rodando."}, to=sid)
            return
        
        # Sincronizar no banco
        config.sync_models(provider_name, models)
        
        # Retornar modelos atualizados
        all_models = config.get_all_models(provider_name)
        await sio.emit("models_synced", {"provider": provider_name, "models": all_models}, to=sid)
    except Exception as e:
        print(f"[Error] sync_provider_models: {e}")
        await sio.emit("sync_error", {"message": str(e)}, to=sid)

@sio.event
async def toggle_model(sid, data):
    """Ativa ou desativa um modelo específico."""
    provider = data.get('provider')
    model_name = data.get('model_name')
    is_active = data.get('is_active', True)
    
    config.toggle_model(provider, model_name, is_active)
    await sio.emit("model_toggled", {"success": True}, to=sid)
    
    # Re-escanear modelos ativos
    await central_brain.scan_providers()
    await sio.emit("models_data", {"providers": central_brain.get_all_models()}, to=sid)

@sio.event
async def toggle_provider(sid, data):
    """Ativa ou desativa todos os modelos de um provedor."""
    provider = data.get('provider')
    is_active = data.get('is_active', True)
    
    config.toggle_provider(provider, is_active)
    await sio.emit("provider_toggled", {"success": True}, to=sid)
    
    # Re-escanear modelos ativos
    await central_brain.scan_providers()
    await sio.emit("models_data", {"providers": central_brain.get_all_models()}, to=sid)

@sio.event
async def get_all_models_config(sid, data):
    """Retorna todos os modelos (ativos e inativos) para configuração."""
    provider = data.get('provider')
    models = config.get_all_models(provider)
    await sio.emit("all_models_config", {"models": models}, to=sid)

@sio.event
async def save_system_prompts(sid, data):
    """Salva os 3 prompts de sistema."""
    try:
        prompts = data.get('prompts', {})
        print(f"[Settings] Salvando prompts: {list(prompts.keys())}")
        for prompt_type, content in prompts.items():
            config.save_prompt(prompt_type, content)
        print("[Settings] Prompts salvos com sucesso")
        await sio.emit("prompts_saved", {"success": True}, to=sid)
    except Exception as e:
        print(f"[Error] save_system_prompts: {e}")
        import traceback
        traceback.print_exc()
        await sio.emit("settings_error", {"message": f"Erro ao salvar prompts: {str(e)}"}, to=sid)

@sio.event
async def load_system_prompts(sid, data):
    """Carrega todos os prompts de sistema."""
    prompts = config.get_all_prompts()
    await sio.emit("prompts_loaded", {"prompts": prompts}, to=sid)

@sio.event
async def save_user_profile(sid, data):
    """Salva o perfil do usuário."""
    try:
        profile = data.get('profile', {})
        print(f"[Settings] Salvando perfil: {profile}")
        config.save_user_profile(profile)
        print("[Settings] Perfil salvo com sucesso")
        await sio.emit("profile_saved", {"success": True}, to=sid)
    except Exception as e:
        print(f"[Error] save_user_profile: {e}")
        import traceback
        traceback.print_exc()
        await sio.emit("settings_error", {"message": f"Erro ao salvar perfil: {str(e)}"}, to=sid)

@sio.event
async def load_user_profile(sid, data):
    """Carrega o perfil do usuário."""
    try:
        profile = config.get_user_profile()
        print(f"[Settings] Perfil carregado: {profile}")
        await sio.emit("profile_loaded", {"profile": profile}, to=sid)
    except Exception as e:
        print(f"[Error] load_user_profile: {e}")
        await sio.emit("profile_loaded", {"profile": {}}, to=sid)

@sio.event
async def save_provider_settings(sid, data):
    """Salva configurações de um provedor (API Key, Base URL)."""
    try:
        provider = data.get('provider')
        settings = data.get('settings', {})
        
        if 'api_key' in settings:
            config.set_api_key(provider, settings['api_key'])
            
        if 'base_url' in settings:
            # Salva base_url como uma configuração padrão
            from core.database import db
            db.set_setting(f"base_url_{provider}", settings['base_url'])
            
        # Re-escanear para aplicar mudanças (ex: nova URL pode trazer novos modelos)
        await central_brain.scan_providers()
        await sio.emit("settings_saved", {"provider": provider}, to=sid)
    except Exception as e:
        print(f"[Error] save_provider_settings: {e}")
        await sio.emit("settings_error", {"message": str(e)}, to=sid)

@sio.event
async def load_provider_settings(sid, data):
    """Carrega configurações de um provedor."""
    provider = data.get('provider')
    from core.database import db
    
    settings = {
        "api_key": config.get_api_key(provider) or "",
        "base_url": db.get_setting(f"base_url_{provider}") or ""
    }
    
    # Defaults para locais se não existirem
    if not settings['base_url']:
        if provider == 'ollama': settings['base_url'] = "http://localhost:11434/v1"
        if provider == 'lmstudio': settings['base_url'] = "http://localhost:1234/v1"
        
    await sio.emit("provider_settings_loaded", {"provider": provider, "settings": settings}, to=sid)

@sio.event
async def get_dashboard_data(sid, data):
    """Retorna dados de métricas para o dashboard."""
    from core.database import db
    stats = db.get_dashboard_stats()
    await sio.emit("dashboard_data", stats, to=sid)

@sio.event
async def generate_tts(sid, data):
    """Gera áudio para o texto solicitado usando Piper TTS."""
    text = data.get('text')
    text_id = data.get('id')
    
    if not text: 
        return
    
    # Importar serviço TTS aqui
    from core.tts_service import tts_service
    
    # Executar serviço (o método speak já faz o clean e gera arquivo)
    filename = await tts_service.speak(text)
    
    if filename:
        # Retorna a URL para o frontend
        audio_url = f"http://127.0.0.1:5000/audio/{filename}"
        await sio.emit("tts_ready", {"url": audio_url, "text_id": text_id}, to=sid)
    else:
        # Notificar erro
        await sio.emit("tts_error", {"message": "Falha na síntese de voz", "text_id": text_id}, to=sid)

# --- Mudança de Estado ---

def on_fsm_change(new_state):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(sio.emit("system_status", {"status": new_state}), loop)
    except Exception:
        pass

fsm.set_on_change(on_fsm_change)

if __name__ == '__main__':
    print("==========================================")
    print("    CRIATIVOSPRO BACKEND - INICIADO      ")
    print("==========================================")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(central_brain.scan_providers())
    
    web.run_app(app, host='127.0.0.1', port=5000)
